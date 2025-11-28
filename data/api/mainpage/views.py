# data/api/mainpage/views.py
import json
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET


# 트랙 key → 화면에 보여줄 한글 이름
TRACK_LABELS = {
    "ai_bigdata": "AI·빅데이터",
    "ai_media": "AI·미디어",
    "ai_science": "AI·사이언스",
    "smart_iot": "스마트 IoT",
    "security": "보안",
}


@require_GET
def track_recommend(request):
    """
    메인 페이지 트랙별 과목 추천 API
    - 로그인한 사용자의 UserProfile.interest / interest_text 를 보고
      적절한 트랙(security, ai_bigdata, ...)을 선택
    - courses.json 의 해당 트랙 과목 목록을 내려준다.
    """

    # 0) 미로그인인 경우
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({
            "has_track": False,
            "message": "로그인이 필요합니다.",
            "courses": [],
        }, status=401)

    # 1) courses.json 읽기
    json_path = os.path.join(settings.BASE_DIR, "courses.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except FileNotFoundError:
        return JsonResponse({
            "has_track": False,
            "message": "과목 정보 파일(courses.json)을 찾을 수 없습니다.",
            "courses": [],
        }, status=500)

    track_dict = json_data.get("트랙", {})

    # 2) 유저 프로필에서 관심 전공/분야 읽기
    profile = getattr(user, "userprofile", None)
    if profile is None:
        return JsonResponse({
            "has_track": False,
            "message": "사용자 프로필 정보가 없습니다.",
            "courses": [],
        })

    # DB에 저장된 값 (예: 'security' / '보안' / 'AI·빅데이터' 등)
    interest_raw = (profile.interest or "").strip()
    if not interest_raw and getattr(profile, "interest_text", None):
        interest_raw = profile.interest_text.strip()

    if not interest_raw:
        return JsonResponse({
            "has_track": False,
            "message": "관심 전공/분야가 설정되어 있지 않습니다.",
            "courses": [],
        })

    # 3) 문자열을 기준으로 트랙 key 결정
    track_key = None

    # 우선, DB에 이미 key 값으로 저장돼 있는 경우
    if interest_raw in track_dict:
        track_key = interest_raw
    else:
        # 공백 제거 + 소문자
        cleaned = interest_raw.replace(" ", "").lower()

        # 핵심 키워드 기준 매핑
        if "보안" in interest_raw:
            track_key = "security"
        elif "빅데이터" in interest_raw or "bigdata" in cleaned:
            track_key = "ai_bigdata"
        elif "미디어" in interest_raw:
            track_key = "ai_media"
        elif "사이언스" in interest_raw or "science" in cleaned:
            track_key = "ai_science"
        elif "iot" in cleaned:
            track_key = "smart_iot"
        elif cleaned in {"security", "ai_bigdata", "ai_media", "ai_science", "smart_iot"}:
            track_key = cleaned

    # 4) 그래도 못 찾으면 추천 불가
    if not track_key or track_key not in track_dict:
        return JsonResponse({
            "has_track": False,
            "message": f"'{interest_raw}'에 해당하는 트랙을 찾을 수 없습니다.",
            "courses": [],
        })

    track_courses = track_dict.get(track_key, [])

    # 5) 응답용 과목 리스트 (code, name, credits, type 등)
    courses = []
    for c in track_courses:
        courses.append({
            "code": c.get("code"),
            "name": c.get("name"),
            "credits": c.get("credits", 0),
            "type": c.get("type", ""),  # 전필/전선/트랙전필 등
        })

    track_name = TRACK_LABELS.get(track_key, track_key)

    return JsonResponse({
        "has_track": True,
        "track_key": track_key,
        "track_name": track_name,
        "interest_raw": interest_raw,   # 디버깅용으로 내려줌
        "courses": courses,
    })
