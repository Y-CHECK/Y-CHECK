# users/mypage.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import UserProfile  # 훈짱이 만든 프로필 모델


@csrf_exempt
def mypage_api(request):
    """
    마이페이지 데이터 제공 + 로그인 여부 체크
    - 로그인 안 되어 있으면 401
    - 로그인 되어 있으면 User + UserProfile 정보 반환
    """
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({"logged_in": False}, status=401)

    try:
        profile = user.userprofile  # UserProfile에서 user = OneToOneField(...)
    except UserProfile.DoesNotExist:
        profile = None

    profile_data = None
    if profile is not None:
        profile_data = {
            "student_id": profile.student_id,
            "real_name": profile.real_name,
            "current_semester": profile.current_semester,
            "interest": profile.interest,
            "interest_text": profile.interest_text,
            "data_consent": profile.data_consent,
        }

    return JsonResponse(
        {
            "logged_in": True,
            "username": user.username,
            "email": user.email,
            "profile": profile_data,
        }
    )