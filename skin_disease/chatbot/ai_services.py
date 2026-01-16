# chatbot/ai_services.py

from google import genai
from django.conf import settings
from .rules import detect_severity
from .prompts import SYSTEM_PROMPT
from google.genai.errors import ClientError


FORBIDDEN_TERMS = [
    "tablet", "capsule", "dosage", "mg",
    "ointment", "cream", "antibiotic",
    "steroid", "medicine"
]


def sanitize(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in FORBIDDEN_TERMS):
        return (
            "I can’t provide treatment or medication details. "
            "I can help with general care and guidance."
        )
    return text


# Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)



def detect_intent(message: str) -> str:
    msg = message.lower()

    if "explain" in msg or "what is" in msg:
        return "explain"

    if "daily" in msg or "care" in msg or "tips" in msg:
        return "care"

    if "worry" in msg or "danger" in msg or "serious" in msg:
        return "risk"

    if "doctor" in msg or "specialist" in msg:
        return "doctor"

    return "general"


def rule_based_reply(disease: str, severity: str, intent: str) -> str:
    header = f"I’ve reviewed your scan showing a possible {disease}.\n\n"

    if intent == "explain":
        return header + (
            f"{disease} refers to changes in skin pigmentation.\n\n"
            "Most cases are harmless, but monitoring changes in size, color, "
            "or shape is important.\n\n"
            "If anything changes rapidly, professional evaluation is advised."
        )

    if intent == "care":
        return header + (
            "General daily skin care guidance:\n\n"
            "• Keep skin clean and dry\n"
            "• Avoid excessive sun exposure\n"
            "• Do not scratch or irritate the area\n"
            "• Observe for visible changes\n"
        )

    if intent == "risk":
        return header + (
            "Warning signs to watch for:\n\n"
            "• Rapid size change\n"
            "• Uneven borders\n"
            "• Color variation\n"
            "• Bleeding or pain\n\n"
            "Seek medical advice if any of these occur."
        )

    if intent == "doctor":
        return header + (
            "If you’re concerned or symptoms persist, "
            "a dermatologist can provide proper evaluation."
        )

    return header + (
        "Skin conditions can have many causes.\n\n"
        "Monitoring and professional advice are recommended if unsure."
    )


def get_gemini_reply(message: str, disease: str | None, severity: str, trigger=None):
    severity = severity or detect_severity(message)

    prompt = f"""
{SYSTEM_PROMPT}

Possible condition (NOT confirmed): {disease}
Estimated severity: {severity}

User message:
"{message}"

Respond with:
• Clear guidance
• Severity-based advice
• NO medicines
• ONE follow-up question
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt,
        )

        return {
            "ai_available": True,
            "text": sanitize(response.text.strip()),
        }

    except ClientError:
        intent = detect_intent(message)
        return {
            "ai_available": False,
            "text": rule_based_reply(disease or "this condition", severity, intent),
        }

