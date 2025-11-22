# timetable/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

from .models import Timetable


@login_required
@require_GET
def timetable_semesters(request):
    """
    현재 로그인한 유저가 가진 연도/학기 목록을 내려주는 API
    GET /api/timetable/semesters/
    응답 예시:
    [
      {"year": 2025, "semester": 2},
      {"year": 2025, "semester": 1}
    ]
    """
    user = request.user

    qs = (
        Timetable.objects
        .filter(user=user)
        .values("year", "semester")
        .distinct()
        .order_by("-year", "-semester")
    )

    semesters = [
        {
            "year": row["year"],
            "semester": row["semester"],
            # 프론트에서 바로 쓸 수 있도록 라벨도 같이 내려줌 (원하면 사용)
            "label": f'{row["year"]}년 {row["semester"]}학기',
        }
        for row in qs
    ]

    return JsonResponse(semesters, safe=False)


@login_required
@require_GET
def timetable_list(request):
    """
    현재 로그인한 유저의 특정 연도/학기 시간표를 내려주는 API

    GET /api/timetable/?year=2025&semester=2
    year/semester 없으면 해당 유저의 '가장 최근' 학기 기준으로 반환
    """
    user = request.user

    qs = Timetable.objects.filter(user=user)

    year_param = request.GET.get("year")
    sem_param = request.GET.get("semester")

    # year & semester가 명시되면 그걸로 필터
    if year_param and sem_param:
        try:
            year = int(year_param)
            semester = int(sem_param)
            qs = qs.filter(year=year, semester=semester)
        except ValueError:
            # 숫자 파싱 실패하면 아래에서 latest로 처리
            pass

    # 둘 다 안 들어왔으면 최신 학기 자동 선택
    if not (year_param and sem_param):
        latest = (
            Timetable.objects.filter(user=user)
            .order_by("-year", "-semester")
            .first()
        )
        if latest is None:
            return JsonResponse([], safe=False)

        qs = qs.filter(year=latest.year, semester=latest.semester)

    data = [
        {
            "year": t.year,
            "semester": t.semester,
            "day": t.day,
            "period": t.period,
            "subject": t.subject,
            "classroom": t.classroom,
            "memo": t.memo,
        }
        for t in qs
    ]

    return JsonResponse(data, safe=False)
