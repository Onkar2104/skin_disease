from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import hashlib

# Create your models here.


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            return ValueError("Email required")


        email = self.normalize_email(email)
        user = self.model(email = email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db) 

        return user
    
    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    

class User(AbstractBaseUser, PermissionsMixin):
    # --- BASIC ---
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)

    # --- VERIFICATION FLAGS ---
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    # --- PERSONAL ---
    dob = models.DateField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, default="Other")
    skin_type = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)

    # --- CONTACT ---
    whatsapp_number = models.CharField(max_length=15, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)

    # --- ADDRESS ---
    area = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    taluka = models.CharField(max_length=50, blank=True)
    district = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    pincode = models.CharField(max_length=6, blank=True)

    # --- INSURANCE ---
    insurance_name = models.CharField(max_length=100, blank=True)
    insurance_number = models.CharField(max_length=50, blank=True)

    # --- PROFILE PHOTO ---
    profile_photo = models.ImageField(upload_to="profiles/", blank=True, null=True)

    # --- SYSTEM ---
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

class VerificationOTP(models.Model):
    identifier = models.CharField(max_length=100)  # email or phone
    purpose = models.CharField(max_length=10)      # email | phone
    otp_hash = models.CharField(max_length=128)

    resend_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent_at = models.DateTimeField(auto_now=True)

    def set_otp(self, otp):
        self.otp_hash = hashlib.sha256(otp.encode()).hexdigest()

    def check_otp(self, otp):
        return self.otp_hash == hashlib.sha256(otp.encode()).hexdigest()

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)
