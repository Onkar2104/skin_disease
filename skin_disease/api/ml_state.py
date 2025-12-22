# api/ml_state.py
import os

model = None  # This ensures: Model loads once, No reload on every request, Much faster API


def get_model():
	"""Lazily load and return the ML model. Falls back to standalone `keras` if
	`tensorflow.keras` is not available.
	"""
	global model
	if model is None:
		try:
			from tensorflow.keras.models import load_model as _load_model
		except Exception:
			from keras.models import load_model as _load_model

		model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_models', 'skin_disease_final.keras')
		model_path = os.path.normpath(model_path)
		model = _load_model(model_path)

	return model
