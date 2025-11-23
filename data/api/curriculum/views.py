# curriculum/views.py
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

"""
2022학번 소프트웨어학부 졸업요건 정의 + 계산 API
훈짱이 정리해준 내용을 그대로 Python 딕셔너리로 옮긴 것.
"""

GRAD_RULES_2022_SWE = {
    "meta": {
        "entry_year": 2022,
        "major": "소프트웨어학부",
    },

    # 1. 기본 졸업요건
    "total_credits": 135,          # 총 이수 학점
    "need_second_major": True,     # 2개 이상의 전공 필수

    "certifications": {
        "language": {              # 외국어인증 (필수)
            "required": True,
            "label": "외국어인증",
        },
        "it_or_industry": {        # 정보인증 or 산업실무역량인증 (택1)
            "required": True,
            "options": ["정보인증", "산업실무역량인증"],
        },
    },

    # 2. 추가 졸업 요건
    "level300_min_credits": 45,    # 3000단위 이상(전공+타전공 포함) 45학점 이상

    # 복수전공 전공필수 이수 규칙 (정성적 규칙 – 계산 참고용)
    "multi_major_required_rule": {
        "type": "text_rule",
        "description": (
            "재학생 복수전공 이수 시: "
            "(1) 전공필수가 12학점 이상인 전공은 전공필수 12학점 이상 취득, "
            "(2) 전공필수가 12학점 미만인 전공은 전공필수 전체 이수."
        ),
    },

    # 전공 중복 인정 규정 (총졸업학점에는 중복 불가)
    "overlap_rules": {
        "basic_vs_explore": {
            "max_credits": 3,
            "description": "기본전공을 1전공으로 이수 시, 지정 전공탐색 3학점까지 전공학점으로 중복 인정 (단, 총졸업학점에는 중복 불가).",
        },
        "basic_vs_deep": {
            "max_credits": 7,
            "description": "기본전공과 심화전공 공통 교과목은 최대 7학점까지 심화전공 학점으로 중복 인정 (총졸업학점에는 중복 불가).",
        },
    },

    # 3. 교양 이수 요건
    "liberal_arts": {
        # 3-1. 교양기초
        "basic_min_credits": 22,   # 채플·글쓰기·영어·리더십·컴퓨팅사고·경력개발 등 포함

        # 3-2. 대학교양 필수 (5학점)
        "univ_required": {
            "min_credits": 5,
            "courses": [
                {
                    "name": "SW소양영어",
                    "area": "3영역 언어와표현",
                    "credits": 2,
                },
                {
                    "name": "자바프로그래밍",
                    "area": "10영역 정보기술",
                    "credits": 3,
                },
            ],
        },

        # 3-3. 대학교양 선택이수
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

        # 3-4. 전공탐색
        "exploration": {
            "min_credits": 21,
            "note": "미분적분학, 공업수학, 물리학, 컴퓨터프로그래밍 등 지정 과목 중에서 21학점.",
        },
    },

    # 4. 전공 (소프트웨어 기본전공)
    "major": {
        # 기본전공 SW전공 최소 학점 (훈짱 정리 요약 기준)
        "basic_min_credits": 36,

        # 기본전공으로 인정되지 않는 과목들
        "not_count_as_major": [
            {"code": "SWE2006", "name": "기초데이터구조"},
            {"code": "SWE2014", "name": "기초알고리즘"},
            {"code": "SWE2015", "name": "기초프로그래밍"},
            {"code": "SWE4025", "name": "PBL스타트업"},
            {"code": "SWE3026", "name": "융합SW-PBL"},
            {"code": "SWE3017", "name": "인턴십", "credits": 3},
            {"code": "SWE3027", "name": "융합SW인턴십"},
            {"code": "SWE4011", "name": "산학공동프로젝트"},
            {"code": "SWE4024", "name": "프로젝트문제해결"},
            {"code": "SWE3028", "name": "융합SW프로젝트"},
        ],

        # ★ 전공필수 과목 리스트 (예시)
        #   → 실제 전필표 보고 과목/코드/학점 더 채우면 됨
        "required_courses": [
            {"code": "SWE2001", "name": "데이터구조론", "credits": 3},
            # {"code": "SWE2XXX", "name": "알고리즘", "credits": 3},
            # TODO: 22학번 소프트웨어학부 전공필수 전체 추가
        ],
    },

    # 5. 심화전공(소프트웨어 심화) 요건
    "deep_major": {
        "min_credits": 36,     # 심화전공으로 최소 36학점
        "track_min_credits": 15,  # 트랙 내 최소 15학점
        "need_two_track_required": True,  # 트랙전필 2과목 포함
        "allow_basic_overlap_max": 7,     # 기본전공과 중복 인정 최대 7학점
        "alternative_rule": (
            "트랙 전필 포함 6학점 + 기타 소프트웨어 학과 교과목 3학점으로 "
            "트랙 15학점 대체 가능"
        ),
    },

    # 6. 트랙 구성
    "tracks": {
        "ai_bigdata": {
            "name": "AI·빅데이터 트랙",
            "required_courses": [
                {"code": "SWE3016", "name": "인공지능", "credits": 3},
                {"code": "SWE3017", "name": "데이터베이스", "credits": 3},
            ],
            "examples": [
                "AI수학",
                "데이터마이닝",
                "웹서비스응용",
                "기계학습개론",
            ],
        },
        "ai_media": {
            "name": "AI미디어 트랙",
            "required_courses": [
                {"code": "SWE3016", "name": "인공지능", "credits": 3},
                {"code": "SWE3019", "name": "디지털신호처리", "credits": 3},
            ],
            "examples": [
                "회로이론",
                "영상처리",
                "AI수학",
                "신호및시스템",
            ],
        },
        "ai_science": {
            "name": "AI계산과학 트랙",
            "required_courses": [
                {"code": "SWE3016", "name": "인공지능", "credits": 3},
                {"code": "SWE3020", "name": "수치해석과최적화", "credits": 3},
            ],
            "examples": [
                "그래프이론",
                "로봇인공지능",
                "모델링&시뮬레이션",
            ],
        },
        "smart_iot": {
            "name": "스마트IoT 트랙",
            "required_courses": [
                {"code": "SWE3022", "name": "임베디드시스템", "credits": 3},
                {"code": "SWE3023", "name": "컴퓨터네트워크", "credits": 3},
            ],
            "examples": [
                "마이크로프로세서",
                "통신시스템",
                "IoT응용프로그래밍",
            ],
        },
        "security": {
            "name": "정보보안 트랙",
            "required_courses": [
                {"code": "SWE3009", "name": "암호학", "credits": 3},
                {"code": "SWE3024", "name": "정보보안", "credits": 3},
            ],
            "examples": [
                "해킹",
                "디지털포렌식",
                "웹서비스응용",
                "컴퓨터보안",
            ],
        },
    },

    # 7. 영역별 최소 학점 – 계산 편의를 위한 요약
    "area_min_credits": {
        "liberal_basic": 22,    # 교양기초
        "univ_required": 5,     # 대학교양 필수
        "exploration": 21,      # 전공탐색
        "major_basic": 36,      # SW 기본전공
        "level300": 45,         # 3000단위 이상 과목
    },
}


