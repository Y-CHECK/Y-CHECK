# users/logout.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout

@csrf_exempt
def logout_api(request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "POST method only"},
            status=405
        )

    # Django 세션 삭제
    logout(request)

    return JsonResponse(
        {"success": True, "message": "Logout successful"},
        status=200
    )
