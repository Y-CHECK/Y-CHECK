from django.db import models


# 1. 과목 공통 테이블
class Course(models.Model):
    class Category(models.TextChoices):
        GE_BASIC = "GE_BASIC", "교양기초"
        GE_UNIV_REQUIRED = "GE_UNIV_REQUIRED", "대학교양(필수)"
        GE_UNIV_ELECTIVE = "GE_UNIV_ELECTIVE", "대학교양(선택)"
        EXPLORATION = "EXPLORATION", "전공탐색"
        MAJOR_BASIC = "MAJOR_BASIC", "전공(기본)"
        MAJOR_DEEP = "MAJOR_DEEP", "전공(심화)"

    class MajorType(models.TextChoices):
        NONE = "NONE", "해당없음"          # 교양 등
        SW_BASIC = "SW_BASIC", "소프트웨어 기본전공"
        SW_DEEP = "SW_DEEP", "소프트웨어 심화전공"

    code = models.CharField(max_length=20, unique=True)     # SWE3006, YHA1002 등
    name = models.CharField(max_length=100)
    credits = models.PositiveSmallIntegerField(default=0)

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
    )
    major_type = models.CharField(
        max_length=20,
        choices=MajorType.choices,
        default=MajorType.NONE,
    )

    is_required = models.BooleanField(default=False)        # 전필 / 교양필수 여부
    is_major_required = models.BooleanField(default=False)  # 전공필수만 따로 표시
    level = models.PositiveSmallIntegerField(default=1000)  # 1000, 2000, 3000, 4000 단위
    ge_area = models.CharField(max_length=50, null=True, blank=True)
    note = models.TextField(blank=True)

    # 예외 처리용 (기본전공으로 인정 안 되는 과목 등)
    is_counted_in_basic_major = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} {self.name}"


# 2. 트랙 (AI빅데이터 / AI미디어 / AI계산과학 / 스마트IoT / 정보보안)
class Track(models.Model):
    class TrackType(models.TextChoices):
        AI_BIGDATA = "AI_BIGDATA", "AI빅데이터"
        AI_MEDIA = "AI_MEDIA", "AI미디어"
        AI_SCIENCE = "AI_SCIENCE", "AI계산과학"
        SMART_IOT = "SMART_IOT", "스마트IoT"
        SECURITY = "SECURITY", "정보보안"

    name = models.CharField(max_length=30, choices=TrackType.choices, unique=True)
    description = models.TextField(blank=True)
    min_credits = models.PositiveSmallIntegerField(default=15)  # 트랙 이수 최소 15학점

    def __str__(self):
        return self.get_name_display()


# 3. 트랙별 과목 매핑 (N:M 관계)
class TrackCourse(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="track_courses")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="track_courses")
    is_track_required = models.BooleanField(default=False)  # 트랙 전필인지 여부

    class Meta:
        unique_together = ("track", "course")

    def __str__(self):
        return f"{self.track} - {self.course}"


# 4. 졸업요건 (큰 틀: 총학점, 전공 최소학점, 3000단위 최소학점 등)
class GraduationRequirement(models.Model):
    major_type = models.CharField(
        max_length=20,
        choices=Course.MajorType.choices,
        default=Course.MajorType.SW_BASIC,
    )
    total_credits = models.PositiveSmallIntegerField(default=135)   # 총 이수학점
    min_major_credits = models.PositiveSmallIntegerField(default=36)
    min_3000_level_credits = models.PositiveSmallIntegerField(default=45)

    # 2전공 필수, 외국어/정보/산업실무 인증 등은 우선 메모로 관리
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_major_type_display()} 졸업요건"


# 5. 영역별 필요 학점 (교양기초 22, 대학교양필수 5, 전공탐색 21 등)
class AreaRequirement(models.Model):
    class AreaCode(models.TextChoices):
        GE_BASIC = "GE_BASIC", "교양기초"
        GE_UNIV_REQUIRED = "GE_UNIV_REQUIRED", "대학교양(필수)"
        GE_UNIV_ELECTIVE = "GE_UNIV_ELECTIVE", "대학교양(선택)"
        EXPLORATION = "EXPLORATION", "전공탐색"
        MAJOR = "MAJOR", "전공 전체"

    requirement = models.ForeignKey(
        GraduationRequirement,
        on_delete=models.CASCADE,
        related_name="areas",
    )
    area_code = models.CharField(max_length=30, choices=AreaCode.choices)
    name = models.CharField(max_length=50)  # 예: "교양기초", "전공탐색 소계"
    min_credits = models.PositiveSmallIntegerField()

    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.requirement} - {self.name}"


# 6. 학생 수강내역 (실제 계산에 사용)
class TakenCourse(models.Model):
    # User 모델을 쓰면 여기에 ForeignKey(User)를 걸어주면 됨
    student_id = models.CharField(max_length=50)  # 임시용, 나중에 User로 교체 가능
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    semester = models.CharField(max_length=10)  # "1-1", "2-2" 등
    grade = models.CharField(max_length=2, blank=True)  # A+, B0 ... (필요 시)

    def __str__(self):
        return f"{self.student_id} - {self.course.code}"
