from django.db import models
from django.contrib.auth.models import User


# =====================================
# 1. 과목 테이블 (전체 강의 DB)
# =====================================
class Course(models.Model):
    class Category(models.TextChoices):
        GE_BASIC = "GE_BASIC", "교양기초"
        GE_UNIV_REQUIRED = "GE_UNIV_REQUIRED", "대학교양(필수)"
        GE_UNIV_ELECTIVE = "GE_UNIV_ELECTIVE", "대학교양(선택)"
        EXPLORATION = "EXPLORATION", "전공탐색"
        MAJOR_BASIC = "MAJOR_BASIC", "전공(기본)"
        MAJOR_DEEP = "MAJOR_DEEP", "전공(심화)"

    class MajorType(models.TextChoices):
        NONE = "NONE", "해당없음"
        SW_BASIC = "SW_BASIC", "소프트웨어 기본전공"
        SW_DEEP = "SW_DEEP", "소프트웨어 심화전공"

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    credits = models.PositiveSmallIntegerField(default=0)

    category = models.CharField(max_length=30, choices=Category.choices)
    major_type = models.CharField(
        max_length=20,
        choices=MajorType.choices,
        default=MajorType.NONE,
    )

    is_required = models.BooleanField(default=False)
    is_major_required = models.BooleanField(default=False)
    level = models.PositiveSmallIntegerField(default=1000)
    ge_area = models.CharField(max_length=50, null=True, blank=True)

    note = models.TextField(blank=True)
    is_counted_in_basic_major = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} {self.name}"


# =====================================
# 2. 트랙 (AI빅데이터 / AI미디어 ...)
# =====================================
class Track(models.Model):
    class TrackType(models.TextChoices):
        AI_BIGDATA = "AI_BIGDATA", "AI빅데이터"
        AI_MEDIA = "AI_MEDIA", "AI미디어"
        AI_SCIENCE = "AI_SCIENCE", "AI계산과학"
        SMART_IOT = "SMART_IOT", "스마트IoT"
        SECURITY = "SECURITY", "정보보안"

    name = models.CharField(max_length=30, choices=TrackType.choices, unique=True)
    description = models.TextField(blank=True)
    min_credits = models.PositiveSmallIntegerField(default=15)

    def __str__(self):
        return self.get_name_display()


# =====================================
# 3. 트랙 ↔ 과목 매핑 (N:M)
# =====================================
class TrackCourse(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="track_courses")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="track_courses")
    is_track_required = models.BooleanField(default=False)

    class Meta:
        unique_together = ("track", "course")

    def __str__(self):
        return f"{self.track} - {self.course}"


# =====================================
# 4. 졸업요건 테이블
# =====================================
class GraduationRequirement(models.Model):
    major_type = models.CharField(
        max_length=20,
        choices=Course.MajorType.choices,
        default=Course.MajorType.SW_BASIC,
    )

    total_credits = models.PositiveSmallIntegerField(default=135)
    min_major_credits = models.PositiveSmallIntegerField(default=36)
    min_3000_level_credits = models.PositiveSmallIntegerField(default=45)

    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_major_type_display()} 졸업요건"


# =====================================
# 5. 영역별 요구 학점 테이블
# =====================================
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
    name = models.CharField(max_length=50)
    min_credits = models.PositiveSmallIntegerField()

    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.requirement} - {self.name}"


# =====================================
# 6. 유저가 실제로 수강한 과목 (로그인 기반)
# =====================================
class TakenCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    year = models.PositiveSmallIntegerField()
    semester = models.CharField(max_length=10)  # "1-1", "2-2"

    grade = models.CharField(max_length=2, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.code} ({self.year} {self.semester})"
