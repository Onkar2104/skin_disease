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
    username = None
    email = models.EmailField(unique=True, blank=False, null=False)
    full_name = models.CharField(max_length=50, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, null=True, default='')
    otp = models.IntegerField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, default='Other')
    skin_type = models.CharField(max_length=20, blank=True, default='')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_short_name(self):
        return self.full_name.split(' ')[0]
    


class RegisterOTP(models.Model):
    email = models.EmailField(unique=True)

    otp_hash = models.CharField(max_length=128)

    full_name = models.CharField(max_length=50, blank=True, null=True)
    password_hash = models.CharField(max_length=128, blank=True, null=True)
    age = models.PositiveIntegerField(default=1,blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    skin_type = models.CharField(max_length=20, blank=True, null=True)

    resend_count = models.IntegerField(default=0)
    attempts = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    last_sent_at = models.DateTimeField(auto_now=True)

    def set_otp(self, otp: str):
        self.otp_hash = hashlib.sha256(str(otp).encode()).hexdigest()

    def check_otp(self, otp: str) -> bool:
        return self.otp_hash == hashlib.sha256(str(otp).encode()).hexdigest()

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def can_reset_resend(self):
        return timezone.now() > self.last_sent_at + timezone.timedelta(minutes=30)
