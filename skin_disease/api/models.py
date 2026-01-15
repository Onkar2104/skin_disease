from django.db import models
from django.conf import settings

class Scan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="scans"
    )
    diagnosis = models.CharField(max_length=255)
    confidence = models.CharField(max_length=20)
    severity = models.CharField(max_length=20)
    advice = models.TextField()
    is_safe = models.BooleanField(default=True)
    image = models.ImageField(upload_to="scans/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.diagnosis}"
    

#Hospital Feedback Model
class DoctorFeedback(models.Model):
    doctor_name = models.CharField(max_length=255)
    hospital_name = models.CharField(max_length=255)
    disease = models.CharField(max_length=255)
    severity = models.CharField(max_length=20)

    rating = models.IntegerField()  # 1–5
    successful = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)

