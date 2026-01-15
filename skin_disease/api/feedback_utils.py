from .models import DoctorFeedback

def get_feedback_score(hospital_name, disease):
    feedbacks = DoctorFeedback.objects.filter(
        hospital_name=hospital_name,
        disease=disease
    )

    if not feedbacks.exists():
        return 0.5  # neutral

    avg_rating = sum(f.rating for f in feedbacks) / (5 * feedbacks.count())
    success_rate = sum(1 for f in feedbacks if f.successful) / feedbacks.count()

    return round((avg_rating * 0.6 + success_rate * 0.4), 2)
