import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from .models import Course


# ========================
#  DB에서 과목 목록 가져오기
# ========================
@csrf_exempt
@require_GET
def get_courses(request):
    courses = Course.objects.all().values(
        "code", "name", "credits", "category", "major_type", "is_required"
    )
    return JsonResponse(list(courses), safe=False)


# ========================
# 2022 SWE 졸업요건 규칙 정의
# ========================
GRAD_RULES_2022_SWE = {
    "meta": {"entry_year": 2022, "major": "소프트웨어학부"},
    "total_credits": 135,
    "need_second_major": True,
    "certifications": {
        "language": {"required": True, "label": "외국어인증"},
        "it_or_industry": {"required": True, "options": ["정보인증", "산업실무역량인증"]},
    },
    "level300_min_credits": 45,
    "multi_major_required_rule": {
        "type": "text_rule",
        "description": (
            "재학생 복수전공 이수 시: "
            "(1) 전공필수가 12학점 이상인 전공은 전공필수 12학점 이상 취득, "
            "(2) 전공필수가 12학점 미만인 전공은 전공필수 전체 이수."
        ),
    },
    "overlap_rules": {
        "basic_vs_explore": {
            "max_credits": 3,
            "description": "기본전공을 1전공으로 이수 시, 지정 전공탐색 3학점까지 전공학점으로 중복 인정.",
        },
        "basic_vs_deep": {
            "max_credits": 7,
            "description": "기본전공과 심화전공 공통 교과목은 최대 7학점까지 심화전공 학점으로 인정.",
        },
    },
    "liberal_arts": {
        "basic_min_credits": 22,
        "univ_required": {
            "min_credits": 5,
            "courses": [
                {"name": "SW소양영어", "area": "3영역 언어와표현", "credits": 2},
                {"name": "자바프로그래밍", "area": "10영역 정보기술", "credits": 3},
            ],
        },
        "univ_elective": {
            "min_areas": 5,
            "areas": [
                "1영역 문화예술",
                "2영역 인간과공동체",
                "3영역 언어와표현",
                "4영역 가치와윤리",
                "5영역 국가와사회",
                "6영역 지역과세계",
                "9영역 생명과환경",
            ],
        },
        "exploration": {"min_credits": 21},
    },
    "major": {
        "basic_min_credits": 36,
        "not_count_as_major": [
            {"code": "SWE2006", "name": "기초데이터구조"},
            {"code": "SWE2014", "name": "기초알고리즘"},
            {"code": "SWE2015", "name": "기초프로그래밍"},
            {"code": "SWE4025", "name": "PBL스타트업"},
            {"code": "SWE3026", "name": "융합SW-PBL"},
            {"code": "SWE3017", "name": "인턴십"},
            {"code": "SWE3027", "name": "융합SW인턴십"},
            {"code": "SWE4011", "name": "산학공동프로젝트"},
            {"code": "SWE4024", "name": "프로젝트문제해결"},
            {"code": "SWE3028", "name": "융합SW프로젝트"},
        ],
        "required_courses": [
            {"code": "SWE2001", "name": "데이터구조론", "credits": 3},
            {"code": "SWE3016", "name": "인공지능", "credits": 3},
            {"code": "SWE3017", "name": "데이터베이스", "credits": 3},
        ],
    },
    "deep_major": {
        "min_credits": 36,
        "track_min_credits": 15,
        "need_two_track_required": True,
        "allow_basic_overlap_max": 7,
    },
    "tracks": {
        "ai_bigdata": {
            "name": "AI·빅데이터 트랙",
            "required_courses": [
                {"code": "SWE3016", "name": "인공지능", "credits": 3},
                {"code": "SWE3017", "name": "데이터베이스", "credits": 3},
            ],
        },
        "ai_media": {
            "name": "AI미디어 트랙",
            "required_courses": [
                {"code": "SWE3016", "name": "인공지능", "credits": 3},
                {"code": "SWE3019", "name": "디지털신호처리", "credits": 3},
            ],
        },
        "ai_science": {
            "name": "AI계산과학 트랙",
            "required_courses": [
                {"code": "SWE3016", "name": "인공지능", "credits": 3},
                {"code": "SWE3020", "name": "수치해석과최적화", "credits": 3},
            ],
        },
        "smart_iot": {
            "name": "스마트IoT 트랙",
            "required_courses": [
                {"code": "SWE3022", "name": "임베디드시스템", "credits": 3},
                {"code": "SWE3023", "name": "컴퓨터네트워크", "credits": 3},
            ],
        },
        "security": {
            "name": "정보보안 트랙",
            "required_courses": [
                {"code": "SWE3009", "name": "암호학", "credits": 3},
                {"code": "SWE3024", "name": "정보보안", "credits": 3},
            ],
        },
    },
    "area_min_credits": {
        "liberal_basic": 22,
        "univ_required": 5,
        "exploration": 21,
        "major_basic": 36,
        "level300": 45,
    },
}


