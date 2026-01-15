def predict_suitability(*, rating, distance, severity):
    """
    This will later become:
    model.predict_proba(X)[1]
    """

    severity_boost = {
        "Low": 0.2,
        "Moderate": 0.4,
        "High": 0.6,
    }[severity]

    score = (
        rating * 0.15
        - distance * 0.03
        + severity_boost
    )

    # Clamp to [0, 1]
    return round(max(0, min(score, 1)), 2)
