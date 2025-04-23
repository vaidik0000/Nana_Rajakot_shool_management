from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from ..models import FeeTransaction
from fees.utils.logging import log_payment_error
import os


def generate_payment_receipt(transaction_id):
    """
    Generate a professionally designed PDF payment receipt for a given transaction
    
    Args:
        transaction_id: ID of the FeeTransaction
        
    Returns:
        tuple: (BytesIO buffer with PDF content, transaction object)
    """
    try:
        transaction = FeeTransaction.objects.get(id=transaction_id)
        student = transaction.student
        
        # Create PDF buffer with higher quality settings
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.setTitle(f"Payment Receipt - {transaction.receipt_number or f'RCPT-{transaction.id}'}")
        width, height = A4
        
        # Set up colors
        primary_color = colors.HexColor('#1E5288')  # Deeper blue for headings
        secondary_color = colors.HexColor('#4A90E2')  # Lighter blue for accents
        border_color = colors.HexColor('#E0E0E0')  # Light gray for borders
        
        # Background design elements
        # Subtle top header background
        p.setFillColor(colors.HexColor('#F5F8FB'))
        p.rect(0, height - 120, width, 120, fill=True, stroke=False)
        
        # Accent line at top
        p.setFillColor(secondary_color)
        p.rect(0, height - 10, width, 10, fill=True, stroke=False)
        
        # School logo/header
        if hasattr(settings, 'SCHOOL_LOGO_PATH') and os.path.exists(settings.SCHOOL_LOGO_PATH):
            # Add logo if available
            p.drawImage(settings.SCHOOL_LOGO_PATH, 50, height - 100, width=80, height=80, mask='auto')
            header_start = 150
        else:
            header_start = 50
            
        # School header with better typography
        p.setFillColor(primary_color)
        p.setFont("Helvetica-Bold", 24)
        p.drawString(header_start, height - 50, "School Management System")
        
        # Add subtle watermark
        p.saveState()
        p.setFillColor(colors.HexColor('#F8F8F8'))
        p.setFont("Helvetica-Bold", 80)
        p.rotate(45)
        p.drawCentredString(350, 100, "PAID")
        p.restoreState()
        
        # Receipt title with better visual distinction
        p.setFillColor(secondary_color)
        p.setFont("Helvetica-Bold", 18)
        p.drawString(header_start, height - 80, "PAYMENT RECEIPT")
        
        # Draw styled receipt box
        content_top = height - 130
        content_bottom = 100
        content_width = width - 100
        
        # Receipt outline with rounded corners
        p.setStrokeColor(border_color)
        p.setLineWidth(1)
        p.roundRect(50, content_bottom, content_width, content_top - content_bottom, 10, stroke=True, fill=False)
        
        # Receipt details in better layout (2-column design)
        p.setFont("Helvetica-Bold", 11)
        p.setFillColor(colors.black)
        
        # Receipt number and date in visually distinct area
        p.setFillColor(colors.HexColor('#F8F8F8'))
        p.rect(51, content_top - 40, content_width - 2, 40, fill=True, stroke=False)
        
        p.setFillColor(primary_color)
        p.drawString(70, content_top - 15, "Receipt No:")
        p.drawString(350, content_top - 15, "Date:")
        
        p.setFillColor(colors.black)
        p.setFont("Helvetica", 11)
        p.drawString(140, content_top - 15, f"{transaction.receipt_number or f'RCPT-{transaction.id}'}")
        p.drawString(390, content_top - 15, f"{transaction.created_at.strftime('%d %b %Y, %I:%M %p')}")
        
        # Divider
        p.setStrokeColor(border_color)
        p.setLineWidth(1)
        p.line(51, content_top - 60, content_width + 49, content_top - 60)
        
        # Two-column layout for student and payment details
        left_col_x = 70
        right_col_x = width/2 + 20
        
        # Student details - Left column
        p.setFillColor(primary_color)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(left_col_x, content_top - 85, "Student Details")
        
        p.setFillColor(colors.black)
        details = [
            ("Name:", f"{student.first_name} {student.last_name}"),
            ("Roll Number:", f"{student.roll_number}"),
            ("Class:", f"{student.get_class_name_display()}"),
            ("Email:", f"{student.email or student.parent_email or 'N/A'}"),
        ]
        
        y_position = content_top - 115
        for label, value in details:
            p.setFont("Helvetica-Bold", 11)
            p.setFillColor(colors.HexColor('#555555'))
            p.drawString(left_col_x, y_position, label)
            p.setFont("Helvetica", 11)
            p.setFillColor(colors.black)
            p.drawString(left_col_x + 85, y_position, value)
            y_position -= 25
        
        # Payment details - Right column
        p.setFillColor(primary_color)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(right_col_x, content_top - 85, "Payment Details")
        
        payment_details = [
            ("Amount Paid:", f"₹{transaction.amount:,}"),
            ("Transaction ID:", f"{transaction.transaction_id}"),
            ("Payment Status:", "Completed"),
            ("Payment Date:", f"{transaction.created_at.strftime('%d %b %Y')}"),
        ]
        
        y_position = content_top - 115
        for label, value in payment_details:
            p.setFont("Helvetica-Bold", 11)
            p.setFillColor(colors.HexColor('#555555'))
            p.drawString(right_col_x, y_position, label)
            p.setFont("Helvetica", 11)
            p.setFillColor(colors.black)
            p.drawString(right_col_x + 100, y_position, value)
            y_position -= 25
        
        # Description in full width
        p.setFont("Helvetica-Bold", 11)
        p.setFillColor(colors.HexColor('#555555'))
        p.drawString(70, content_top - 225, "Description:")
        p.setFont("Helvetica", 11)
        p.setFillColor(colors.black)
        
        # Handle multiline description
        description = transaction.description or 'School Fee Payment'
        description_width = content_width - 100
        description_lines = []
        
        # Simple text wrapping
        words = description.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if p.stringWidth(test_line, "Helvetica", 11) < description_width:
                current_line = test_line
            else:
                description_lines.append(current_line)
                current_line = word
                
        if current_line:
            description_lines.append(current_line)
            
        desc_y = content_top - 225
        for line in description_lines:
            p.drawString(160, desc_y, line)
            desc_y -= 20
        
       
        
        # Verification text
        p.setFont("Helvetica", 9)
        p.drawCentredString(width - 90, content_bottom + 10, "Scan to verify")
        
        # Footer with improved layout
        p.setFillColor(colors.HexColor('#F5F8FB'))
        p.rect(0, 0, width, 80, fill=True, stroke=False)
        
        p.setFillColor(colors.HexColor('#555555'))
        p.setFont("Helvetica-Bold", 9)
        p.drawString(60, 55, "This is a computer-generated receipt and does not require a signature.")
        
        p.setFont("Helvetica", 9)
        p.drawString(60, 40, "For any queries, please contact the school administration at:")
        p.setFillColor(secondary_color)
        p.drawString(60, 25, getattr(settings, 'SCHOOL_CONTACT_EMAIL', 'kotadiyavaidik10@gmail.com'))
        
        # School stamp/seal (placeholder circle)
        p.setStrokeColor(secondary_color)
        p.setLineWidth(1.5)
        p.circle(width - 100, 40, 25, stroke=True, fill=False)
        p.setFont("Helvetica-Bold", 7)
        p.setFillColor(secondary_color)
        p.drawCentredString(width - 100, 42, "SCHOOL")
        p.drawCentredString(width - 100, 35, "SEAL")
        
        # Draw a subtle bottom border
        p.setFillColor(secondary_color)
        p.rect(0, 0, width, 5, fill=True, stroke=False)
        
        # Save PDF
        p.showPage()
        p.save()
        buffer.seek(0)
        
        return buffer, transaction
    
    except FeeTransaction.DoesNotExist:
        raise ValueError(f"Transaction with ID {transaction_id} not found")
    except Exception as e:
        log_payment_error(
            error_type='receipt_generation',
            error_message=str(e),
            transaction_id=transaction_id
        )
        raise

def send_receipt_email(transaction_id):
    """
    Generate and send a receipt email for a transaction
    
    Args:
        transaction_id: ID of the FeeTransaction
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        buffer, transaction = generate_payment_receipt(transaction_id)
        student = transaction.student
        
        # Determine recipient email
        recipient_email = student.email or student.parent_email
        if not recipient_email:
            return False, "No email address available for student"
        
        # Create email
        subject = f"Payment Receipt - {student.first_name} {student.last_name}"
        email_message = EmailMessage(
            subject=subject,
            body=f"Dear {student.first_name} {student.last_name},\n\nThank you for your payment. Please find attached the receipt for your recent fee payment of ₹{transaction.amount}.\n\nRegards,\nSchool Management System",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        
        # Attach PDF
        email_message.attach(f'payment_receipt_{transaction.id}.pdf', buffer.getvalue(), 'application/pdf')
        
        # Send email
        email_message.send(fail_silently=False)
        return True, f"Receipt sent to {recipient_email}"
    
    except Exception as e:
        log_payment_error(
            error_type='receipt_email',
            error_message=str(e),
            transaction_id=transaction_id
        )
        return False, str(e) 