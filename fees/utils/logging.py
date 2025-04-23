"""
Specialized logging utilities for the fees module
"""
import logging
import json
import traceback
from datetime import datetime

# Get the fees logger
logger = logging.getLogger('fees')

def log_payment_attempt(student_id, amount, user_id=None):
    """
    Log a payment attempt with detailed information
    
    Args:
        student_id: ID of the student making payment
        amount: Payment amount
        user_id: ID of the user initiating the payment (if different from student)
    """
    logger.info(
        f"Payment attempt initiated | Student ID: {student_id} | "
        f"Amount: {amount} | User ID: {user_id or 'Same as student'}"
    )

def log_payment_success(transaction_id, payment_id, order_id, amount):
    """
    Log a successful payment with all transaction details
    
    Args:
        transaction_id: Internal transaction ID
        payment_id: Payment gateway payment ID
        order_id: Payment gateway order ID
        amount: Payment amount
    """
    logger.info(
        f"Payment successful | Transaction ID: {transaction_id} | "
        f"Payment ID: {payment_id} | Order ID: {order_id} | Amount: {amount}"
    )

def log_payment_error(error_type, error_message, transaction_id=None, additional_data=None):
    """
    Log a payment error with detailed information and traceback
    
    Args:
        error_type: Type of error (e.g., 'verification', 'gateway', 'database')
        error_message: Error message
        transaction_id: Related transaction ID if available
        additional_data: Any additional data to log
    """
    # Format the error data
    error_data = {
        'error_type': error_type,
        'error_message': error_message,
        'timestamp': datetime.now().isoformat(),
        'transaction_id': transaction_id,
    }
    
    if additional_data:
        error_data['additional_data'] = additional_data
    
    # Get the current traceback
    error_data['traceback'] = traceback.format_exc()
    
    # Log as JSON for better parsing
    logger.error(f"Payment error: {json.dumps(error_data, indent=2)}")

def log_webhook_event(event_type, event_id, order_id=None, status=None, raw_data=None):
    """
    Log webhook events from payment gateway
    
    Args:
        event_type: Type of webhook event
        event_id: Unique ID of the webhook event
        order_id: Related order ID if available
        status: Status of the event
        raw_data: Raw webhook data (will be logged at debug level only)
    """
    logger.info(
        f"Webhook event received | Type: {event_type} | "
        f"Event ID: {event_id} | Order ID: {order_id or 'N/A'} | "
        f"Status: {status or 'N/A'}"
    )
    
    if raw_data:
        # Log raw data at debug level to avoid cluttering normal logs
        logger.debug(f"Webhook raw data: {json.dumps(raw_data, indent=2)}") 