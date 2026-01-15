SPECIALTY_MATCH = {
    "High": ["oncologist", "dermatologist"],
    "Moderate": ["dermatologist"],
    "Low": ["dermatologist", "general"],
}

def score_doctor(*, doctor, severity):
    score = 0

    # ⭐ Rating
    score += doctor["rating"] * 2

    # 🎓 Experience
    score += min(doctor["experience_years"], 20) * 0.3

    # 🧬 Specialty relevance
    if doctor["specialty"].lower() in SPECIALTY_MATCH[severity]:
        score += 5

    # 📍 Distance
    score -= doctor["distance_km"] * 0.5

    return round(score, 2)


def explain_doctor_choice(doctor, severity):
    reasons = []

    if doctor["rating"] >= 4.5:
        reasons.append(f"high patient rating ({doctor['rating']}★)")

    if doctor["specialty"].lower() in SPECIALTY_MATCH[severity]:
        reasons.append(f"specialist for {severity.lower()} severity cases")

    if doctor["experience_years"] >= 10:
        reasons.append(f"{doctor['experience_years']}+ years of experience")

    if doctor["distance_km"] <= 3:
        reasons.append("located nearby")

    return "Recommended because of " + ", ".join(reasons) + "."
