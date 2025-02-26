from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path("register/",UserRegistrationAPIView.as_view(),name="register-user"),
    # path("login/",UserLoginAPIView.as_view(),name="login-user"),
    path("login/", UserLoginAPIView.as_view(), name="login-user"),
    path("logout/",UserLogoutAPIView.as_view(),name="logour-user"),
    path("token/refresh/",CustomTokenRefreshView.as_view(),name="token-refresh"),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify-otp"),
    path("resend-otp/", ResendOTPAPIView.as_view(), name="resend-otp"),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
]


    # path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
