from django.http import JsonResponse
from django.views.decorators.http import require_GET

from timetable.models import Timetable


def _normalize_memo(raw_memo: str) -> str:
    """
    시간표에 저장된 memo 값을 프론트에서 쓰기 좋게 정리한다.

    지금은 fixture(timetable_courses.json)에서 이미
    '필수' / '선택' / '교양' 으로 통일해서 넣으므로

      - 앞뒤 공백만 제거해서 그대로 돌려준다.

    (혹시 나중에 DB에 '전필', '전선' 같은 값이 섞여 들어오면
     여기서만 매핑 추가해 주면 됨.)
    """
    if not raw_memo:
        return ""
    return raw_memo.strip()


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
            "display_name": "홍길동"
          },
          "label": "2025년 1학기",
          "year": 2025,
          "semester": 1,
          "courses": [
            {"subject": "데이터구조론", "memo": "필수"},
            {"subject": "글쓰기", "memo": "교양"},
            ...
          ]
        },
        ...
      ]
    }
    """

    track_param = request.GET.get("track")   # 예: "AI", "AI_ML"
    grade_param = request.GET.get("grade")   # 예: "3"

    # 기본 쿼리셋: 공유 ON
    qs = (
        Timetable.objects
        .filter(is_shared=True)
        .select_related("user", "user__userprofile")
        .order_by("user_id", "year", "semester", "day", "period")
    )

    # -------------------------------
    #  관심 트랙 필터
    # -------------------------------
    TRACK_LABEL_MAP = {
        # 버튼: 실제 DB에 저장된 코드
        "AI": "AI_ML",
        "AI_ML": "AI_ML",

        "SECURITY": "SECURITY_NETWORK",
        "SECURITY_NETWORK": "SECURITY_NETWORK",

        "GAME": "GAME_MEDIA",
        "GAME_MEDIA": "GAME_MEDIA",

        "EMBEDDED": "EMBEDDED_SYSTEM",
        "EMBEDDED_SYSTEM": "EMBEDDED_SYSTEM",

        "STARTUP": "STARTUP_SERVICE",
        "STARTUP_SERVICE": "STARTUP_SERVICE",

        "OTHER": "OTHER",
    }

    if track_param:
        interest_code = TRACK_LABEL_MAP.get(track_param, track_param)
        qs = qs.filter(user__userprofile__interest=interest_code)

    # -------------------------------
    #  학년 필터
    #   - UserProfile.current_semester: "3-1", "3-2" 형식
    #   - grade="3" → "3-" 로 시작
    # -------------------------------
    if grade_param:
        qs = qs.filter(
            user__userprofile__current_semester__startswith=f"{grade_param}-"
        )

    # -------------------------------
    #  user + year + semester 단위로 그룹핑
    # -------------------------------
    grouped = {}  # key: (user_id, year, semester) → dict

    for tt in qs:
        key = (tt.user_id, tt.year, tt.semester)

        if key not in grouped:
            user = tt.user
            profile = getattr(user, "userprofile", None)

            if profile and getattr(profile, "real_name", None):
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
                "memo": _normalize_memo(tt.memo),
            }
        )

    results = list(grouped.values())
    return JsonResponse({"results": results})
