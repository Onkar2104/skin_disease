# 🧠 Skin Disease Classification

An **AI/ML-based Skin Disease Classification system** that predicts different skin diseases from images using **Deep Learning (CNN)**.  
This project aims to assist in **early detection of skin diseases** and act as a **support tool** for healthcare applications.

---

## 🚀 Project Overview

Skin diseases affect millions of people worldwide, and early diagnosis is critical.  
This project uses **Convolutional Neural Networks (CNNs)** and **transfer learning** to classify skin disease images into multiple disease categories.

The system:
- Takes a **skin image** as input
- Preprocesses and normalizes the image
- Uses a trained deep learning model to **predict the disease**
- Returns the **predicted class with confidence score**

---

## 🎯 Key Features

- 🖼️ Image-based skin disease detection  
- 🧠 Deep Learning with **EfficientNet / CNN**
- 📊 Multi-class classification
- 🔁 Retraining & fine-tuning supported
- ⚡ GPU-accelerated training (Colab / Kaggle)
- 💾 Safe model & dataset storage using Google Drive
- 🌐 API-ready for backend integration (Django / FastAPI)

---

## 🔗 Frontend Repository

👉 **React Native Frontend (Mobile App):**  
🔗 https://github.com/Onkar2104/skin_disease_frontend

The frontend communicates with this backend via REST APIs.

---

## 🛠️ Tech Stack

### 🔹 Machine Learning / AI
- Python
- TensorFlow / Keras
- NumPy
- OpenCV
- Matplotlib
- Scikit-learn

### 🔹 Training Platforms
- Google Colab (CPU / T4 GPU)

### 🔹 Deployment (Planned)
- Django REST Framework
- React Native frontend
- AWS / EC2

---

## 📂 Dataset Information

The project uses **multiple Kaggle datasets** merged and cleaned carefully.

### Datasets Used:
- HAM10000 – Skin Cancer MNIST
- ISIC 2019 Skin Lesion Dataset

### Dataset Processing:
- Removed corrupted images
- Removed duplicates
- Unified class names across datasets
- Balanced classes where possible
- Split into **Train / Validation / Test**

---

## 📦 Project Structure

```
SKIN_DISEASE/
│
├── sample_images/                # Sample images for testing predictions
│
├── skin_disease/                 # Django project root
│   │
│   ├── api/                      # API app for ML inference
│   │   ├── __pycache__/
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── ml_state.py           # Model loading & global state
│   │   ├── ml_utils.py           # Image preprocessing & prediction logic
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py               # API routes
│   │   └── views.py              # Prediction API views
│   │
│   ├── ml_models/                # Trained ML models (.keras)
│   │
│   ├── skin_disease/             # Django project settings
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── db.sqlite3                # SQLite database
│   ├── manage.py                 # Django management script
│   └── requirements.txt          # Python dependencies
│
├── venv/                         # Virtual environment (not committed)
└── .gitignore                    # Git ignored files

```

---

## 🔮 Future Enhancements

- 🔍 Increase accuracy & confidence
- 🧬 Add more disease classes
- 🌐 Deploy as REST API
- 📱 Mobile app integration
- 🧑‍⚕️ Doctor-assisted decision support
- 📊 Explainable AI (Grad-CAM)

---

## ⚠️ Disclaimer

It **does not replace professional medical diagnosis**. Always consult a certified dermatologist.

---

## 👨‍💻 Author

**Onkar Ijare**  

---
