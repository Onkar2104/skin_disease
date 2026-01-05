from rest_framework import serializers
from .models import Scan

class ScanSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)

    class Meta:
        model = Scan
        fields = "__all__"
        read_only_fields = ("user", "created_at")
