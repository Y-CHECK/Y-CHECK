# footprints/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from timetable.models import Timetable


@require_GET
def shared_timetables(request):
    """
    공유된 시간표 목록
    GET /api/footprints/timetables/

    쿼리 파라미터:
      - track: 관심 트랙 (예: "AI", "AI_ML", "SECURITY" ...)
      - grade: 학년 (예: "2", "3", "4")

    응답 예:
    {
      "results": [
        {
          "user": {
            "id": 3,
            "username": "testuser",
            "display_name": "testuser"
          },
          "label": "2025년 1학기",
          "year": 2025,
          "semester": 1,
          "courses": [
            {"subject": "데이터구조론", "memo": "전필"},
            ...
          ]
        },
        ...
      ]
    }

    - Timetable.is_shared = True 인 것만 포함
    - (선택) user의 관심분야 / 학년으로 필터
    - user + year + semester 기준으로 묶어서 한 카드로 내려줌
    """
    track_param = request.GET.get("track")   # 예: "AI", "AI_ML"
    grade_param = request.GET.get("grade")   # 예: "3"

    # 기본 쿼리셋: 공유 ON + UserProfile 있는 유저만
    qs = (
        Timetable.objects
        .filter(is_shared=True, user__userprofile__isnull=False)
        .select_related("user", "user__userprofile")
        .order_by("user_id", "year", "semester", "day", "period")
    )

    # ---- 관심 트랙 필터 ----
    # DB에는 "AI/머신러닝" 이런 '라벨'이 들어있으므로, 파라미터를 라벨로 매핑해준다.
    TRACK_LABEL_MAP = {
        "AI": "AI/머신러닝",
        "AI_ML": "AI/머신러닝",
        "SECURITY": "보안/네트워크",
        "SECURITY_NETWORK": "보안/네트워크",
        "GAME": "게임/미디어",
        "GAME_MEDIA": "게임/미디어",
        "EMBEDDED": "임베디드/시스템",
        "EMBEDDED_SYSTEM": "임베디드/시스템",
        "STARTUP": "창업/서비스기획",
        "STARTUP_SERVICE": "창업/서비스기획",
        "OTHER": "기타(직접입력)",
    }

    if track_param:
        # 매핑에 없으면 그대로 비교 (혹시 "AI/머신러닝" 같이 라벨이 직접 넘어오는 경우 대비)
        interest_label = TRACK_LABEL_MAP.get(track_param, track_param)
        qs = qs.filter(user__userprofile__interest=interest_label)

    # ---- 학년 필터 ----
    # grade="3" 이면 current_semester 가 "3-1", "3-2" 인 유저만
    if grade_param:
        qs = qs.filter(user__userprofile__current_semester__startswith=f"{grade_param}-")

    # ---- 그룹핑 (user, year, semester 단위 카드) ----
    grouped = {}  # key: (user_id, year, semester) → dict

    for tt in qs:
        key = (tt.user_id, tt.year, tt.semester)

        if key not in grouped:
            user = tt.user
            profile = getattr(user, "userprofile", None)

            # display_name: 실명 있으면 실명, 없으면 username
            display_name = None
            if profile and profile.real_name:
                display_name = profile.real_name
            else:
                display_name = user.username

            grouped[key] = {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "display_name": display_name,
                },
                "label": f"{tt.year}년 {tt.semester}학기",
                "year": tt.year,
                "semester": tt.semester,
                "courses": [],
            }

        grouped[key]["courses"].append(
            {
                "subject": tt.subject,
                "memo": tt.memo,
            }
        )

    results = list(grouped.values())
    return JsonResponse({"results": results})
