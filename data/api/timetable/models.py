# timetable/models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Course(models.Model):
    """
    실제 개설된 '수업' 정보 테이블
    → 검색 모달에서 이 데이터를 조회해서 시간표에 담아 넣는 용도
    """
    SEMESTER_CHOICES = [
        (1, "1학기"),
        (2, "2학기"),
    ]

    DAY_CHOICES = [
        ('MON', '월요일'),
        ('TUE', '화요일'),
        ('WED', '수요일'),
        ('THU', '목요일'),
        ('FRI', '금요일'),
        ('SAT', '토요일'),
        ('SUN', '일요일'),
    ]

    year = models.PositiveSmallIntegerField(help_text="연도 (예: 2025)")
    semester = models.PositiveSmallIntegerField(
        choices=SEMESTER_CHOICES,
        help_text="학기 (1=1학기, 2=2학기)"
    )

    subject = models.CharField(max_length=100, help_text="과목명")
    professor = models.CharField(max_length=50, blank=True, help_text="담당 교수 (선택)")

    day = models.CharField(
        max_length=3,
        choices=DAY_CHOICES,
        help_text="요일 (예: MON, TUE ...)"
    )
    period = models.PositiveSmallIntegerField(help_text="교시 (1, 2, 3 ...)")

    classroom = models.CharField(max_length=50, blank=True, help_text="강의실 (선택)")
    memo = models.CharField(max_length=200, blank=True, help_text="비고 (선택)")

    class Meta:
        ordering = ["year", "semester", "day", "period", "subject"]

    def __str__(self):
        return f"[{self.year}-{self.semester}] {self.subject} ({self.day} {self.period}교시)"


class Timetable(models.Model):
    # 학기 선택 (필요하면 3학기/계절학기 나중에 추가 가능)
    SEMESTER_CHOICES = [
        (1, "1학기"),
        (2, "2학기"),
    ]

    # 어떤 유저의 시간표인지
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="timetables",
    )

    # 연도/학기
    year = models.PositiveSmallIntegerField(
        help_text="연도 (예: 2025)"
    )
    semester = models.PositiveSmallIntegerField(
        choices=SEMESTER_CHOICES,
        help_text="학기 (1=1학기, 2=2학기)"
    )

    # 기존 필드들
    DAY_CHOICES = [
        ('MON', '월요일'),
        ('TUE', '화요일'),
        ('WED', '수요일'),
        ('THU', '목요일'),
        ('FRI', '금요일'),
        ('SAT', '토요일'),
        ('SUN', '일요일'),
    ]

    day = models.CharField(
        max_length=3,
        choices=DAY_CHOICES,
        help_text="요일 (예: MON, TUE ...)"
    )
    period = models.PositiveSmallIntegerField(
        help_text="교시 (1, 2, 3 ...)"
    )
    subject = models.CharField(
        max_length=100,
        help_text="과목명"
    )
    classroom = models.CharField(
        max_length=50,
        blank=True,
        help_text="강의실 (선택)"
    )
    memo = models.CharField(
        max_length=200,
        blank=True,
        help_text="비고 (선택)"
    )

    # 🔥 새로 추가된 공유 여부 필드
    is_shared = models.BooleanField(default=False)

    class Meta:
        # 같은 유저 + 연도 + 학기 + 요일 + 교시 조합은 하나만
        unique_together = ('user', 'year', 'semester', 'day', 'period')
        ordering = ['year', 'semester', 'day', 'period']

    def __str__(self):
        return f"[{self.year}-{self.semester}] {self.user.username} / {self.day} {self.period}교시 - {self.subject}"

class TimetableEntry(models.Model):
    """
    한 칸짜리 시간표 데이터
    예: 월요일 10~12시 자료구조
    """
    DAY_CHOICES = [
        ("MON", "월"),
        ("TUE", "화"),
        ("WED", "수"),
        ("THU", "목"),
        ("FRI", "금"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="timetable_entries",
    )
    term = models.CharField(max_length=20)   # 예: "2025-2"
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start = models.IntegerField()            # 시작 시간(정수, 9, 10 ...)
    end = models.IntegerField()              # 끝 시간(정수)
    name = models.CharField(max_length=100)  # 과목명
    location = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["term", "day", "start"]

    def __str__(self):
        return f"{self.term} {self.get_day_display()} {self.start}~{self.end} {self.name}"