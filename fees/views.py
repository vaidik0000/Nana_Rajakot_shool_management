from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import authenticate, login

from .models import FeeTransaction
from students.models import Student
from fees import logger
from fees.utils.logging import (
    log_payment_attempt,
    log_payment_success,
    log_payment_error,
    log_webhook_event
)
from .utils.receipts import send_receipt_email

import razorpay
import json
import traceback
import logging

logger = logging.getLogger('fees')

# Initialize Razorpay client with settings from settings.py
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

# Remove this log statement to prevent terminal output
# logger.info(f"Using Razorpay Key ID: {settings.RAZORPAY_KEY_ID}")

@login_required
def fee_payment_list(request):
    # For students, show only their transactions
    if hasattr(request, 'user_type') and request.user_type == 'student':
        student = request.student
        transactions = FeeTransaction.objects.filter(student=student).order_by('-created_at')
    else:
        # For teachers and admins, show all transactions
        transactions = FeeTransaction.objects.all().order_by('-created_at')
    
    return render(request, 'fees/transaction_list.html', {'transactions': transactions})

@login_required
def initiate_payment(request, student_id=None):
    # First try to identify the student
    try:
        user_id = request.user.id if request.user.is_authenticated else None
        
        if student_id:
            # If student_id is provided, fetch that specific student
            student = get_object_or_404(Student, id=student_id)
        elif hasattr(request, 'user_type') and request.user_type == 'student':
            # If logged in as student, use the student associated with the user
            student = request.student
            logger.info(f"Student detected: {student.first_name} {student.last_name} (ID: {student.id})")
        else:
            # Not a student and no student ID provided
            messages.error(request, 'Student identification failed')
            return redirect('fees:fee_payment_list')
    except Exception as e:
        log_payment_error(
            error_type='student_identification',
            error_message=str(e), 
            additional_data={
                'student_id': student_id,
                'user_id': user_id,
                'user_type': getattr(request, 'user_type', None)
            }
        )
        messages.error(request, 'Error identifying student')
        return redirect('fees:fee_payment_list')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if not amount:
            messages.error(request, 'Please enter a valid amount')
            return redirect('fees:initiate_payment', student_id=student.id)
        
        try:
            # Convert to float and validate amount
            amount = float(amount)
            if amount <= 0:
                messages.error(request, 'Amount must be greater than zero')
                return redirect('fees:initiate_payment', student_id=student.id)
                
            # Log payment attempt
            log_payment_attempt(
                student_id=student.id,
                amount=amount,
                user_id=user_id if user_id != getattr(student, 'user_id', None) else None
            )
                
            # Create a new transaction
            transaction = FeeTransaction.objects.create(
                student=student,
                amount=amount,
                status='pending',
                description=f"Fee payment for {student.first_name} {student.last_name}"
            )
            
            # Convert amount to paise (Razorpay accepts amount in smallest currency unit)
            amount_in_paise = int(float(amount) * 100)
            
            # Create Razorpay order with automatic capture
            razorpay_order = razorpay_client.order.create({
                'amount': amount_in_paise,
                'currency': settings.RAZORPAY_CURRENCY,
                'receipt': f'receipt_{transaction.id}',
                'payment_capture': '1'  # Auto capture
            })
            
            logger.info(f"Razorpay order created: {razorpay_order['id']} for student {student.id}")
            logger.debug(f"Order details: {razorpay_order}")
            
            # Update transaction with order ID
            transaction.transaction_id = razorpay_order['id']
            transaction.save()
            
            # Build the absolute callback URL - use reverse() to avoid hardcoding
            callback_url = request.build_absolute_uri(reverse('fees:payment_callback'))
            
            # Prepare context for the payment page
            context = {
                'student': student,
                'transaction': transaction,
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'amount': amount,
                'amount_in_paise': amount_in_paise,
                'order_id': razorpay_order['id'],
                'callback_url': callback_url
            }
            
            return render(request, 'fees/payment.html', context)
        except Exception as e:
            log_payment_error(
                error_type='payment_initiation',
                error_message=str(e),
                transaction_id=getattr(transaction, 'id', None) if 'transaction' in locals() else None,
                additional_data={
                    'student_id': student.id,
                    'amount': amount if 'amount' in locals() else None,
                    'user_id': user_id
                }
            )
            messages.error(request, f'Error initiating payment: {str(e)}')
            return redirect('fees:fee_payment_list')
    
    return render(request, 'fees/initiate_payment.html', {'student': student})

