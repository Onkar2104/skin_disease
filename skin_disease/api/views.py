from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import ScanSerializer
from .models import Scan
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .pdf import generate_scan_pdf

# Local ML helpers
from . import ml_state, ml_utils

@csrf_exempt
def predict_skin_disease(request):

    # ✅ Allow preflight
    if request.method == "OPTIONS":
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "*"
        return response

    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    # print("FILES:", request.FILES)
    # print("POST:", request.POST)

    image = request.FILES.get("image")
    if not image:
        return JsonResponse({
            "error": "Image not provided",
            "received_files": list(request.FILES.keys())
        }, status=400)

    # Load model (lazily) and run prediction
    try:
        model = ml_state.get_model()
    except Exception as exc:
        return JsonResponse({"error": "Failed to load model", "details": str(exc)}, status=500)

    try:
        result = ml_utils.predict_skin_disease_from_file(model, image)
    except Exception as exc:
        return JsonResponse({"error": "Prediction failed", "details": str(exc)}, status=500)

    # views.py (FIXED)

    response = {
        "label": result["predicted_label"],           # e.g. "nv"
        "diagnosis": result["predicted_disease"],     # e.g. "Melanocytic Nevi"
        "confidence": result["confidence_percent"],   # e.g. 94
        "severity": (
            "High" if result["predicted_label"] in ["mel", "bcc", "scc"]
            else "Moderate" if result["predicted_label"] == "akiec"
            else "Low"
        ),
        "advice": result["explanation"],
        "isSafe": result["predicted_label"] not in ["mel", "bcc", "scc"],
    }

    return JsonResponse(response)

    
class ScanViewSet(viewsets.ModelViewSet):
    serializer_class = ScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Scan.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_scan_pdf(request, pk):
    scan = get_object_or_404(Scan, pk=pk, user=request.user)
    return generate_scan_pdf(scan)