# ---------------------------------------------------
# 계산 API (이전 버전에서 GRAD_RULES 구조만 확장)
# ---------------------------------------------------
@csrf_exempt
@require_POST
@csrf_exempt
@require_POST
def calculate_graduation(request):
    """
    요청(JSON) 예시
    {
      "entry_year": 2022,
      "major": "소프트웨어학부",
      "track": "ai_bigdata",          // 또는 "none"

      "total_credits": 135,
      "completed_courses": ["SWE2001", "SWE3016", "SWE3017"],

      "credits": {
        "liberal_basic": 22,          // 교양기초
        "univ_required": 5,           // 대학교양 필수
        "exploration": 21,            // 전공탐색
        "major_basic": 36,            // SW 기본전공
        "level300": 45,               // 3000단위 이상
        "deep_major": 36,             // SW 심화전공
        "track": 15                   // 트랙 내 학점
      },

      "flags": {
        "second_major_done": true,    // 2전공 이수 여부
        "language_cert": true,        // 외국어 인증
        "it_cert": false,             // 정보인증
        "industry_cert": true         // 산업실무역량인증
      }
    }
    """

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

    # 영역별 학점
    liberal_basic_credits = int(credits.get("liberal_basic", 0))
    univ_required_credits = int(credits.get("univ_required", 0))
    exploration_credits = int(credits.get("exploration", 0))
    major_basic_credits = int(credits.get("major_basic", 0))
    level300_credits = int(credits.get("level300", 0))
    deep_major_credits = int(credits.get("deep_major", 0))
    track_credits = int(credits.get("track", 0))

    # 플래그
    second_major_done = bool(flags.get("second_major_done", False))
    language_cert_ok = bool(flags.get("language_cert", False))
    it_cert_ok = bool(flags.get("it_cert", False))
    industry_cert_ok = bool(flags.get("industry_cert", False))

    # 현재는 2022 소프트웨어학부만 지원
    if entry_year != 2022 or major != "소프트웨어학부":
        return JsonResponse(
            {"detail": "현재는 2022학번 소프트웨어학부만 지원합니다."},
            status=400,
        )

    rules = GRAD_RULES_2022_SWE

    # -------------------------
    # 1) 전공필수 진행률
    # -------------------------
    required_courses = rules["major"]["required_courses"]
    required_total_credits = sum(c.get("credits", 0) for c in required_courses)

    completed_required = [
        c for c in required_courses if c["code"] in completed_codes
    ]
    remaining_required = [
        c for c in required_courses if c["code"] not in completed_codes
    ]

    earned_required_credits = sum(c.get("credits", 0) for c in completed_required)

    major_required_percentage = (
        int(earned_required_credits / required_total_credits * 100)
        if required_total_credits > 0
        else 0
    )

    # -------------------------
    # 2) 트랙 전필 이수 여부
    # -------------------------
    track_result = None
    track_required_ok = True  # 트랙을 선택 안 했으면 True로 둠
    if track_key in rules["tracks"]:
        track_info = rules["tracks"][track_key]
        track_required = track_info["required_courses"]
        track_required_total = sum(c.get("credits", 0) for c in track_required)
        track_completed = [
            c for c in track_required if c["code"] in completed_codes
        ]
        track_earned = sum(c.get("credits", 0) for c in track_completed)

        track_required_ok = (track_earned >= track_required_total)

        track_result = {
            "track_key": track_key,
            "track_name": track_info["name"],
            "required_credits": track_required_total,
            "earned_credits": track_earned,
            "completed": track_completed,
        }

    # -------------------------
    # 3) 각 조건별 통과 여부 계산
    # -------------------------
    area_min = rules["area_min_credits"]

    conditions = {}

    # (1) 총 이수 학점 135 이상
    conditions["total_credits"] = (
        total_credits >= rules["total_credits"]
    )

    # (2) 2개 이상의 전공 이수
    conditions["second_major"] = (
        (not rules["need_second_major"]) or second_major_done
    )

    # (3) 외국어 인증
    lang_rule = rules["certifications"]["language"]
    conditions["language_cert"] = (
        (not lang_rule["required"]) or language_cert_ok
    )

    # (4) 정보 or 산업실무 인증 (택1)
    it_rule = rules["certifications"]["it_or_industry"]
    conditions["it_or_industry_cert"] = (
        (not it_rule["required"]) or (it_cert_ok or industry_cert_ok)
    )

    # (5) 3000단위 이상 45학점
    conditions["level300"] = (
        level300_credits >= rules["level300_min_credits"]
    )

    # (6) 교양기초 22
    conditions["liberal_basic"] = (
        liberal_basic_credits >= area_min["liberal_basic"]
    )

    # (7) 대학교양 필수 5
    conditions["univ_required"] = (
        univ_required_credits >= area_min["univ_required"]
    )

    # (8) 전공탐색 21
    conditions["exploration"] = (
        exploration_credits >= area_min["exploration"]
    )

    # (9) SW 기본전공 36
    conditions["major_basic"] = (
        major_basic_credits >= area_min["major_basic"]
    )

    # (10) 전공필수 과목 전체 이수
    conditions["major_required_all"] = (len(remaining_required) == 0)

    # (11) 심화전공 / 트랙 요건
    deep_rules = rules["deep_major"]

    # 트랙을 선택하지 않은 경우 → 심화/트랙 요건은 아직 안 보는 걸로 처리
    if track_key in rules["tracks"]:
        # 심화전공 최소 36학점
        conditions["deep_major_min"] = (
            deep_major_credits >= deep_rules["min_credits"]
        )
        # 트랙 내 최소 15학점
        conditions["track_min_credits"] = (
            track_credits >= deep_rules["track_min_credits"]
        )
        # 트랙 전필 2과목 포함 이수
        conditions["track_required_all"] = track_required_ok
    else:
        conditions["deep_major_min"] = True
        conditions["track_min_credits"] = True
        conditions["track_required_all"] = True

    # 최종 졸업 가능 여부 = 모든 조건 AND
    can_graduate = all(conditions.values())

    # -------------------------
    # 4) 응답 JSON 구성
    # -------------------------
    response_data = {
        "entry_year": entry_year,
        "major": major,
        "track": track_key,

        # 상단 카드용
        "summary": {
            "total_credits": total_credits,
            "required_total_credits": rules["total_credits"],
            "can_graduate": can_graduate,
        },

        # 전공필수 진행률
        "major_required": {
            "percentage": major_required_percentage,
            "earned_credits": earned_required_credits,
            "total_credits": required_total_credits,
            "completed": completed_required,
            "remaining": remaining_required,
        },

        # 트랙 결과 (선택)
        "track": track_result,

        # 어떤 조건 때문에 불합격인지 프론트에서 바로 보여줄 수 있도록
        "conditions": conditions,

        # 룰 메타 정보
        "rules_meta": {
            "area_min_credits": rules["area_min_credits"],
            "need_second_major": rules["need_second_major"],
            "certifications": rules["certifications"],
            "level300_min_credits": rules["level300_min_credits"],
            "deep_major": rules["deep_major"],
        },
    }

    return JsonResponse(response_data, status=200)