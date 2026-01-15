from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    predict_skin_disease,
    ScanViewSet,
    download_scan_pdf,
    nearby_hospitals,
)

router = DefaultRouter()
router.register(r"scans", ScanViewSet, basename="scan")

urlpatterns = [
    path("predict/skin-disease/", predict_skin_disease),

    # ✅ REGISTER VIEWSET ROUTES
    path("", include(router.urls)),

    # Optional
    path("scans/<int:pk>/pdf/", download_scan_pdf),

    path("nearby-hospitals/", nearby_hospitals),

]
