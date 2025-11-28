# users/login_status.py
from django.http import JsonResponse
from .models import UserProfile

def login_status(request):
    if not request.user.is_authenticated:
        return JsonResponse({"logged_in": False})

    user = request.user

    # 프로필 가져오기
    try:
        profile_obj = UserProfile.objects.get(user=user)
        profile = {
            "real_name": profile_obj.real_name,
            "student_id": profile_obj.student_id,
            "current_semester": profile_obj.current_semester,
            "major_department": profile_obj.major_department,
            "interest": profile_obj.interest,
            "interest_text": profile_obj.interest_text,
            "data_consent": profile_obj.data_consent,
        }
    except UserProfile.DoesNotExist:
        profile = None

    return JsonResponse({
        "logged_in": True,
        "username": user.username,
        "profile": profile
    })