@csrf_exempt
def payment_callback(request):
    """Handle payment callback from Razorpay JS checkout"""
    if request.method == 'POST':
        try:
            # Log request data for debugging
            logger.info("Payment callback received")
            logger.debug(f"POST data: {request.POST}")
            
            # Get the payment details from POST request
            razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            razorpay_signature = request.POST.get('razorpay_signature', '')
            
            # For debugging
            logger.info(f"Payment callback: payment_id={razorpay_payment_id}, order_id={razorpay_order_id}")
            
            # Validate that we have the required parameters
            if not (razorpay_payment_id and razorpay_order_id and razorpay_signature):
                log_payment_error(
                    error_type='missing_parameters',
                    error_message="Missing required parameters in callback",
                    additional_data={
                        'payment_id': razorpay_payment_id,
                        'order_id': razorpay_order_id,
                        'has_signature': bool(razorpay_signature)
                    }
                )
                return redirect('fees:payment_failure')
            
            # Verify payment signature
            params_dict = {
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_order_id': razorpay_order_id,
                'razorpay_signature': razorpay_signature
            }
            
            try:
                # Verify the payment signature
                result = razorpay_client.utility.verify_payment_signature(params_dict)
                logger.info(f"Signature verification result: {result}")
                
                # Find the transaction by order ID
                try:
                    transaction = FeeTransaction.objects.get(transaction_id=razorpay_order_id)
                except FeeTransaction.DoesNotExist:
                    logger.error(f"Transaction with order ID {razorpay_order_id} not found")
                    # Attempt to fetch payment details from Razorpay directly
                    try:
                        payment = razorpay_client.payment.fetch(razorpay_payment_id)
                        order_id = payment.get('order_id')
                        logger.debug(f"Retrieved payment info from Razorpay: {payment}")
                        transaction = FeeTransaction.objects.get(transaction_id=order_id)
                    except Exception as e:
                        log_payment_error(
                            error_type='transaction_not_found',
                            error_message=str(e),
                            additional_data={
                                'payment_id': razorpay_payment_id,
                                'order_id': razorpay_order_id
                            }
                        )
                        messages.error(request, 'Transaction not found')
                        return redirect('fees:payment_failure')
                
                # Update transaction
                transaction.status = 'completed'
                transaction.save()
                
                # Update student fee status
                student = transaction.student
                student.fee_status = 'paid'
                student.last_payment_date = timezone.now().date()
                student.transaction_id = razorpay_payment_id
                student.save()
                
                # Log successful payment
                log_payment_success(
                    transaction_id=transaction.id,
                    payment_id=razorpay_payment_id,
                    order_id=razorpay_order_id,
                    amount=transaction.amount
                )
                
                messages.success(request, 'Payment successful!')
                return redirect('fees:payment_success', transaction_id=transaction.id)
            
            except razorpay.errors.SignatureVerificationError as e:
                # Payment verification failed
                log_payment_error(
                    error_type='signature_verification',
                    error_message=str(e),
                    additional_data={
                        'payment_id': razorpay_payment_id,
                        'order_id': razorpay_order_id
                    }
                )
                messages.error(request, 'Payment verification failed. Please contact support.')
                return redirect('fees:payment_failure')
            
        except Exception as e:
            # Log the error for debugging
            log_payment_error(
                error_type='payment_callback',
                error_message=str(e),
                additional_data={
                    'payment_id': razorpay_payment_id if 'razorpay_payment_id' in locals() else None,
                    'order_id': razorpay_order_id if 'razorpay_order_id' in locals() else None
                }
            )
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('fees:payment_failure')
    
    return HttpResponse('Invalid request', status=400)

