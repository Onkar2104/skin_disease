from django.urls import path
from .views import send_register_otp, verify_register_otp

urlpatterns = [
    path("register/send-otp/", send_register_otp),
    path("register/verify-otp/", verify_register_otp),
]

