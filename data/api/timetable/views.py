# timetable/views.py
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser

from .models import Timetable, Course
import json


def get_login_user(request):
    """
    세션 로그인 된 유저 반환. 아니면 None.
    """
    user = getattr(request, "user", None)
    if isinstance(user, AnonymousUser) or user is None or not user.is_authenticated:
        return None
    return user


@method_decorator(csrf_exempt, name="dispatch")
class TimetableSemestersAPI(View):
    """
    내가 가진 시간표의 학기 목록
    GET /api/timetable/semesters/

    응답:
    {
      "semesters": [
        {"year": 2025, "semester": 1},
        {"year": 2025, "semester": 2}
      ]
    }
    """

    def get(self, request):
        user = get_login_user(request)
        if user is None:
            return JsonResponse({"detail": "로그인이 필요합니다."}, status=401)

        qs = (
            Timetable.objects
            .filter(user=user)
            .values("year", "semester")
            .distinct()
            .order_by("year", "semester")
        )

        semesters = [
            {"year": row["year"], "semester": row["semester"]}
            for row in qs
        ]

        return JsonResponse({"semesters": semesters})


@method_decorator(csrf_exempt, name="dispatch")
class TimetableBySemesterAPI(View):
    """
    GET  /api/timetable/?year=YYYY&semester=S  → 해당 학기의 시간표
    POST /api/timetable/                     → 시간표 초기화/저장
        body: { "year": 2025, "semester": 2, "timetable": [ ... ] }
    """

    def get(self, request):
        user = get_login_user(request)
        if user is None:
            return JsonResponse({"detail": "로그인이 필요합니다."}, status=401)

        year = request.GET.get("year")
        semester = request.GET.get("semester")

        if not year or not semester:
            return JsonResponse(
                {"detail": "year, semester 쿼리 파라미터가 필요합니다."},
                status=400,
            )

        try:
            year = int(year)
            semester = int(semester)
        except ValueError:
            return JsonResponse({"detail": "year/semester 형식이 잘못되었습니다."}, status=400)

        qs = Timetable.objects.filter(
            user=user,
            year=year,
            semester=semester,
        ).order_by("day", "period")

        if not qs.exists():
            # 해당 학기 시간표 없음
            return JsonResponse({"timetable": []}, status=200)

        data = [
            {
                "day": t.day,
                "period": t.period,
                "subject": t.subject,
                "classroom": t.classroom,
                "memo": t.memo,
            }
            for t in qs
        ]

        return JsonResponse({"timetable": data})

    def post(self, request):
        """
        새 시간표 만들기/덮어쓰기용.
        body 예시:
        {
          "year": 2025,
          "semester": 2,
          "timetable": [
            {"day": "MON", "period": 1, "subject": "자료구조", "classroom": "...", "memo": "전필"},
            ...
          ]
        }
        """
        user = get_login_user(request)
        if user is None:
            return JsonResponse({"detail": "로그인이 필요합니다."}, status=401)

        try:
            body = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"detail": "올바른 JSON 형식이 아닙니다."}, status=400)

        year = body.get("year")
        semester = body.get("semester")
        timetable_items = body.get("timetable", [])

        if year is None or semester is None:
            return JsonResponse({"detail": "year, semester 필드가 필요합니다."}, status=400)

        try:
            year = int(year)
            semester = int(semester)
        except ValueError:
            return JsonResponse({"detail": "year/semester 형식이 잘못되었습니다."}, status=400)

        # 해당 유저+학기 시간표 싹 지우고 새로 넣기
        Timetable.objects.filter(
            user=user,
            year=year,
            semester=semester,
        ).delete()

        bulk = []
        for item in timetable_items:
            day = item.get("day")
            period = item.get("period")
            subject = item.get("subject", "")
            classroom = item.get("classroom", "")
            memo = item.get("memo", "")

            if not day or not period:
                continue

            bulk.append(
                Timetable(
                    user=user,
                    year=year,
                    semester=semester,
                    day=day,
                    period=period,
                    subject=subject,
                    classroom=classroom,
                    memo=memo,
                )
            )

        if bulk:
            Timetable.objects.bulk_create(bulk)

        return JsonResponse({"success": True})


@method_decorator(csrf_exempt, name="dispatch")
class CourseSearchAPI(View):
    """
    수업 검색
    GET /api/timetable/courses/?year=2025&semester=2&q=알고
    응답: [{id, year, semester, subject, professor, day, period, classroom, memo}, ...]
    """

    def get(self, request):
        year = request.GET.get("year")
        semester = request.GET.get("semester")
        query = request.GET.get("q", "").strip()

        qs = Course.objects.all()

        if year:
            try:
                qs = qs.filter(year=int(year))
            except ValueError:
                pass

        if semester:
            try:
                qs = qs.filter(semester=int(semester))
            except ValueError:
                pass

        if query:
            qs = qs.filter(
                Q(subject__icontains=query) |
                Q(professor__icontains=query)
            )

        qs = qs.order_by("year", "semester", "day", "period")

        results = [
            {
                "id": c.id,
                "year": c.year,
                "semester": c.semester,
                "subject": c.subject,
                "professor": c.professor,
                "day": c.day,
                "period": c.period,
                "classroom": c.classroom,
                "memo": c.memo,
            }
            for c in qs
        ]
        return JsonResponse(results, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class TimetableAddCourseAPI(View):
    """
    내 시간표에 과목 1개 추가
    POST /api/timetable/add-course/
        { "course_id": 3, "year": 2025, "semester": 2 }

    → 같은 유저 + 연도 + 학기 + 요일 + 교시 조합으로 Timetable upsert
    """

    def post(self, request):
        user = get_login_user(request)
        if user is None:
            return JsonResponse({"error": "로그인이 필요합니다."}, status=401)

        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON 파싱 실패"}, status=400)

        course_id = data.get("course_id")
        year = data.get("year")
        semester = data.get("semester")

        if course_id is None:
            return JsonResponse({"error": "course_id 필수"}, status=400)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({"error": "해당 과목을 찾을 수 없습니다."}, status=404)

        if year is None:
            year = course.year
        if semester is None:
            semester = course.semester

        try:
            year = int(year)
            semester = int(semester)
        except ValueError:
            return JsonResponse({"error": "year/semester 형식 오류"}, status=400)

        Timetable.objects.update_or_create(
            user=user,
            year=year,
            semester=semester,
            day=course.day,
            period=course.period,
            defaults={
                "subject": course.subject,
                "classroom": course.classroom,
                "memo": course.memo,
            },
        )

        return JsonResponse({"success": True})
