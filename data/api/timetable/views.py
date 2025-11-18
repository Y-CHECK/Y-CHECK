from rest_framework.views import APIView
from rest_framework.response import Response


class TimetableSemestersAPI(APIView):
    """
    시간표 페이지에서 학기 선택 드롭다운에 쓸 학기 목록
    TODO: 나중에 실제로 사용자가 가진 시간표 목록을 DB에서 가져오도록 변경
    """

    def get(self, request):
        semesters = [
            {"year": 2025, "term": 2, "label": "2025년 2학기"},
            {"year": 2025, "term": 1, "label": "2025년 1학기"},
            {"year": 2024, "term": 2, "label": "2024년 2학기"},
        ]
        return Response({"semesters": semesters})


class TimetableBySemesterAPI(APIView):
    """
    특정 학기의 시간표를 반환하는 API
    GET /api/timetable/?year=2025&term=2

    TODO:
      - 나중에 DB에서 해당 학기 시간표를 조회해서 반환하도록 변경
    """

    def get(self, request):
        year = int(request.GET.get("year", 2025))
        term = int(request.GET.get("term", 2))

        # 기본 요일/교시 (월~금, 1~9교시)
        days = ["월", "화", "수", "목", "금"]
        periods = list(range(1, 10))

        # TODO: 학기별로 DB에서 다른 내용 가져오기
        entries = []

        if year == 2025 and term == 2:
            entries = [
                {
                    "day": "월",
                    "period": 3,
                    "code": "SWE2003",
                    "title": "데이터구조론",
                }
            ]

        data = {
            "year": year,
            "term": term,
            "label": f"{year}년 {term}학기",
            "days": days,
            "periods": periods,
            "entries": entries,
        }
        return Response(data)
