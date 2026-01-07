from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import *


urlpatterns = [
    path("register/", RegisterAPIView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutAPIView.as_view()),

    path("profile/update/", update_profile),
    path("profile/", get_profile),

    path("otp/email/send/", send_email_otp),
    path("otp/email/verify/", verify_email_otp),

    path("otp/phone/send/", send_phone_otp),
    path("otp/phone/verify/", verify_phone_otp),
]


