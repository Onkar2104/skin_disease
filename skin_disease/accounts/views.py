import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import *
from .models import User, RegisterOTP


# ---------------- SEND OTP ----------------
@csrf_exempt
def send_register_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    email = request.POST.get("email", "").lower().strip()

    if not email:
        return JsonResponse({"error": "Email required"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already in use"}, status=409)

    otp = str(random.randint(100000, 999999))

    obj, _ = RegisterOTP.objects.get_or_create(email=email)

    if obj.can_reset_resend():
        obj.resend_count = 0

    if obj.resend_count >= 3:
        return JsonResponse({"error": "OTP resend limit reached"}, status=429)

    obj.set_otp(otp)
    obj.resend_count += 1
    obj.created_at = timezone.now()
    obj.is_verified = False
    obj.save()

    send_mail(
        "Your Verification Code",
        f"Your OTP is {otp}",
        settings.EMAIL_HOST_USER,
        [email],
    )

    return JsonResponse({"message": "OTP sent"})


# ---------------- VERIFY OTP (NO USER CREATION) ----------------
@csrf_exempt
def verify_register_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    email = request.POST.get("email", "").lower().strip()
    otp = request.POST.get("otp", "")

    try:
        obj = RegisterOTP.objects.get(email=email)
    except RegisterOTP.DoesNotExist:
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    if obj.is_expired():
        obj.delete()
        return JsonResponse({"error": "OTP expired"}, status=400)

    if not obj.check_otp(otp):
        obj.attempts += 1
        obj.save()
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    # ✅ MARK VERIFIED ONLY
    obj.is_verified = True
    obj.save()

    return JsonResponse({"message": "OTP verified successfully"})


# ---------------- FINAL REGISTER ----------------
@csrf_exempt
def register_user(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = data.get("email", "").lower().strip()

    try:
        otp_obj = RegisterOTP.objects.get(email=email, is_verified=True)
    except RegisterOTP.DoesNotExist:
        return JsonResponse({"error": "Email not verified"}, status=403)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "User already exists"}, status=409)

    user = User.objects.create_user(
        email=email,
        password=data.get("password"),
        full_name=data.get("full_name", ""),
        age=data.get("age"),
        gender=data.get("gender", ""),
        skin_type=data.get("skin_type", ""),
    )

    otp_obj.delete()

    return JsonResponse({"message": "Account created"})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"error": "Account disabled"},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "age": user.age,
                "gender": user.gender,
                "skin_type": user.skin_type,
            }
        })


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # For JWT → frontend just deletes token
        # For session → Django handles it
        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )

