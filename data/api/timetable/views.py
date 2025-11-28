from django.http import JsonResponse, HttpResponseNotAllowed
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Count

from .models import Timetable, Course, TimetableEntry
from .serializers import TimetableEntrySerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json


def get_login_user(request):
    """
    세션 로그인 기준으로 request.user 에서 유저를 꺼내는 간단한 헬퍼.
    로그인 안 되어 있으면 None 반환.
    """
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        return user
    return None



# =========================================
#  학기별 시간표 조회 / 생성
#   GET  /api/timetable/?year=YYYY&semester=S
#   POST /api/timetable/
# =========================================
@method_decorator(csrf_exempt, name="dispatch")
class TimetableListCreateAPI(View):
    """
    GET:
      /api/timetable/?year=2025&semester=2
      → 해당 유저의 해당 학기 시간표를 내려줌

    응답 예:
      {
        "timetable": [
          {
            "day": "MON",
            "period": 3,
            "subject": "데이터구조론",
            "classroom": "공학관101",
            "memo": "전필"
          },
          ...
        ]
      }

    POST:
      /api/timetable/
      body: { "year": 2025, "semester": 2, "timetable": [...] }

      지금 프론트에서는 "새 시간표 만들기" 시
      {year, semester, timetable: []} 만 보내므로,
      여기서는 해당 학기의 기존 row를 지우고
      "학기 존재 표시용 더미 row" 하나를 만들어 둔다.
      (day="MON", period=0 → 화면에는 안 보임)
    """

    def get(self, request):
        user = get_login_user(request)
        if user is None:
            return JsonResponse({"detail": "로그인이 필요합니다."}, status=401)

        year = request.GET.get("year")
        semester = request.GET.get("semester")

        try:
            year = int(year)
            semester = int(semester)
        except (TypeError, ValueError):
            return JsonResponse(
                {"detail": "year, semester 쿼리 파라미터가 필요합니다."}, status=400
            )

        qs = Timetable.objects.filter(
            user=user,
            year=year,
            semester=semester,
        ).order_by("day", "period", "id")

        if not qs.exists():
            return JsonResponse(
                {"detail": "해당 학기 시간표가 없습니다."},
                status=404,
            )

        data = []
        for t in qs:
            # period=0 은 "더미"라서 화면에 안 쓰이게 건너뜀
            if t.period == 0:
                continue
            data.append(
                {
                    "day": t.day,
                    "period": t.period,
                    "subject": t.subject,
                    "classroom": t.classroom,
                    "memo": t.memo,
                }
            )

        return JsonResponse({"timetable": data})

    def post(self, request):
        if request.content_type != "application/json":
            return JsonResponse({"detail": "JSON body 필요"}, status=400)

        user = get_login_user(request)
        if user is None:
            return JsonResponse({"detail": "로그인이 필요합니다."}, status=401)

        try:
            body = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON 파싱 오류"}, status=400)

        year = body.get("year")
        semester = body.get("semester")
        timetable_entries = body.get("timetable", [])

        try:
            year = int(year)
            semester = int(semester)
        except (TypeError, ValueError):
            return JsonResponse({"detail": "year/semester 형식 오류"}, status=400)

        # 해당 학기 기존 row 전부 삭제
        Timetable.objects.filter(user=user, year=year, semester=semester).delete()

        created = []

        if timetable_entries:
            # 나중에 직접 모든 칸을 저장하는 방식으로 확장 가능
            for item in timetable_entries:
                day = item.get("day")
                period = item.get("period")
                if not day or period is None:
                    continue

                tt = Timetable.objects.create(
                    user=user,
                    year=year,
                    semester=semester,
                    day=day,
                    period=int(period),
                    subject=item.get("subject", ""),
                    classroom=item.get("classroom", ""),
                    memo=item.get("memo", ""),
                )
                created.append(tt.id)
        else:
            # 프론트에서 새 시간표 생성 시 timetable: [] 로 보내므로
            # "해당 학기가 존재한다"는 표시만 해 주기 위해 더미 row 하나 생성
            Timetable.objects.create(
                user=user,
                year=year,
                semester=semester,
                day="MON",
                period=0,  # 화면엔 없는 교시
                subject="",
                classroom="",
                memo="",
            )

        return JsonResponse(
            {
                "success": True,
                "year": year,
                "semester": semester,
                "created_ids": created,
            }
        )


