from datetime import datetime
import random

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    CustomUserSerializer,
    UserProfileSerializer,
    CustomTokenRefreshSerializer,
)
from .utils import send_otp_email


class UserRegistrationAPIView(GenericAPIView):
    """Handle user registration with OTP verification."""
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        serialized_user = self.get_serializer(user).data

        return Response(
            {
                "message": "OTP sent to your email. Please verify to activate your account.",
                "user": serialized_user,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPAPIView(APIView):
    """Verify OTP for user account activation."""
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        try:
            user = CustomUser.objects.get(email=email)

            if user.is_active:
                return Response(
                    {"message": "User already verified!"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.otp != otp:
                return Response(
                    {"error": "Invalid OTP!"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.otp_expiration < now():
                return Response(
                    {"error": "OTP expired! Please request a new one."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # OTP is correct, activate user
            user.is_active = True
            user.otp = None  # Clear OTP
            user.otp_expiration = None
            user.save()

            return Response(
                {"message": "Account verified successfully!"}, 
                status=status.HTTP_200_OK
            )

        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found!"}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ResendOTPAPIView(APIView):
    """Handle resending OTP for account verification."""
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get("email")

        try:
            user = CustomUser.objects.get(email=email)

            if user.is_active:
                return Response(
                    {"message": "User already verified!"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate new OTP
            otp = str(random.randint(100000, 999999))
            otp_expiration = now() + datetime.timedelta(minutes=10)
            user.otp = otp
            user.otp_expiration = otp_expiration
            user.save()

            # Send OTP via email
            subject = "Your New OTP for Account Verification"
            message = f"Your new OTP is {otp}. It will expire in 10 minutes."
            send_mail(subject, message, "no-reply@sonic.com", [user.email])

            return Response(
                {"message": "New OTP sent to your email!"},
                status=status.HTTP_200_OK
            )

        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found!"}, 
                status=status.HTTP_404_NOT_FOUND
            )


class UserLoginAPIView(GenericAPIView):
    """Handle user authentication and JWT token generation."""
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Add custom claim to access token payload
        access_token["is_staff"] = user.is_staff
        access_token["is_superuser"] = user.is_superuser

        # Serialize user data
        serializer = CustomUserSerializer(user)
        data = serializer.data
        data["tokens"] = {
            "refresh": str(refresh),
            "access": str(access_token) 
        }

        return Response(data, status=status.HTTP_200_OK)


class UserLogoutAPIView(GenericAPIView):
    """Handle user logout by blacklisting refresh token."""
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ProfileUpdateView(APIView):
    """Handle user profile updates including profile picture."""
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileSerializer(user)  
        return Response(serializer.data, status=200)

    def put(self, request, *args, **kwargs):
        user = request.user
        if request.data.get("remove_image") == "true":
            user.profile_picture = None
            user.save()
            return Response(
                {
                    "message": "Profile image removed successfully",
                    "profile_picture": None
                },
                status=200
            )

        serializer = UserProfileSerializer(
            user, 
            data=request.data, 
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully"}, 
                status=200
            )
        
        return Response(serializer.errors, status=400)


class CustomTokenRefreshView(TokenRefreshView):
    """Custom JWT token refresh view with additional user data."""
    serializer_class = CustomTokenRefreshSerializer


class ForgotPasswordView(APIView):
    """Handle password reset requests."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"http://localhost:5173/reset-password/{uid}/{token}/"
            
            send_mail(
                "Password Reset Request",
                f"Click the link to reset your password: {reset_link}",
                "no-reply@elern.com",
                [user.email],
                fail_silently=False,
            )
            
            return Response(
                {"message": "Password reset link sent to email."},
                status=status.HTTP_200_OK
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResetPasswordView(APIView):
    """Handle password reset confirmation."""
    permission_classes = [AllowAny]
    
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
    
            if not default_token_generator.check_token(user, token):
                return Response(
                    {"error": "Invalid or expired token."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            new_password = request.data.get("password")
            if len(new_password) < 8:
                return Response(
                    {"error": "Password must be at least 8 characters long."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(new_password)
            user.save()
            
            return Response(
                {"message": "Password reset successful."},
                status=status.HTTP_200_OK
            )
        except (CustomUser.DoesNotExist, ValueError, TypeError):
            return Response(
                {"error": "Invalid request."},
                status=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordView(APIView):
    """Handle authenticated user password changes."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate new password length
        if len(new_password) < 8:
            return Response(
                {"error": "New password must be at least 8 characters long."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set the new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK
        )