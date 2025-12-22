# api/apps.py

from django.apps import AppConfig
from django.conf import settings
import tensorflow as tf
import os

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from . import ml_state

        model_path = os.path.join(
            settings.BASE_DIR,
            "ml_models",
            "skin_disease_final.keras"
        )

        ml_state.model = tf.keras.models.load_model(model_path)
        print("✅ Skin disease model loaded successfully")
