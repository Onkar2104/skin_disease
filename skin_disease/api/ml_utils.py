
CLASS_NAMES = [
    'akiec', 'bcc', 'bkl', 'df',
    'mel', 'nv', 'scc', 'vasc'
]

CLASS_FULL_FORMS = {
    "akiec": "Actinic Keratoses and Intraepithelial Carcinoma",
    "bcc": "Basal Cell Carcinoma",
    "bkl": "Benign Keratosis-like Lesions",
    "df": "Dermatofibroma",
    "mel": "Melanoma",
    "nv": "Melanocytic Nevi",
    "scc": "Squamous Cell Carcinoma",
    "vasc": "Vascular Lesions",
}


import numpy as np
from io import BytesIO
from PIL import Image

try:
    from tensorflow.keras.applications.efficientnet import preprocess_input
    from tensorflow.keras.preprocessing.image import load_img, img_to_array
except Exception:
    from keras.applications.efficientnet import preprocess_input
    from keras.preprocessing.image import load_img, img_to_array

IMAGE_SIZE = (224, 224)

def preprocess_image_from_file(file_obj):
    
    file_obj.seek(0)
    raw = file_obj.read()
    img = Image.open(BytesIO(raw)).convert("RGB")
    img = img.resize(IMAGE_SIZE)
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return x


def predict_skin_disease_from_file(model, file_obj):
    x = preprocess_image_from_file(file_obj)

    preds = model.predict(x)[0]
    idx = int(np.argmax(preds))

    label_code = CLASS_NAMES[idx]
    full_form = CLASS_FULL_FORMS[label_code]
    confidence = float(preds[idx])

    print("predicted_label:", label_code,
        "predicted_disease:", full_form,
        "confidence:", confidence,
        "confidence_percent:", round(confidence * 100, 2),
        "explanation:", f"The model predicts {full_form} with {confidence*100:.2f}% confidence.")

    return {
        "predicted_label": label_code,
        "predicted_disease": full_form,
        "confidence": confidence,
        "confidence_percent": round(confidence * 100, 2),
        "explanation": f"The model predicts {full_form} with {confidence*100:.2f}% confidence."
    }
