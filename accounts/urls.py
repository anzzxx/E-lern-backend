from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegistrationAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    CustomTokenRefreshView,
    ProfileUpdateView,
    VerifyOTPAPIView,
    ResendOTPAPIView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView,
)

urlpatterns = [
    path("register/", UserRegistrationAPIView.as_view(), name="register-user"),
    path("login/", UserLoginAPIView.as_view(), name="login-user"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout-user"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile-update"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify-otp"),
    path("resend-otp/", ResendOTPAPIView.as_view(), name="resend-otp"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/<uidb64>/<token>/",ResetPasswordView.as_view(),name="reset-password",),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]