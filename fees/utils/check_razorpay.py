"""
Utility script to directly check the Razorpay dashboard for recent payments
"""
import os
import sys
import django
from datetime import datetime, timedelta
import time

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

# Now import Django modules
from django.conf import settings
from fees.utils.logging import logger
import razorpay
import json

def check_razorpay_dashboard():
    """Check recent payments directly in the Razorpay dashboard"""
    # Initialize Razorpay client
    try:
        razorpay_client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        logger.info(f"Connected to Razorpay with key ID: {settings.RAZORPAY_KEY_ID}")
        
        # Print API key details for verification
        print(f"Using Razorpay Key ID: {settings.RAZORPAY_KEY_ID}")
        print(f"Key Secret: {'*' * (len(settings.RAZORPAY_KEY_SECRET) - 4)}{settings.RAZORPAY_KEY_SECRET[-4:]}")
    except Exception as e:
        logger.error(f"Failed to initialize Razorpay client: {str(e)}")
        print(f"Error: {str(e)}")
        return

    # Get start and end dates for filter (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Convert to Unix timestamps as required by Razorpay API
    from_timestamp = int(start_date.timestamp())
    to_timestamp = int(end_date.timestamp())
    
    print(f"\nChecking Razorpay dashboard for payments from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Using timestamps: from={from_timestamp}, to={to_timestamp}")
    print("=" * 80)
    
    # Check for payments
    try:
        # First check orders directly (no timestamp filtering needed)
        print("\nChecking orders in Razorpay:")
        orders = razorpay_client.order.all({'count': 25})
        
        if orders and 'items' in orders and orders['items']:
            print(f"Found {len(orders['items'])} orders in Razorpay dashboard.")
            print("-" * 80)
            
            for order in orders['items']:
                print(f"Order ID: {order.get('id')}")
                print(f"Amount: {float(order.get('amount', 0)) / 100} {order.get('currency', 'INR')}")
                print(f"Status: {order.get('status')}")
                print(f"Attempts: {order.get('attempts', 0)}")
                created_at = order.get('created_at', 0)
                if created_at:
                    created_datetime = datetime.fromtimestamp(created_at)
                    print(f"Created At: {created_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # If this is the 69 rupees order, print all details
                if abs(float(order.get('amount', 0)) / 100 - 69.0) < 0.01:
                    print("\n*** THIS IS THE 69 RUPEES ORDER - FULL DETAILS ***")
                    print(json.dumps(order, indent=2))
                
                print("-" * 80)
        else:
            print("No orders found in Razorpay dashboard.")
        
        # Get all payments - first without date filtering to ensure we get all data
        print("\nChecking all recent payments in Razorpay:")
        payments = razorpay_client.payment.all({'count': 100})
        
        if payments and 'items' in payments and payments['items']:
            print(f"Found {len(payments['items'])} payments in Razorpay dashboard.")
            print("-" * 80)
            
            found_69_payment = False
            
            for payment in payments['items']:
                payment_amount = float(payment.get('amount', 0)) / 100
                payment_id = payment.get('id')
                order_id = payment.get('order_id', 'N/A')
                status = payment.get('status')
                method = payment.get('method', 'N/A')
                
                # Print details for all payments
                print(f"Payment ID: {payment_id}")
                print(f"Order ID: {order_id}")
                print(f"Amount: {payment_amount} {payment.get('currency', 'INR')}")
                print(f"Status: {status}")
                print(f"Method: {method}")
                
                created_at = payment.get('created_at', 0)
                if created_at:
                    created_datetime = datetime.fromtimestamp(created_at)
                    print(f"Created At: {created_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # If this is the 69 rupees payment, print all details
                if abs(payment_amount - 69.0) < 0.01:
                    found_69_payment = True
                    print("\n*** THIS IS THE 69 RUPEES PAYMENT - FULL DETAILS ***")
                    print(json.dumps(payment, indent=2))
                
                print("-" * 80)
            
            if not found_69_payment:
                print("\nWARNING: No 69 rupees payment found in the Razorpay dashboard.")
                print("This may indicate that:")
                print("1. The payment was not processed by Razorpay")
                print("2. The payment was made to a different Razorpay account")
                print("3. The payment may have been refunded or deleted")
                print("4. The API keys used may not have access to this payment")
        else:
            print("No payments found in Razorpay dashboard.")
            
    except Exception as e:
        logger.error(f"Error fetching from Razorpay: {str(e)}")
        print(f"Error: {str(e)}")
        
    print("=" * 80)

if __name__ == "__main__":
    print(f"Starting Razorpay dashboard check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    check_razorpay_dashboard()
    print(f"Completed Razorpay dashboard check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 