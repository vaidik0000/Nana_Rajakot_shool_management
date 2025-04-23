"""
Management command to check payment status between Razorpay and local database
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from fees.models import FeeTransaction
from fees.utils.logging import logger, log_payment_error
import razorpay
import json
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Check payment status between Razorpay and local database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to look back for payments',
        )
        
        parser.add_argument(
            '--amount',
            type=float,
            help='Filter payments by specific amount',
        )
        
        parser.add_argument(
            '--payment-id',
            type=str,
            help='Check a specific payment by ID',
        )

    def handle(self, *args, **options):
        days = options['days']
        amount = options['amount']
        payment_id = options['payment_id']
        
        self.stdout.write(self.style.SUCCESS(f"Starting payment status check..."))
        
        # Initialize Razorpay client
        try:
            razorpay_client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            self.stdout.write(f"Connected to Razorpay with key ID: {settings.RAZORPAY_KEY_ID}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to initialize Razorpay client: {str(e)}"))
            return
            
        # Process local transactions
        self.check_local_transactions(razorpay_client, amount, payment_id)
        
        # Process Razorpay dashboard
        self.check_razorpay_dashboard(razorpay_client, days, amount, payment_id)
        
        self.stdout.write(self.style.SUCCESS("Payment status check completed."))

    def check_local_transactions(self, razorpay_client, amount=None, payment_id=None):
        """Check transactions in local database"""
        self.stdout.write(self.style.NOTICE("\nChecking local transactions:"))
        
        # Build query
        transactions = FeeTransaction.objects.all().order_by('-created_at')
        
        if amount:
            # Find transactions with the specified amount
            self.stdout.write(f"Filtering by amount: {amount}")
            transactions = transactions.filter(amount=amount)
        
        if payment_id:
            # Find transaction with the specified Razorpay ID
            self.stdout.write(f"Filtering by payment ID: {payment_id}")
            transactions = transactions.filter(transaction_id=payment_id)
        
        # Limit to 10 transactions unless specific filters are applied
        if not amount and not payment_id:
            transactions = transactions[:10]
        
        if not transactions:
            self.stdout.write("No matching transactions found in local database.")
            return
        
        self.stdout.write(self.style.SUCCESS(f"Found {transactions.count()} matching transactions in local database."))
        
        for t in transactions:
            self.stdout.write(f"\nLocal Transaction ID: {t.id}")
            self.stdout.write(f"Student: {t.student.first_name} {t.student.last_name}")
            self.stdout.write(f"Amount: {t.amount}")
            self.stdout.write(f"Status: {t.status}")
            self.stdout.write(f"Razorpay ID: {t.transaction_id}")
            self.stdout.write(f"Created at: {t.created_at}")
            
            # Check transaction in Razorpay if we have a transaction ID
            if t.transaction_id:
                self.verify_transaction_in_razorpay(razorpay_client, t.transaction_id, float(t.amount))
            else:
                self.stdout.write(self.style.WARNING("No Razorpay transaction ID available."))
    
    def check_razorpay_dashboard(self, razorpay_client, days=7, amount=None, payment_id=None):
        """Check payments directly in Razorpay dashboard"""
        self.stdout.write(self.style.NOTICE("\nChecking Razorpay dashboard:"))
        
        # Get start and end dates for filter
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Convert to Unix timestamps as required by Razorpay API
        from_timestamp = int(start_date.timestamp())
        to_timestamp = int(end_date.timestamp())
        
        self.stdout.write(f"Checking payments from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        try:
            # If we have a specific payment ID, fetch just that payment
            if payment_id:
                try:
                    payment = razorpay_client.payment.fetch(payment_id)
                    self.stdout.write(self.style.SUCCESS(f"Found payment with ID {payment_id}"))
                    self.print_payment_details(payment)
                    return
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error fetching payment {payment_id}: {str(e)}"))
            
            # Otherwise get all payments for the period - without date filter first
            payments = razorpay_client.payment.all({'count': 50})
            
            if not payments or 'items' not in payments or not payments['items']:
                self.stdout.write("No payments found in Razorpay dashboard.")
                return
                
            self.stdout.write(self.style.SUCCESS(
                f"Found {len(payments['items'])} payments in Razorpay dashboard."
            ))
            
            matching_payments = []
            
            for payment in payments['items']:
                payment_amount = float(payment.get('amount', 0)) / 100
                
                # If filtering by amount, only show matching payments
                if amount and abs(payment_amount - amount) >= 0.01:
                    continue
                
                matching_payments.append(payment)
                self.print_payment_details(payment)
                
                # Cross-reference with our database
                self.check_payment_in_local_db(payment)
                
            if amount and not matching_payments:
                self.stdout.write(self.style.WARNING(f"No payments with amount {amount} found in Razorpay dashboard."))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching from Razorpay: {str(e)}"))
            logger.error(f"Error fetching from Razorpay dashboard: {str(e)}")
    
    def verify_transaction_in_razorpay(self, razorpay_client, transaction_id, local_amount):
        """Verify if a transaction exists in Razorpay"""
        try:
            # First try to fetch as an order
            razorpay_order = razorpay_client.order.fetch(transaction_id)
            razorpay_amount = float(razorpay_order.get('amount', 0)) / 100
            
            self.stdout.write(self.style.SUCCESS("\nRazorpay Order Found:"))
            self.stdout.write(f"Order ID: {razorpay_order.get('id')}")
            self.stdout.write(f"Order Status: {razorpay_order.get('status')}")
            self.stdout.write(f"Order Amount: {razorpay_amount}")
            
            # Check amounts
            if abs(razorpay_amount - local_amount) >= 0.01:
                self.stdout.write(self.style.WARNING(
                    f"Amount mismatch: Local={local_amount}, Razorpay={razorpay_amount}"
                ))
            
            # Check for associated payments
            try:
                payments = razorpay_client.payment.all({'order_id': transaction_id})
                if payments and 'items' in payments and payments['items']:
                    self.stdout.write(self.style.SUCCESS(f"\nFound {len(payments['items'])} payment(s) for this order:"))
                    
                    for payment in payments['items']:
                        self.stdout.write(f"Payment ID: {payment.get('id')}")
                        self.stdout.write(f"Payment Status: {payment.get('status')}")
                        self.stdout.write(f"Payment Amount: {float(payment.get('amount', 0)) / 100}")
                        self.stdout.write(f"Payment Method: {payment.get('method', 'N/A')}")
                else:
                    self.stdout.write(self.style.WARNING("\nNo payments found for this order in Razorpay."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching payments for order: {str(e)}"))
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"\nNot found as order: {str(e)}"))
            
            # If it's not an order, try to fetch as a payment
            try:
                payment = razorpay_client.payment.fetch(transaction_id)
                payment_amount = float(payment.get('amount', 0)) / 100
                
                self.stdout.write(self.style.SUCCESS("\nRazorpay Payment Found:"))
                self.stdout.write(f"Payment ID: {payment.get('id')}")
                self.stdout.write(f"Payment Status: {payment.get('status')}")
                self.stdout.write(f"Payment Amount: {payment_amount}")
                self.stdout.write(f"Payment Method: {payment.get('method', 'N/A')}")
                
                # Check amounts
                if abs(payment_amount - local_amount) >= 0.01:
                    self.stdout.write(self.style.WARNING(
                        f"Amount mismatch: Local={local_amount}, Razorpay={payment_amount}"
                    ))
                
            except Exception as e2:
                self.stdout.write(self.style.ERROR(f"Not found in Razorpay: {str(e2)}"))
    
    def print_payment_details(self, payment):
        """Print details of a Razorpay payment"""
        self.stdout.write("-" * 80)
        self.stdout.write(f"Payment ID: {payment.get('id')}")
        self.stdout.write(f"Order ID: {payment.get('order_id', 'N/A')}")
        self.stdout.write(f"Amount: {float(payment.get('amount', 0)) / 100} {payment.get('currency', 'INR')}")
        self.stdout.write(f"Status: {payment.get('status')}")
        self.stdout.write(f"Method: {payment.get('method', 'N/A')}")
        
        created_at = payment.get('created_at', 0)
        if created_at:
            created_datetime = datetime.fromtimestamp(created_at)
            self.stdout.write(f"Created At: {created_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def check_payment_in_local_db(self, payment):
        """Check if a Razorpay payment exists in our local database"""
        payment_id = payment.get('id')
        order_id = payment.get('order_id')
        
        # Try to find a transaction with this payment ID or order ID
        transactions = FeeTransaction.objects.filter(transaction_id__in=[payment_id, order_id])
        
        if transactions.exists():
            self.stdout.write(self.style.SUCCESS("Found in local database:"))
            for t in transactions:
                self.stdout.write(f"Local ID: {t.id}")
                self.stdout.write(f"Student: {t.student.first_name} {t.student.last_name}")
                self.stdout.write(f"Local Amount: {t.amount}")
                self.stdout.write(f"Local Status: {t.status}")
        else:
            self.stdout.write(self.style.WARNING("NOT FOUND in local database!")) 