from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email, otp):
    """Send OTP to the user's email."""
    subject = "Your OTP Code for Verification"
    message = f"Your OTP code is {otp}. It is valid for 5 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