# ============================
#         계산 API
# ============================
@csrf_exempt
@require_POST
def calculate_graduation(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "잘못된 JSON 형식입니다."}, status=400)

    entry_year = int(data.get("entry_year", 0))
    major = data.get("major")
    track_key = data.get("track", "none")
    total_credits = int(data.get("total_credits", 0))
    completed_codes = set(data.get("completed_courses", []))

    credits = data.get("credits", {}) or {}
    flags = data.get("flags", {}) or {}

    liberal_basic_credits = int(credits.get("liberal_basic", 0))
    univ_required_credits = int(credits.get("univ_required", 0))
    exploration_credits = int(credits.get("exploration", 0))
    major_basic_credits = int(credits.get("major_basic", 0))
    level300_credits = int(credits.get("level300", 0))
    deep_major_credits = int(credits.get("deep_major", 0))
    track_credits = int(credits.get("track", 0))

    second_major_done = bool(flags.get("second_major_done", False))
    language_cert_ok = bool(flags.get("language_cert", False))
    it_cert_ok = bool(flags.get("it_cert", False))
    industry_cert_ok = bool(flags.get("industry_cert", False))

    if entry_year != 2022 or major != "소프트웨어학부":
        return JsonResponse(
            {"detail": "현재는 2022학번 소프트웨어학부만 지원합니다."},
            status=400,
        )

    rules = GRAD_RULES_2022_SWE

    required_courses = rules["major"]["required_courses"]
    required_total_credits = sum(c.get("credits", 0) for c in required_courses)

    completed_required = [c for c in required_courses if c["code"] in completed_codes]
    remaining_required = [c for c in required_courses if c["code"] not in completed_codes]

    earned_required_credits = sum(c.get("credits", 0) for c in completed_required)

    major_required_percentage = (
        int(earned_required_credits / required_total_credits * 100)
        if required_total_credits > 0
        else 0
    )

    track_result = None
    track_required_ok = True
    if track_key in rules["tracks"]:
        track_info = rules["tracks"][track_key]
        track_required = track_info["required_courses"]
        track_required_total = sum(c.get("credits", 0) for c in track_required)
        track_completed = [c for c in track_required if c["code"] in completed_codes]
        track_earned = sum(c.get("credits", 0) for c in track_completed)

        track_required_ok = (track_earned >= track_required_total)

        track_result = {
            "track_key": track_key,
            "track_name": track_info["name"],
            "required_credits": track_required_total,
            "earned_credits": track_earned,
            "completed": track_completed,
        }

    area_min = rules["area_min_credits"]

    conditions = {}
    conditions["total_credits"] = (total_credits >= rules["total_credits"])
    conditions["second_major"] = (not rules["need_second_major"]) or second_major_done
    conditions["language_cert"] = (not rules["certifications"]["language"]["required"]) or language_cert_ok
    conditions["it_or_industry_cert"] = (
        (not rules["certifications"]["it_or_industry"]["required"]) or (it_cert_ok or industry_cert_ok)
    )
    conditions["level300"] = (level300_credits >= rules["level300_min_credits"])
    conditions["liberal_basic"] = (liberal_basic_credits >= area_min["liberal_basic"])
    conditions["univ_required"] = (univ_required_credits >= area_min["univ_required"])
    conditions["exploration"] = (exploration_credits >= area_min["exploration"])
    conditions["major_basic"] = (major_basic_credits >= area_min["major_basic"])
    conditions["major_required_all"] = (len(remaining_required) == 0)

    deep_rules = rules["deep_major"]
    if track_key in rules["tracks"]:
        conditions["deep_major_min"] = (deep_major_credits >= deep_rules["min_credits"])
        conditions["track_min_credits"] = (track_credits >= deep_rules["track_min_credits"])
        conditions["track_required_all"] = track_required_ok
    else:
        conditions["deep_major_min"] = True
        conditions["track_min_credits"] = True
        conditions["track_required_all"] = True

    can_graduate = all(conditions.values())

    response_data = {
        "entry_year": entry_year,
        "major": major,
        "track": track_key,
        "summary": {
            "total_credits": total_credits,
            "required_total_credits": rules["total_credits"],
            "can_graduate": can_graduate,
        },
        "major_required": {
            "percentage": major_required_percentage,
            "earned_credits": earned_required_credits,
            "total_credits": required_total_credits,
            "completed": completed_required,
            "remaining": remaining_required,
        },
        "track": track_result,
        "conditions": conditions,
        "rules_meta": rules,
    }

    return JsonResponse(response_data, status=200)