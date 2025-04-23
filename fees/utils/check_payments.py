"""
Utility script to check payment transactions and verify their status in Razorpay
"""
import os
import sys
import django
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

# Now import Django modules
from django.conf import settings
from fees.models import FeeTransaction
from fees.utils.logging import logger
import razorpay
import json

def check_transactions():
    """Check the status of recent transactions in database and Razorpay"""
    # Initialize Razorpay client
    try:
        razorpay_client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        logger.info(f"Connected to Razorpay with key ID: {settings.RAZORPAY_KEY_ID}")
    except Exception as e:
        logger.error(f"Failed to initialize Razorpay client: {str(e)}")
        return

    # Get the 10 most recent transactions
    transactions = FeeTransaction.objects.all().order_by('-created_at')[:10]
    
    if not transactions:
        print("No transactions found in the database.")
        return
    
    print(f"Found {len(transactions)} recent transactions.")
    print("=" * 80)
    
    for t in transactions:
        print(f"Transaction ID: {t.id}")
        print(f"Student: {t.student.first_name} {t.student.last_name}")
        print(f"Amount: {t.amount}")
        print(f"Status: {t.status}")
        print(f"Razorpay ID: {t.transaction_id}")
        print(f"Created at: {t.created_at}")
        
        # Check transaction in Razorpay if we have a transaction ID
        if t.transaction_id:
            try:
                # First try to fetch as an order
                razorpay_order = razorpay_client.order.fetch(t.transaction_id)
                print("\nRazorpay Order Details:")
                print(f"Order ID: {razorpay_order.get('id')}")
                print(f"Order Status: {razorpay_order.get('status')}")
                print(f"Order Amount: {float(razorpay_order.get('amount', 0)) / 100}")  # Convert paise to rupees
                
                # Try to find associated payments for this order
                payments = razorpay_client.payment.all({'order_id': t.transaction_id})
                if payments and 'items' in payments and payments['items']:
                    print("\nAssociated Payments:")
                    for payment in payments['items']:
                        print(f"Payment ID: {payment.get('id')}")
                        print(f"Payment Status: {payment.get('status')}")
                        print(f"Payment Amount: {float(payment.get('amount', 0)) / 100}")
                        print(f"Payment Method: {payment.get('method')}")
                else:
                    print("\nNo payments found for this order in Razorpay.")
            except Exception as e:
                print(f"\nError fetching from Razorpay: {str(e)}")
                
                # If it's not an order, try to fetch as a payment
                try:
                    payment = razorpay_client.payment.fetch(t.transaction_id)
                    print("\nRazorpay Payment Details:")
                    print(f"Payment ID: {payment.get('id')}")
                    print(f"Payment Status: {payment.get('status')}")
                    print(f"Payment Amount: {float(payment.get('amount', 0)) / 100}")
                    print(f"Payment Method: {payment.get('method')}")
                except Exception as e2:
                    print(f"Error fetching as payment: {str(e2)}")
        else:
            print("\nNo Razorpay transaction ID available.")
        
        print("-" * 80)

if __name__ == "__main__":
    print(f"Starting payment check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    check_transactions()
    print(f"Completed payment check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 