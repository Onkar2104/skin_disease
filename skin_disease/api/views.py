from math import radians, sin, cos, sqrt, atan2
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .hospital_keywords import get_keyword_from_diagnosis
from django.conf import settings
from .serializers import ScanSerializer
from .models import Scan
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .pdf import generate_scan_pdf
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

    try:
        model = ml_state.get_model()
    except Exception as exc:
        return JsonResponse({"error": "Failed to load model", "details": str(exc)}, status=500)

    try:
        result = ml_utils.predict_skin_disease_from_file(model, image)
    except Exception as exc:
        return JsonResponse({"error": "Prediction failed", "details": str(exc)}, status=500)


    response = {
        "label": result["predicted_label"],           
        "diagnosis": result["predicted_disease"],     
        "confidence": result["confidence_percent"],   
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
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Scan.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_scan_pdf(request, pk):
    scan = get_object_or_404(Scan, pk=pk, user=request.user)
    return generate_scan_pdf(scan)


# hospital recommandation system
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def nearby_hospitals(request):
    try:
        diagnosis = request.data.get("diagnosis")
        lat = request.data.get("lat")
        lon = request.data.get("lon")
        city = request.data.get("city")

        if not diagnosis:
            return Response({"error": "diagnosis required"}, status=400)

        keyword = get_keyword_from_diagnosis(diagnosis)

        if city and not (lat and lon):
            try:
                geo_res = requests.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params={"address": city, "key": settings.GOOGLE_MAPS_API_KEY},
                    timeout=5,
                ).json()
            except requests.exceptions.RequestException:
                return Response(
                    {"error": "Geocoding service unavailable"},
                    status=503
                )

            if not geo_res.get("results"):
                return Response({"error": "Invalid city"}, status=400)

            loc = geo_res["results"][0]["geometry"]["location"]
            lat, lon = loc["lat"], loc["lng"]

        try:
            places_res = requests.get(
                "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
                params={
                    "location": f"{lat},{lon}",
                    "radius": 5000,
                    "keyword": keyword,
                    "type": "hospital",
                    "key": settings.GOOGLE_MAPS_API_KEY
                },
                timeout=5,
            ).json()
        except requests.exceptions.RequestException:
            return Response(
                {"error": "Places service unavailable"},
                status=503
            )

        hospitals = []
        for p in places_res.get("results", []):
            h_lat = p["geometry"]["location"]["lat"]
            h_lon = p["geometry"]["location"]["lng"]

            hospitals.append({
                "name": p.get("name"),
                "address": p.get("vicinity"),
                "rating": p.get("rating", 0),
                "distance_km": calculate_distance(lat, lon, h_lat, h_lon),
                "maps_url": f"https://www.google.com/maps/dir/?api=1&destination={h_lat},{h_lon}"
            })

        return Response({
            "diagnosis": diagnosis,
            "keyword_used": keyword,
            "hospitals": hospitals
        })

    except Exception as e:
        return Response(
            {"error": "Internal server error"},
            status=500
        )
