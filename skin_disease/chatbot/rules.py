# chatbot/rules.py

RED_FLAG_KEYWORDS = [
    "bleeding",
    "severe pain",
    "spreading fast",
    "pus",
    "fever",
    "burning badly",
]

BLOCKED_KEYWORDS = [
    "medicine",
    "dosage",
    "tablet",
    "cream name",
    "steroid",
]

GREETING_KEYWORDS = [
    "hi",
    "hello",
    "hey",
    "good morning",
    "good evening",
]

SEVERITY_KEYWORDS = {
    "mild": ["slight", "small", "few", "light"],
    "moderate": ["itching", "redness", "pain"],
    "severe": ["severe", "worsening", "spreading", "very painful"],
}


def check_red_flags(message: str):
    message = message.lower()
    return any(word in message for word in RED_FLAG_KEYWORDS)


def check_blocked_content(message: str):
    message = message.lower()
    return any(word in message for word in BLOCKED_KEYWORDS)


def check_greeting(message: str):
    message = message.lower()
    return any(word in message for word in GREETING_KEYWORDS)


def detect_severity(message: str):
    message = message.lower()
    for level, keywords in SEVERITY_KEYWORDS.items():
        if any(word in message for word in keywords):
            return level
    return "unknown"
