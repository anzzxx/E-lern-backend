from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string
from django.utils.timezone import now, timedelta

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiration = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def generate_otp(self):
        """Generate a 6-digit OTP and set expiration time."""
        self.otp = ''.join(random.choices(string.digits, k=6))  
        self.otp_expiration = now() + timedelta(minutes=5) 
        self.save()


