import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes

from .serializers import *
from .models import User, VerificationOTP



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    return Response({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "email_verified": user.email_verified,
        "phone_verified": user.phone_verified,
        "gender": user.gender,
        "blood_group": user.blood_group,
        "skin_type": user.skin_type,
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    data = request.data

    editable_fields = [
        "full_name", "phone", "dob", "age", "gender", "skin_type",
        "blood_group", "whatsapp_number", "emergency_contact",
        "area", "city", "taluka", "district", "state",
        "country", "pincode", "insurance_name", "insurance_number"
    ]

    for field in editable_fields:
        if field in data:
            setattr(user, field, data.get(field))

    # Reset verification if changed
    if "email" in data and data["email"] != user.email:
        user.email = data["email"]
        user.email_verified = False

    if "phone" in data and data["phone"] != user.phone:
        user.phone_verified = False

    if "profile_photo" in request.FILES:
        user.profile_photo = request.FILES["profile_photo"]

    user.save()
    return Response({"message": "Profile updated successfully"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_email_otp(request):
    email = request.user.email
    otp = str(random.randint(100000, 999999))

    obj, _ = VerificationOTP.objects.get_or_create(
        identifier=email,
        purpose="email"
    )
    obj.set_otp(otp)
    obj.save()

    send_mail(
        "Email Verification OTP",
        f"Your OTP is {otp}. Valid for 5 minutes.",
        settings.EMAIL_HOST_USER,
        [email],
    )

    return Response({"message": "Email OTP sent"})



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_email_otp(request):
    otp = request.data.get("otp")
    email = request.user.email

    try:
        obj = VerificationOTP.objects.get(
            identifier=email,
            purpose="email"
        )
    except VerificationOTP.DoesNotExist:
        return Response(
            {"error": "OTP not found. Please request OTP first."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if obj.is_expired():
        obj.delete()
        return Response(
            {"error": "OTP expired. Please resend OTP."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not obj.check_otp(otp):
        return Response(
            {"error": "Invalid OTP"},
            status=status.HTTP_400_BAD_REQUEST
        )

    request.user.email_verified = True
    request.user.save()
    obj.delete()

    return Response({"message": "Email verified successfully"})




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_phone_otp(request):
    phone = request.user.phone

    # ✅ FIX: guard clause
    if not phone:
        return Response(
            {"error": "Please add phone number before verification"},
            status=status.HTTP_400_BAD_REQUEST
        )

    otp = str(random.randint(100000, 999999))

    obj, _ = VerificationOTP.objects.get_or_create(
        identifier=phone,
        purpose="phone"
    )
    obj.set_otp(otp)
    obj.save()

    print("PHONE OTP:", otp)

    return Response({"message": "Phone OTP sent"})



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_phone_otp(request):
    otp = request.data.get("otp")
    phone = request.user.phone

    if not phone:
        return Response(
            {"error": "Phone number not set"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        obj = VerificationOTP.objects.get(
            identifier=phone,
            purpose="phone"
        )
    except VerificationOTP.DoesNotExist:
        return Response(
            {"error": "OTP not found. Please request OTP first."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if obj.is_expired():
        obj.delete()
        return Response(
            {"error": "OTP expired. Please resend OTP."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not obj.check_otp(otp):
        return Response(
            {"error": "Invalid OTP"},
            status=status.HTTP_400_BAD_REQUEST
        )

    request.user.phone_verified = True
    request.user.save()
    obj.delete()

    return Response({"message": "Phone verified successfully"})




class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Account created successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

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

