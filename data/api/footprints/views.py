from django.http import JsonResponse
from django.views.decorators.http import require_GET

# ====== 임시 더미 데이터 ======
# 나중에 DB 붙이면 여기 부분을 ORM 쿼리로 교체하면 됨.
SENIORS = [
    {
        "id": 1,
        "display_name": "익명선배A",
        "track": "AI/머신러닝",
        # grade -> semesters
        "records": {
            3: [
                {
                    "label": "3학년 1학기",
                    "year": 2024,
                    "term": "봄",
                    "courses": [
                        {"code": "SWE2010", "title": "데이터구조론", "category": "전필"},
                        {"code": "SWE3005", "title": "인공지능개론", "category": "전선"},
                    ],
                },
                {
                    "label": "3학년 2학기",
                    "year": 2024,
                    "term": "가을",
                    "courses": [
                        {"code": "SWE3007", "title": "운영체제", "category": "전필"},
                    ],
                },
            ]
        },
    },
    {
        "id": 2,
        "display_name": "익명선배B",
        "track": "보안",
        "records": {
            3: [
                {
                    "label": "3학년 1학기",
                    "year": 2024,
                    "term": "봄",
                    "courses": [
                        {"code": "SWE3020", "title": "정보보호개론", "category": "전필"},
                        {"code": "SWE3021", "title": "네트워크보안", "category": "전선"},
                    ],
                }
            ]
        },
    },
]


def _get_tracks():
    return sorted({s["track"] for s in SENIORS})


@require_GET
def filters(request):
    """
    관심 트랙 / 선택 가능한 학년 목록 내려주기
    GET /api/footprints/filters/
    """
    # 더미: 1~4학년 고정
    grades = [1, 2, 3, 4]

    return JsonResponse(
        {
            "tracks": _get_tracks(),
            "grades": grades,
        }
    )


@require_GET
def seniors(request):
    """
    선택된 트랙+학년에 맞는 선배 목록
    GET /api/footprints/seniors/?track=AI/머신러닝&grade=3
    """
    track = request.GET.get("track")
    grade = request.GET.get("grade")
    try:
        grade = int(grade) if grade is not None else None
    except ValueError:
        grade = None

    results = []
    for s in SENIORS:
        if track and s["track"] != track:
            continue
        if grade is not None and grade not in s["records"]:
            # 해당 학년에 이수 기록이 없는 선배는 제외
            continue
        results.append(
            {
                "id": s["id"],
                "display_name": s["display_name"],
                "track": s["track"],
            }
        )

    return JsonResponse({"results": results})


@require_GET
def senior_records(request, senior_id: int):
    """
    특정 선배의 특정 학년 이수 기록
    GET /api/footprints/seniors/1/records/?grade=3
    """
    grade = request.GET.get("grade")
    try:
        grade = int(grade)
    except (TypeError, ValueError):
        return JsonResponse({"detail": "grade 쿼리 파라미터가 필요합니다."}, status=400)

    senior = next((s for s in SENIORS if s["id"] == senior_id), None)
    if not senior:
        return JsonResponse({"detail": "선배를 찾을 수 없습니다."}, status=404)

    semesters = senior["records"].get(grade, [])

    return JsonResponse(
        {
            "senior": {
                "id": senior["id"],
                "display_name": senior["display_name"],
                "track": senior["track"],
            },
            "grade": grade,
            "semesters": semesters,
        }
    )
