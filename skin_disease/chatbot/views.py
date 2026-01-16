# chatbot/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import ChatbotRequestSerializer
from .rules import detect_severity
from .ai_services import get_gemini_reply


@api_view(["POST"])
@permission_classes([AllowAny])
def chatbot_response(request):
    serializer = ChatbotRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    message = serializer.validated_data["message"]
    disease = serializer.validated_data.get("disease")
    trigger = serializer.validated_data.get("trigger")

    severity = serializer.validated_data.get("severity") or detect_severity(message)

    # ------------------------------
    # 1️⃣ AUTO MESSAGE AFTER SCAN
    # ------------------------------
    if trigger == "scan_result":
        message = (
            f"A skin scan was completed.\n"
            f"Possible condition detected: {disease}.\n\n"
            "Guide the user calmly and step-by-step.\n"
            "Do NOT mention medicines.\n"
            "Encourage selecting one next action."
        )

    # ------------------------------
    # 2️⃣ CALL AI (SAFE WRAPPER)
    # ------------------------------
    ai_result = get_gemini_reply(
        message=message,
        disease=disease,
        severity=severity,
        trigger=trigger,
    )


    ai_available = ai_result["ai_available"]
    reply_text = ai_result["text"]

    # ------------------------------
    # 3️⃣ QUICK REPLIES (SMART + SAFE)
    # ------------------------------
    if severity == "mild":
        quick_replies = [
            "Daily skin care tips",
            "Common triggers",
            "How to prevent worsening",
            "When should I worry?",
        ]
    elif severity == "moderate":
        quick_replies = [
            "How serious is this?",
            "Daily care tips",
            "Warning signs to watch",
            "Should I see a doctor?",
        ]
    elif severity == "severe":
        quick_replies = [
            "Is this dangerous?",
            "Emergency warning signs",
            "Find nearby dermatologist",
            "What should I do now?",
        ]
    else:
        quick_replies = [
            "Explain this condition",
            "Daily skin care tips",
            "When to see a doctor",
        ]

    # ------------------------------
    # 4️⃣ FALLBACK MODE LOCK
    # ------------------------------
    if not ai_available:
        quick_replies = [
            "Explain this condition",
            "Daily skin care tips",
            "When to see a doctor",
        ]

    # ------------------------------
    # 5️⃣ FINAL RESPONSE
    # ------------------------------
    return Response({
        "reply": reply_text,
        "severity": severity,
        "quick_replies": quick_replies,
        "ai_available": ai_available,
        "disclaimer": (
            "This chatbot provides general information only and "
            "is not a substitute for professional medical advice."
        ),
    })









