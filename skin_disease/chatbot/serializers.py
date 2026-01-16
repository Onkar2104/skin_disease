# chatbot/serializers.py
from rest_framework import serializers

class ChatbotRequestSerializer(serializers.Serializer):
    message = serializers.CharField()
    disease = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    trigger = serializers.CharField(required=False, allow_blank=True)