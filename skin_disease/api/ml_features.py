def extract_features(
    disease,
    severity,
    hospital_type,
    rating,
    distance,
    feedback_score,
):
    return {
        "disease": disease,
        "severity": severity,
        "hospital_type": hospital_type,
        "rating": rating,
        "distance": distance,
        "feedback_score": feedback_score,
    }
