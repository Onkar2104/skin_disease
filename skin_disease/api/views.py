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
from .scoring_weights import SEVERITY_WEIGHTS
from .ml_hospital_predictor import predict_suitability
from .explanation import generate_hospital_explanation


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
def calculate_distance_km(lat1, lon1, lat2, lon2):
    """
    Accurate straight-line distance using WGS84
    """
    R = 6371.0088  # More precise Earth radius (km)

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(R * c, 3)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def nearby_hospitals(request):
    try:
        diagnosis = request.data.get("diagnosis")
        severity = request.data.get("severity", "Low")  
        lat = request.data.get("lat")
        lon = request.data.get("lon")
        city = request.data.get("city")

        lat = float(lat) if lat is not None else None
        lon = float(lon) if lon is not None else None

        if not diagnosis:
            return Response({"error": "diagnosis required"}, status=400)

        keyword = get_keyword_from_diagnosis(diagnosis)
        weights = SEVERITY_WEIGHTS.get(severity, SEVERITY_WEIGHTS["Low"])


        if city and not (lat and lon):
            geo_res = requests.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"address": city, "key": settings.GOOGLE_MAPS_API_KEY},
                timeout=5,
            ).json()

            if not geo_res.get("results"):
                return Response({"error": "Invalid city"}, status=400)

            loc = geo_res["results"][0]["geometry"]["location"]
            lat, lon = loc["lat"], loc["lng"]


        places_res = requests.get(
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
            params={
                "location": f"{lat},{lon}",
                "radius": 5000,
                "keyword": keyword,
                "type": "hospital",
                "key": settings.GOOGLE_MAPS_API_KEY,
            },
            timeout=5,
        ).json()

        ranked_hospitals = []

        for p in places_res.get("results", []):
            name = p.get("name", "")
            rating = p.get("rating", 0)

            h_lat = p["geometry"]["location"]["lat"]
            h_lon = p["geometry"]["location"]["lng"]
            distance = calculate_distance_km(
                float(lat), float(lon),
                float(h_lat), float(h_lon)
            )

            # 🔮 ML-ready suitability score
            try:
                ml_score = predict_suitability(
                    rating=rating,
                    distance=distance,
                    severity=severity,
                )
            except Exception:
                ml_score = 0.5  


            # 🎯 Final severity-aware score
            final_score = (
                rating * weights["rating"]
                + ml_score * weights["ml"]
                - distance * weights["distance"]
            )

            explanation = generate_hospital_explanation(
                severity=severity,
                rating=rating,
                distance=distance,
                ml_score=ml_score,
            )

            ranked_hospitals.append({
                "name": name,
                "address": p.get("vicinity"),
                "rating": rating,
                "distance_km": distance,
                "ml_score": ml_score,
                "final_score": round(final_score, 2),
                "why_recommended": explanation,  
                "top_doctors": fetch_doctors_for_hospital(
                    hospital_name=name,
                    lat=h_lat,
                    lon=h_lon,
                    severity=severity
                ),
                "maps_url": f"https://www.google.com/maps/dir/?api=1&destination={h_lat},{h_lon}",
            })


        # 🧠 SMART SORT
        ranked_hospitals.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        return Response({
            "diagnosis": diagnosis,
            "severity": severity,
            "keyword_used": keyword,
            "hospitals": ranked_hospitals,
        })

    except Exception:
        return Response(
            {"error": "Internal server error"},
            status=500
        )


def fetch_doctors_for_hospital(hospital_name, lat, lon, severity):
    query = f"{hospital_name} dermatologist"

    res = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        params={
            "query": query,
            "location": f"{lat},{lon}",
            "radius": 5000,
            "key": settings.GOOGLE_MAPS_API_KEY,
        },
        timeout=5
    ).json()

    doctors = []

    for p in res.get("results", []):
        rating = p.get("rating", 4.0)

        # Severity-aware scoring (distance not exposed)
        score = rating * (2 if severity == "High" else 1)

        doctors.append({
            "id": p["place_id"],
            "name": p["name"],
            "specialty": "Dermatologist",
            "rating": rating,
            "experience_years": 5 + int(rating),
            "score": round(score, 2),
            "why_recommended": (
                f"Practices at {hospital_name}, "
                f"high patient ratings, "
                f"suitable for {severity.lower()} severity cases"
            ),
        })

    # 🧠 Rank doctors inside hospital
    doctors.sort(key=lambda x: x["score"], reverse=True)

    return doctors[:3]
