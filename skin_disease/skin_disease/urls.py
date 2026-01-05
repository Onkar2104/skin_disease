from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from api.views import ScanViewSet, download_scan_pdf

router = DefaultRouter()
router.register("scans", ScanViewSet, basename="scans")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("api.urls")),
    path("api/", include(router.urls)),   # ✅ THIS WAS MISSING
    path("api/scans/<int:pk>/pdf/", download_scan_pdf),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