# =========================================
#  내가 가지고 있는 학기 목록
#   GET /api/timetable/semesters/
# =========================================
class SemesterListAPI(View):
    """
    로그인한 사용자가 가지고 있는 시간표의 학기 목록을 내려줌.

    응답 예:
      {
        "semesters": [
          { "year": 2025, "semester": 2, "label": "2025년 2학기" },
          ...
        ]
      }
    """

    def get(self, request):
        user = get_login_user(request)
        if user is None:
            return JsonResponse({"detail": "로그인이 필요합니다."}, status=401)

        qs = (
            Timetable.objects.filter(user=user)
            .values("year", "semester")
            .annotate(cnt=Count("id"))
            .order_by("-year", "-semester")
        )

        semesters = [
            {
                "year": row["year"],
                "semester": row["semester"],
                "label": f"{row['year']}년 {row['semester']}학기",
            }
            for row in qs
        ]

        return JsonResponse({"semesters": semesters})


# =========================================
#  수업 검색 API
#   GET /api/timetable/courses/?year=2025&semester=2&q=데이터
# =========================================
class CourseSearchAPI(View):
    def get(self, request):
        user = get_login_user(request)
        if user is None:
            return JsonResponse({"detail": "로그인이 필요합니다."}, status=401)

        year = request.GET.get("year")
        semester = request.GET.get("semester")
        q = request.GET.get("q", "").strip()

        try:
            year = int(year)
            semester = int(semester)
        except (TypeError, ValueError):
            return JsonResponse({"detail": "year/semester 형식 오류"}, status=400)

        qs = Course.objects.filter(year=year, semester=semester)

        if q:
            qs = qs.filter(subject__icontains=q) | qs.filter(professor__icontains=q)

        qs = qs.order_by("day", "period", "subject")

        data = []
        for c in qs:
            data.append(
                {
                    "id": c.id,
                    "year": c.year,
                    "semester": c.semester,
                    "subject": c.subject,
                    "professor": c.professor,
                    "day": c.day,
                    "period": c.period,
                    "classroom": c.classroom,
                }
            )

        return JsonResponse(data, safe=False)


