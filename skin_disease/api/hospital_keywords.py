DISEASE_KEYWORDS = {
    "Basal Cell Carcinoma": "dermatology skin cancer hospital",
    "Melanoma": "oncology dermatology hospital",
    "Squamous Cell Carcinoma": "skin cancer hospital",
    "Actinic Keratoses and Intraepithelial Carcinoma": "dermatology clinic",
    "Benign Keratosis-like Lesions": "dermatology clinic",
    "Dermatofibroma": "dermatology clinic",
    "Melanocytic Nevi": "dermatology clinic",
    "Vascular Lesions": "vascular dermatology clinic",
}

def get_keyword_from_diagnosis(diagnosis: str) -> str:
    return DISEASE_KEYWORDS.get(diagnosis, "dermatology hospital")
