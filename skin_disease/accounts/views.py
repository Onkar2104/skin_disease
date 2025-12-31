import hashlib
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import User, RegisterOTP


@csrf_exempt
def send_register_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    email = request.POST.get("email", "").lower().strip()

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already in use"}, status=409)

    if not email:
        return JsonResponse({"error": "Email required"}, status=400)

    otp = str(random.randint(100000, 999999))

    obj, _ = RegisterOTP.objects.get_or_create(email=email)

    if obj.can_reset_resend():
        obj.resend_count = 0

    if obj.resend_count >= 3:
        return JsonResponse({"error": "OTP resend limit reached"}, status=429)

    obj.set_otp(otp)
    obj.resend_count += 1
    obj.created_at = timezone.now()
    obj.save()

    send_mail(
        "Your Verification Code",
        f"Your OTP is {otp}",
        settings.EMAIL_HOST_USER,
        [email],
    )

    return JsonResponse({"message": "OTP sent"})


@csrf_exempt
def verify_register_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    email = request.POST.get("email", "").lower().strip()
    otp = request.POST.get("otp", "")

    full_name = request.POST.get("full_name", "")
    password = request.POST.get("password", "")
    age_raw = request.POST.get("age")
    age = int(age_raw) if age_raw and age_raw.isdigit() else None
    gender = request.POST.get("gender", "")
    skin_type = request.POST.get("skin_type", "")

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

    # ✅ CREATE USER WITH FINAL DATA
    user = User.objects.create_user(
        email=email,
        password=password,  # Django will hash properly
        full_name=full_name,
        age=age,
        gender=gender,
        skin_type=skin_type,
    )

    obj.delete()

    return JsonResponse({"message": "Account created successfully"})
