import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout   # ⭐ 추가
from .models import UserProfile


@csrf_exempt
def mypage_api(request):
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({"logged_in": False}, status=401)

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
                "major_department": profile.major_department,   # ⭐ 추가
                "interest": profile.interest,
                "interest_text": profile.interest_text,
                "data_consent": profile.data_consent,
            }

        return JsonResponse(
            {
                "logged_in": True,
                "username": user.username,
                "profile": profile_data,
            }
        )

    # --- GET: 내 정보 조회 ---
    if request.method == "GET":
        return build_profile_response()

    # --- POST: 프로필 수정 / 로그아웃 ---
    if request.method == "POST":
        # 1) JSON 파싱
        try:
            data = json.loads(request.body.decode() or "{}")
        except Exception:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

        # 2) 로그아웃 요청 처리
        #    프론트에서 { "action": "logout" } 형태로 보내면 됨
        if data.get("action") == "logout":
            logout(request)  # 세션 삭제
            return JsonResponse({"success": True, "message": "Logged out"})

        # 3) 그 외에는 프로필 업데이트
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user)

        if "real_name" in data:
            profile.real_name = data["real_name"]

        if "student_id" in data:
            profile.student_id = data["student_id"]

        if "current_semester" in data:
            profile.current_semester = data["current_semester"]

        if "major_department" in data:
            profile.major_department = data["major_department"]

        if "interest" in data:
            profile.interest = data["interest"]

        if "interest_text" in data:
            profile.interest_text = data["interest_text"]

        if "data_consent" in data:
            profile.data_consent = bool(data["data_consent"])

        profile.save()

        return JsonResponse({"success": True, "message": "Profile updated"})

    return JsonResponse({"success": False, "message": "GET/POST only"}, status=405)
