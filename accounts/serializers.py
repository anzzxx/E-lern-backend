from .models import CustomUser
from rest_framework import serializers
from django.contrib.auth import authenticate
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
import random
import datetime
from django.utils.timezone import now  # ✅ Import now() correctly
from rest_framework import serializers
from django.core.mail import send_mail
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=("id","username","email")


class UserRegistrationSerializer(serializers.ModelSerializer):
    password1=serializers.CharField(write_only=True)
    password2=serializers.CharField(write_only=True)

    class Meta:
        model=CustomUser
        fields=("id","username","email","password1","password2")
        extra_kwargs={"password":{"write_only":True}}

    def validate(self,attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("password do not match!")

        password=attrs.get("password1", "")
        if len(password)<8:
            raise serializers.ValidationError("Password must be at least 8 characters!")

        return attrs    

    def create(self,validated_data):
        password=validated_data.pop("password1")
        validated_data.pop("password2")

        otp = str(random.randint(100000, 999999))
        otp_expiration = now() + datetime.timedelta(minutes=10)  # OTP expires in 10 minutes

        user = CustomUser.objects.create_user(password=password, otp=otp, otp_expiration=otp_expiration, **validated_data)
        user.is_active = False # User is inactive until OTP is verified
        user.save()

        # Send OTP via email
        subject = "Your OTP for Account Verification"
        message = f"Your OTP is {otp}. It will expire in 10 minutes."
        send_mail(subject, message, "no-reply@sonic.com", [user.email])

        return user

        # return  CustomUser.objects.create_user(password=password,**validated_data) 


class UserLoginSerializer(serializers.Serializer):
    email=serializers.CharField()
    password=serializers.CharField(write_only=True)

    def validate(self,data):
        user=authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("incorrect Credential")    



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "profile_picture"]
        read_only_fields = ["email"]

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        if "profile_picture" in validated_data:
            instance.profile_picture = validated_data["profile_picture"]
        instance.save()
        return instance




logger = logging.getLogger(__name__)
User = get_user_model()


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            logger.info(f"Received data: {attrs}")  # Log input data

            refresh = RefreshToken(attrs["refresh"])  # Decode refresh token
            logger.info(f"Decoded refresh token: {refresh}")

            data = super().validate(attrs)  # Process normally
            access_token = AccessToken(data["access"])  # Decode access token

            user_id = refresh["user_id"]
            try:
                user = User.objects.get(id=user_id)

                # Add custom claims to the access token payload
                
                access_token["is_staff"] = user.is_staff
                access_token["is_superuser"] = user.is_superuser

                # Construct user data
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                }
            except ObjectDoesNotExist:
                user_data = None  # If user not found, return None

            data["access"] = str(access_token)  # Encode back to string
            data["user"] = user_data  # Add user data to the response

            return data
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise
