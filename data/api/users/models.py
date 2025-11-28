# users/models.py
from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    # 기본 User와 1:1로 연결
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # 추가 정보
    student_id = models.CharField(max_length=20, unique=True)  # 학번
    real_name = models.CharField(max_length=50)                # 실명

    # 1학년1학기 ~ 4학년2학기
    SEMESTER_CHOICES = [
        ("1-1", "1학년 1학기"),
        ("1-2", "1학년 2학기"),
        ("2-1", "2학년 1학기"),
        ("2-2", "2학년 2학기"),
        ("3-1", "3학년 1학기"),
        ("3-2", "3학년 2학기"),
        ("4-1", "4학년 1학기"),
        ("4-2", "4학년 2학기"),
    ]
    current_semester = models.CharField(max_length=3, choices=SEMESTER_CHOICES)

    DEPARTMENT_CHOICES = [
        ("SOFTWARE", "소프트웨어학부"),
        ("DATASCIENCE", "데이터사이언스학부"),
        ("AI_SEMI", "AI반도체학부"),
        ("BIOMED", "의공학부"),
        ("CLINICAL", "임상병리학과"),
        ("OCC_THERAPY", "작업치료학과"),
    ]
    major_department = models.CharField(max_length=30, choices=DEPARTMENT_CHOICES)

    # 관심 전공/분야
    INTEREST_CHOICES = [
        ("AI_ML", "AI/머신러닝"),
        ("SECURITY_NETWORK", "보안/네트워크"),
        ("GAME_MEDIA", "게임/미디어"),
        ("EMBEDDED_SYSTEM", "임베디드/시스템"),
        ("STARTUP_SERVICE", "창업/서비스기획"),
        ("OTHER", "기타(직접입력)"),
    ]
    interest = models.CharField(max_length=30, choices=INTEREST_CHOICES)
    # 기타일 때만 값 들어가도 되도록
    interest_text = models.CharField(max_length=100, blank=True)

    # 데이터 사용 동의
    data_consent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.real_name} ({self.student_id})"


# ============================
# 🔥 메인페이지 요약 정보 저장용 모델
# ============================
class UserSummary(models.Model):
    # AUTH_USER_MODEL 그대로 사용 (커스텀 유저 대비)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="summary",
    )

    # 총 이수 학점
    total_credits = models.PositiveSmallIntegerField(default=0)

    # 계산기에서 쓰는 영역별 학점 그대로 저장
    liberal_basic_credits = models.PositiveSmallIntegerField(default=0)
    univ_required_credits = models.PositiveSmallIntegerField(default=0)
    exploration_credits = models.PositiveSmallIntegerField(default=0)
    major_basic_credits = models.PositiveSmallIntegerField(default=0)
    deep_major_credits = models.PositiveSmallIntegerField(default=0)
    level300_credits = models.PositiveSmallIntegerField(default=0)

    # 수강 과목 리스트 (코드/이름/학점/분류만 JSON으로 저장)
    # 예) [{"code": "SWE2001", "name": "데이터구조론", "credits": 3, "category": "MAJOR_BASIC"}, ...]
    selected_courses = models.JSONField(default=list)

    def __str__(self):
        return f"{self.user.username} 요약 정보"
