import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import Course, TakenCourse
from users.models import UserProfile


# =======================================
#   1) 전체 과목 목록 API
# =======================================
@csrf_exempt
@require_GET
def get_courses(request):
    courses = Course.objects.all().values(
        "code",
        "name",
        "credits",
        "category",
        "major_type",
        "is_required",
        "level",
        "ge_area",
    )
    return JsonResponse(
        list(courses),
        safe=False,
        json_dumps_params={"ensure_ascii": False},
    )


# =======================================
#   2) 로그인한 유저의 이수 과목 목록 조회 API
# =======================================
@login_required
@require_GET
def get_taken_courses(request):
    user = request.user
    completed = TakenCourse.objects.filter(user=user).select_related("course")

    data = []
    for item in completed:
        course = item.course
        data.append({
            "code": course.code,
            "name": course.name,
            "credits": course.credits,
            "category": course.category,
            "major_type": course.major_type,
            "ge_area": course.ge_area,
            "year": item.year,
            "semester": item.semester,
        })

    return JsonResponse(
        data, safe=False, json_dumps_params={"ensure_ascii": False}
    )


# =======================================
#   3) 학점 요약 API
# =======================================
@login_required
@require_GET
def get_credit_summary(request):
    user = request.user
    completed = TakenCourse.objects.filter(user=user).select_related("course")

    summary = {
        "total_credits": 0,
        "GE_BASIC": 0,
        "GE_UNIV_REQUIRED": 0,
        "GE_UNIV_ELECTIVE": 0,
        "EXPLORATION": 0,
        "MAJOR_BASIC": 0,
        "MAJOR_DEEP": 0,
        "level300": 0,
    }

    for item in completed:
        course = item.course
        summary["total_credits"] += course.credits

        if course.category in summary:
            summary[course.category] += course.credits

        if course.level >= 300:
            summary["level300"] += course.credits

    return JsonResponse(summary, json_dumps_params={"ensure_ascii": False})


# =======================================
#   4) 졸업요건 규칙 (2022 SWE)
# =======================================
GRAD_RULES_2022_SWE = {
    "meta": {"entry_year": 2022, "major": "소프트웨어학부"},

    "total_credits": 135,
    "need_second_major": True,

    "certifications": {
        "language": {"required": True},
        "it_or_industry": {"required": True},
    },

    "level300_min_credits": 45,

    "area_min_credits": {
        "liberal_basic": 22,
        "univ_required": 5,
        "exploration": 21,
        "major_basic": 36,
        "level300": 45,
    },

    "major": {
        "required_courses": [
            {"code": "SWE2001", "name": "데이터구조론", "credits": 3},
            {"code": "SWE3016", "name": "인공지능", "credits": 3},
            {"code": "SWE3017", "name": "데이터베이스", "credits": 3},
        ],
    },

    "tracks": {
        "ai_bigdata": {
            "name": "AI·빅데이터",
            "required_courses": [
                {"code": "SWE3016", "name": "인공지능", "credits": 3},
                {"code": "SWE3017", "name": "데이터베이스", "credits": 3},
            ],
        },
        "security": {
            "name": "정보보안",
            "required_courses": [
                {"code": "SWE3009", "name": "암호학", "credits": 3},
                {"code": "SWE3024", "name": "정보보안", "credits": 3},
            ],
        },
    },
}


# =======================================
#   5) 졸업요건 계산 API
# =======================================
@csrf_exempt
@require_POST
def calculate_graduation(request):

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "잘못된 JSON입니다."}, status=400)

    entry_year = int(data.get("entry_year", 0))
    major = data.get("major")
    track_key = data.get("track", "none")
    total_credits = int(data.get("total_credits", 0))
    completed_codes = set(data.get("completed_courses", []))

    credits = data.get("credits", {}) or {}
    flags = data.get("flags", {}) or {}

    liberal_basic = int(credits.get("liberal_basic", 0))
    univ_required = int(credits.get("univ_required", 0))
    exploration = int(credits.get("exploration", 0))
    major_basic = int(credits.get("major_basic", 0))
    level300 = int(credits.get("level300", 0))

    second_major_done = bool(flags.get("second_major_done", False))
    language_cert = bool(flags.get("language_cert", False))
    it_cert = bool(flags.get("it_cert", False))
    industry_cert = bool(flags.get("industry_cert", False))

    rules = GRAD_RULES_2022_SWE

    required_courses = rules["major"]["required_courses"]
    required_total = sum(c["credits"] for c in required_courses)

    completed_required = [c for c in required_courses if c["code"] in completed_codes]
    remaining_required = [c for c in required_courses if c["code"] not in completed_codes]

    earned_required = sum(c["credits"] for c in completed_required)

    track_result = None
    if track_key in rules["tracks"]:
        t = rules["tracks"][track_key]
        track_required = t["required_courses"]
        track_total = sum(c["credits"] for c in track_required)
        track_completed = [c for c in track_required if c["code"] in completed_codes]
        track_earned = sum(c["credits"] for c in track_completed)

        track_result = {
            "track_name": t["name"],
            "required_credits": track_total,
            "earned_credits": track_earned,
            "completed": track_completed,
        }

    area = rules["area_min_credits"]

    conditions = {
        "total_credits": total_credits >= rules["total_credits"],
        "second_major": (not rules["need_second_major"]) or second_major_done,
        "language_cert": (not rules["certifications"]["language"]["required"]) or language_cert,
        "it_or_industry_cert": (not rules["certifications"]["it_or_industry"]["required"])
                                or (it_cert or industry_cert),
        "level300": level300 >= area["level300"],
        "liberal_basic": liberal_basic >= area["liberal_basic"],
        "univ_required": univ_required >= area["univ_required"],
        "exploration": exploration >= area["exploration"],
        "major_basic": major_basic >= area["major_basic"],
        "major_required_all": len(remaining_required) == 0,
    }

    return JsonResponse({
        "summary": {
            "total_credits": total_credits,
            "required_total_credits": rules["total_credits"],
            "can_graduate": all(conditions.values()),
        },
        "major_required": {
            "earned": earned_required,
            "required": required_total,
            "completed": completed_required,
            "remaining": remaining_required,
        },
        "track": track_result,
        "conditions": conditions,
    })


# =======================================
#   6) [NEW] 계산기에서 과목 체크 → TakenCourse 저장
# =======================================
@csrf_exempt
@login_required
@require_POST
def save_taken_courses(request):
    user = request.user

    try:
        data = json.loads(request.body.decode("utf-8"))
        codes = data.get("completed_courses", [])
    except:
        return JsonResponse({"error": "invalid body"}, status=400)

    # 기존 데이터 삭제
    TakenCourse.objects.filter(user=user).delete()

    # 다시 저장
    for code in codes:
        try:
            course = Course.objects.get(code=code)
            TakenCourse.objects.create(
                user=user,
                course=course,
                year=2024,         # 기본값 (나중에 선택 가능하도록 확장)
                semester="2-1",    # 기본값
                grade="A+"
            )
        except Course.DoesNotExist:
            pass

    return JsonResponse({"status": "success", "saved": len(codes)})
