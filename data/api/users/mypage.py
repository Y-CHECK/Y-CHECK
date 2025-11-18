# api/users/mypage.py
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import UserProfile


@csrf_exempt
def mypage_api(request):
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({"logged_in": False}, status=401)

    # --- 프로필 가져오기 공통 함수 ---
    def build_profile_response():
        try:
            profile = user.userprofile
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

    # --- GET: 조회 ---
    if request.method == "GET":
        return build_profile_response()

    # --- POST: 수정 ---
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode())
        except Exception:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

        # 프로필이 없으면 생성
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user)

        # 아이디(username)는 수정하지 않음

        real_name = data.get("real_name")
        student_id = data.get("student_id")
        interest = data.get("interest")
        data_consent = data.get("data_consent")

        if real_name is not None:
            profile.real_name = real_name
        if student_id is not None:
            profile.student_id = student_id
        if interest is not None:
            profile.interest = interest
        if data_consent is not None:
            profile.data_consent = bool(data_consent)

        profile.save()

        return JsonResponse({"success": True, "message": "Profile updated"})

    # 그 외 메서드
    return JsonResponse({"success": False, "message": "GET/POST only"}, status=405)