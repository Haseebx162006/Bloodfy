"""
Auth URL routes.
"""

from django.urls import path
from ..views import (
    RegisterView,
    LoginView,
    LogoutView,
    VerifyEmailView,
    ResendOTPView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    CustomTokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='auth-refresh'),
    path('verify-email/', VerifyEmailView.as_view(), name='auth-verify-email'),
    path('resend-otp/', ResendOTPView.as_view(), name='auth-resend-otp'),
    path('request-password-reset/', PasswordResetRequestView.as_view(), name='auth-password-reset-request'),
    path('reset-password/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
]
