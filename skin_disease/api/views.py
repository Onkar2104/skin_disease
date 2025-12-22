from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

    print("FILES:", request.FILES)
    print("POST:", request.POST)

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

    response = JsonResponse(result)
    response["Access-Control-Allow-Origin"] = "*"
    return response
