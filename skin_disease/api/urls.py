# api/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path("predict/skin-disease/", predict_skin_disease, name="predict-skin-disease"),
]