# =========================================
#  수업 추가 API
#   POST /api/timetable/add-course/
#   body: { "course_id": 1, "year": 2025, "semester": 2 }
# =========================================
@method_decorator(csrf_exempt, name="dispatch")
class AddCourseAPI(View):
    def post(self, request):
        if request.content_type != "application/json":
            return JsonResponse({"detail": "JSON body 필요"}, status=400)

        user = get_login_user(request)
        if user is None:
            return JsonResponse({"detail": "로그인이 필요합니다."}, status=401)

        try:
            body = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON 파싱 오류"}, status=400)

        course_id = body.get("course_id")
        year = body.get("year")
        semester = body.get("semester")

        try:
            year = int(year)
            semester = int(semester)
            course = Course.objects.get(id=course_id)
        except (TypeError, ValueError, Course.DoesNotExist):
            return JsonResponse({"detail": "유효하지 않은 course_id/year/semester"}, status=400)

        # 해당 학기의 "더미 row(period=0)" 는 있더라도 상관 없음
        tt, created = Timetable.objects.update_or_create(
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

        return JsonResponse(
            {
                "success": True,
                "created": created,
                "id": tt.id,
            }
        )


# =========================================
#  공유 여부 토글 + 조회
#   POST /api/timetable/share/
#   GET  /api/timetable/share-status/?year=2025&semester=2
# =========================================
@method_decorator(csrf_exempt, name="dispatch")
class TimetableShareToggleAPI(View):
    """
    POST /api/timetable/share/
    body: { "year": 2025, "semester": 1, "is_shared": true }

    → 해당 학기의 시간표 전체에 대해 공유 여부 토글
    """

    def _parse_bool(self, value):
        """
        JS에서 true/false 로 오든, "true"/"false" 문자열로 오든 안전하게 bool로 바꿔주는 헬퍼
        """
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        return str(value).lower() in ("1", "true", "yes", "y", "on")

    def post(self, request):
        # 로그인 확인
        user = get_login_user(request)
        if user is None:
            return JsonResponse({"detail": "로그인이 필요합니다."}, status=401)

        # JSON 파싱
        try:
            body = request.body.decode("utf-8") or "{}"
            data = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return JsonResponse({"detail": "JSON 파싱 오류"}, status=400)

        # year / semester / is_shared 꺼내기
        try:
            year = int(data.get("year"))
            semester = int(data.get("semester"))
        except (TypeError, ValueError):
            return JsonResponse({"detail": "year/semester 형식 오류"}, status=400)

        if "is_shared" not in data:
            return JsonResponse({"detail": "is_shared 필드가 필요합니다."}, status=400)

        is_shared = self._parse_bool(data.get("is_shared"))

        # 해당 학기의 Timetable row들 전부 가져오기
        qs = Timetable.objects.filter(
            user=user,
            year=year,
            semester=semester,
        )

        if not qs.exists():
            return JsonResponse(
                {"detail": "해당 학기 시간표가 존재하지 않습니다."},
                status=404,
            )

        # is_shared 일괄 업데이트
        qs.update(is_shared=is_shared)

        return JsonResponse(
            {
                "success": True,
                "year": year,
                "semester": semester,
                "is_shared": is_shared,
            }
        )



def timetable_share_status(request):
    """
    GET /api/timetable/share-status/?year=2025&semester=2

    응답 예:
      { "is_shared": true }
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    user = get_login_user(request)
    if user is None:
        return JsonResponse({"detail": "로그인이 필요합니다."}, status=401)

    year = request.GET.get("year")
    semester = request.GET.get("semester")

    try:
        year = int(year)
        semester = int(semester)
    except (TypeError, ValueError):
        return JsonResponse({"detail": "year/semester 형식 오류"}, status=400)

    exists = Timetable.objects.filter(
        user=user,
        year=year,
        semester=semester,
        is_shared=True,
    ).exists()

    return JsonResponse({"is_shared": exists})

class WeeklyTimetableAPI(APIView):
    """
    메인페이지 오른쪽 '주간 시간표'용 API
    - 쿼리파라미터 term 예: ?term=2025-2
    - Timetable 테이블에서 현재 로그인 유저의 해당 학기 시간표를 읽어온다.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        term = request.GET.get("term")
        if not term:
            return Response(
                {"detail": "term 파라미터가 필요합니다. 예: ?term=2025-2"},
                status=400,
            )

        # "2025-2" → year=2025, semester=2
        try:
            year_str, sem_str = term.split("-")
            year = int(year_str)
            semester = int(sem_str)
        except ValueError:
            return Response(
                {"detail": "term 형식이 잘못되었습니다. 예: 2025-2"},
                status=400,
            )

        # 이 학기의 내 시간표 행들을 가져오기
        qs = Timetable.objects.filter(
            user=request.user,
            year=year,
            semester=semester,
        )

        # 메인페이지 JS가 쓰는 포맷으로 변환
        lectures = []
        for row in qs:
            # 교시(1~9)를 메인페이지 시간(9~17시)로 변환
            start_hour = 8 + row.period   # 1교시 → 9, 2교시 → 10 ...
            end_hour = start_hour + 1     # 한 칸(1교시)짜리로 처리

            lectures.append({
                "name": row.subject,
                "day": row.day,           # "MON", "TUE", ...
                "start": start_hour,      # 예: 11
                "end": end_hour,          # 예: 12
                "location": row.classroom or "",
            })

        return Response({
            "term": term,
            "lectures": lectures,
        })

@method_decorator(csrf_exempt, name="dispatch")
class SaveTimetableAPI(APIView):
    """
    시간표 저장 API
    POST /api/timetable/save/

    요청 JSON 예시:
    {
      "term": "2025-2",
      "lectures": [
        {"day": "MON", "start": 10, "end": 12, "name": "자료구조", "location": "창조관"},
        ...
      ]
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        term = request.data.get("term")
        lectures = request.data.get("lectures", [])

        if not term:
            return Response({"detail": "term 값이 필요합니다."}, status=400)

        # 1) 기존에 저장되어 있던 해당 학기 시간표 싹 지우고
        TimetableEntry.objects.filter(user=request.user, term=term).delete()

        # 2) 새롭게 넣기
        new_entries = []
        for lec in lectures:
            new_entries.append(
                TimetableEntry(
                    user=request.user,
                    term=term,
                    day=lec.get("day"),
                    start=lec.get("start"),
                    end=lec.get("end"),
                    name=lec.get("name", ""),
                    location=lec.get("location", ""),
                )
            )

        TimetableEntry.objects.bulk_create(new_entries)

        return Response({"detail": "시간표가 저장되었습니다.", "count": len(new_entries)})
