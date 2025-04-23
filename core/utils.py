from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_otp_email(email, otp, purpose='registration'):
    """
    Send OTP email for registration or password reset
    """
    if purpose == 'registration':
        subject = 'Verify Your Email - School Management System'
        template = 'core/emails/registration_otp.html'
    else:
        subject = 'Password Reset OTP - School Management System'
        template = 'core/emails/password_reset_otp.html'

    context = {
        'otp': otp,
        'email': email,
        'purpose': purpose
    }
    
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

def send_welcome_email(user):
    """
    Send welcome email to newly registered user
    """
    subject = 'Welcome to School Management System'
    template = 'core/emails/welcome.html'
    
    context = {
        'user': user,
    }
    
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        # Log the error but don't fail the registration process 