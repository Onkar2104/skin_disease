def generate_hospital_explanation(
    *,
    severity,
    rating,
    distance,
    ml_score,
):
    reasons = []

    # Rating explanation
    if rating >= 4.5:
        reasons.append(f"high patient rating ({rating}★)")
    elif rating >= 4.0:
        reasons.append(f"good rating ({rating}★)")

    # Severity-based reasoning
    if severity == "High" and ml_score >= 0.7:
        reasons.append("suitable for high-severity cases")
    elif severity == "Moderate" and ml_score >= 0.6:
        reasons.append("well-suited for moderate conditions")
    elif severity == "Low":
        reasons.append("appropriate for routine dermatology care")

    # Distance reasoning
    if distance <= 3:
        reasons.append(f"very close to you ({distance} km)")
    elif distance <= 7:
        reasons.append(f"within reasonable distance ({distance} km)")

    if not reasons:
        reasons.append("overall good match for your condition")

    # Final human-readable explanation
    return "Recommended because it has " + ", ".join(reasons) + "."