@csrf_exempt
def webhook_handler(request):
    """
    Webhook handler for direct server notifications from Razorpay
    This provides a more reliable way to capture payment status
    """
    if request.method == 'POST':
        try:
            # Get the webhook data
            data = json.loads(request.body)
            
            # Extract key information for logging
            event_type = data.get('event', 'unknown')
            event_id = data.get('id', 'no_id')
            
            # Log webhook event
            log_webhook_event(
                event_type=event_type,
                event_id=event_id,
                raw_data=data
            )
            
            # Verify webhook signature
            webhook_signature = request.headers.get('X-Razorpay-Signature', '')
            
            if not webhook_signature:
                logger.error("Missing webhook signature")
                return HttpResponse('Missing signature', status=400)
            
            # Verify signature using the webhook secret from settings
            try:
                razorpay_client.utility.verify_webhook_signature(
                    request.body.decode(), 
                    webhook_signature, 
                    settings.RAZORPAY_WEBHOOK_SECRET
                )
                logger.info("Webhook signature verified successfully")
            except Exception as e:
                log_payment_error(
                    error_type='webhook_signature_verification',
                    error_message=str(e),
                    additional_data={
                        'event_type': event_type,
                        'event_id': event_id
                    }
                )
                return HttpResponse('Invalid signature', status=400)
            
            # Process payment event
            logger.info(f"Processing webhook event: {event_type}")
            
            if event_type == 'payment.authorized' or event_type == 'payment.captured':
                payment_entity = data.get('payload', {}).get('payment', {}).get('entity', {})
                order_id = payment_entity.get('order_id')
                payment_id = payment_entity.get('id')
                status = payment_entity.get('status')
                
                # Update log with more payment details
                log_webhook_event(
                    event_type=event_type,
                    event_id=event_id,
                    order_id=order_id,
                    status=status
                )
                
                if status == 'captured' and order_id:
                    try:
                        # Update transaction
                        transaction = FeeTransaction.objects.get(transaction_id=order_id)
                        if transaction.status != 'completed':
                            transaction.status = 'completed'
                            transaction.save()
                            
                            # Update student fee status
                            student = transaction.student
                            student.fee_status = 'paid'
                            student.last_payment_date = timezone.now().date()
                            student.transaction_id = payment_id
                            student.save()
                            
                            # Log successful payment
                            log_payment_success(
                                transaction_id=transaction.id,
                                payment_id=payment_id,
                                order_id=order_id,
                                amount=transaction.amount
                            )
                            
                            # Generate and send payment receipt via email
                            try:
                                success, message = send_receipt_email(transaction.id)
                                if success:
                                    logger.info(f"Webhook: Payment receipt sent for transaction {transaction.id}: {message}")
                                else:
                                    logger.warning(f"Webhook: Could not send receipt for transaction {transaction.id}: {message}")
                            except Exception as e:
                                # Just log the error, don't interrupt webhook processing
                                log_payment_error(
                                    error_type='webhook_receipt_sending',
                                    error_message=str(e),
                                    transaction_id=transaction.id
                                )
                                logger.error(f"Failed to send receipt in webhook: {str(e)}")
                            
                            # Return a success response
                            response_data = {
                                'status': 'success',
                                'message': 'Payment successfully processed',
                                'transaction_id': transaction.id
                            }
                        else:
                            logger.info(f"Transaction {transaction.id} already completed")
                    except FeeTransaction.DoesNotExist:
                        log_payment_error(
                            error_type='webhook_transaction_not_found',
                            error_message=f"Transaction with order ID {order_id} not found",
                            additional_data={
                                'event_type': event_type,
                                'event_id': event_id,
                                'order_id': order_id,
                                'payment_id': payment_id
                            }
                        )
            
            return HttpResponse('Webhook received', status=200)
            
        except Exception as e:
            log_payment_error(
                error_type='webhook_processing',
                error_message=str(e),
                additional_data={
                    'headers': dict(request.headers.items())
                }
            )
            return HttpResponse('Error processing webhook', status=500)
    
    return HttpResponse('Invalid request', status=400)

@login_required
def payment_success(request, transaction_id):
    transaction = get_object_or_404(FeeTransaction, id=transaction_id)
    
    # Try to send payment receipt
    try:
        success, message = send_receipt_email(transaction_id)
        if success:
            messages.success(request, f"Payment receipt has been sent to your email.")
        else:
            messages.warning(request, f"Payment successful, but receipt could not be sent: {message}")
    except Exception as e:
        log_payment_error(
            error_type='receipt_email_view',
            error_message=str(e),
            transaction_id=transaction.id
        )
        messages.warning(request, "Payment successful, but we encountered an error sending the receipt. Please contact administration.")
    
    return render(request, 'fees/payment_success.html', {'transaction': transaction})

@login_required
def payment_failure(request):
    logger.info("Displaying payment failure page")
    return render(request, 'fees/payment_failure.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        logger.debug(f"Attempting login for username: {username}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('core:home')
        else:
            messages.error(request, 'Invalid username or password.')
            logger.error(f"Login failed for username: {username}")
