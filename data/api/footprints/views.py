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
      - major_required_only: "true" 면 전공 필수 그룹만
      - major_elective_only: "true" 면 전공 선택 그룹만

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
            {"subject": "데이터구조론", "memo": "전공"},
            ...
          ]
        },
        ...
      ]
    }
    """

    track_param = request.GET.get("track")   # 예: "AI", "AI_ML"
    grade_param = request.GET.get("grade")   # 예: "3"

    # 🔹 전공 필수 / 전공 선택 필터 파라미터
    major_required_only = request.GET.get("major_required_only") == "true"
    major_elective_only = request.GET.get("major_elective_only") == "true"

    # 기본 쿼리셋: 공유 ON
    qs = (
        Timetable.objects
        .filter(is_shared=True)
        .select_related("user", "user__userprofile")
        .order_by("user_id", "year", "semester", "day", "period")
    )

    # 🔹 전필/전선 매핑 규칙 (Timetable.memo 기준)
    #   - 전공 필수 그룹: "전공필수", "필수"
    #   - 전공 선택 그룹: "선택", "전공", "심화"
    required_memos = ["전공필수", "필수"]
    elective_memos = ["선택", "전공", "심화"]

    #   - 둘 다 false → 전체
    #   - 둘 다 true  → 전체(필터 X)
    #   - 한쪽만 true → 해당 그룹만
    if major_required_only and not major_elective_only:
        qs = qs.filter(memo__in=required_memos)
    elif major_elective_only and not major_required_only:
        qs = qs.filter(memo__in=elective_memos)

    # -------------------------------
    #  관심 트랙 필터
    #   - UserProfile.interest 에 저장된 '라벨'과 매칭
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
        # 매핑에 없으면 그냥 그대로 사용
        interest_code = TRACK_LABEL_MAP.get(track_param, track_param)
        qs = qs.filter(user__userprofile__interest=interest_code)

    # -------------------------------
    #  학년 필터
    #   - UserProfile.current_semester 가 "3-1", "3-2" 이런 형식이라고 가정
    #   - grade="3" → "3-" 로 시작하는 값만
    # -------------------------------
    if grade_param:
        qs = qs.filter(
            user__userprofile__current_semester__startswith=f"{grade_param}-"
        )

    # -------------------------------
    #  user + year + semester 단위로 그룹핑해서 카드 만들기
    # -------------------------------
    grouped = {}  # key: (user_id, year, semester) → dict

    for tt in qs:
        key = (tt.user_id, tt.year, tt.semester)

        if key not in grouped:
            user = tt.user
            profile = getattr(user, "userprofile", None)

            # display_name: 프로필 실명 있으면 그거, 없으면 username
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
                "memo": tt.memo,
            }
        )

    results = list(grouped.values())
    return JsonResponse({"results": results})
