from rest_framework.views import APIView
from rest_framework.response import Response
# from users.models import UserProfile  # 나중에 실제 유저 정보 쓸 때 사용


class MainSummaryAPI(APIView):
    """
    메인 페이지 요약 정보 API

    TODO:
      - request.user 기반으로 실제 이수 학점/성적/분류별 학점/트랙/수강 과목/채플/메모를 계산해서 채우기
    """

    def get(self, request):
        # === 1) 총 이수 진행도 ===
        total_credits = 135          # 졸업 필요 학점 (고정)
        earned_credits = 123         # TODO: DB에서 계산

        rate = round(earned_credits / total_credits * 100)

        overall = {
            "total_credits": total_credits,
            "earned_credits": earned_credits,
            "rate": rate,
        }

        # === 2) 성적 비율 ===
        # TODO: 실제 성적 테이블에서 집계
        grade_distribution = {
            "A": {"label": "A+~A0", "count": 15, "rate": 47},
            "B": {"label": "B+~B0", "count": 14, "rate": 44},
            "C": {"label": "C+~C0", "count": 2, "rate": 7},
            "D": {"label": "D+~D0", "count": 1, "rate": 2},
            "F": {"label": "F", "count": 0, "rate": 0},
        }

        # === 3) 이수 학점 진행도 (분류별) ===
        category_progress = [
            {"code": "GE", "name": "교양", "taken": 52, "total": 52},
            {"code": "MR", "name": "전공필수", "taken": 56, "total": 65},
            {"code": "ME", "name": "전공선택", "taken": 15, "total": 16},
        ]

        # === 4) 트랙 추천 (회원가입 때 관심분야 기반) ===
        track_recommendation = {
            "track_name": "AI 트랙",
            "score": 1,
            "message": "연관도 점수: 1 — 관련 과목을 더 들으면 정확도가 높아집니다.",
            "courses": [
                {"priority": 1, "name": "기계학습", "type": "전선", "credit": 3},
                {"priority": 2, "name": "데이터베이스", "type": "전필", "credit": 3},
                {"priority": 3, "name": "확률과통계", "type": "MSC", "credit": 3},
            ],
        }

        # === 5) 내 기본 정보 카드 ===
        # TODO: users 앱의 User / Profile 모델에서 가져오기
        user_info = {
            "name": "김연세",
            "student_id": "20220000",
            "year": 2,
            "department": "소프트웨어학부",
        }

        # === 6) 현재 학기 수강 과목 리스트 ===
        # TODO: 실제 수강신청/성적 테이블에서 필터링
        current_courses = [
            {"name": "자료구조", "type": "전필", "credit": 3},
            {"name": "인공지능개론", "type": "전선", "credit": 3},
            {"name": "운영체제", "type": "전필", "credit": 3},
        ]

        # === 7) 채플 카운트 ===
        # 예: 채플 4번 들어야 졸업, 현재 0회
        required_chapel = 4
        taken_chapel = 0      # TODO: 채플 수강 이력에서 계산

        chapel_rate = (
            round(taken_chapel / required_chapel * 100) if required_chapel > 0 else 0
        )

        chapel = {
            "taken": taken_chapel,
            "required": required_chapel,
            "rate": chapel_rate,
        }

        # === 8) 졸업 요구사항 메모 ===
        # TODO: 유저별로 커스터마이징해서 저장/수정 가능하게 만들 수 있음
        memo = "- 졸업작품 / 졸업논문 중 택1\n- 토익 800+"

        return Response(
            {
                "overall": overall,
                "grade_distribution": grade_distribution,
                "category_progress": category_progress,
                "track_recommendation": track_recommendation,
                "user_info": user_info,
                "current_courses": current_courses,
                "chapel": chapel,
                "memo": memo,
            }
        )
