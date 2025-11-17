# users/login.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
import json

@csrf_exempt
def login_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST method only"}, status=405)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JsonResponse({"success": False, "message": "username and password required"}, status=400)

    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({"success": False, "message": "Invalid credentials"}, status=401)

    login(request, user)
    return JsonResponse({"success": True, "message": "Login successful"})