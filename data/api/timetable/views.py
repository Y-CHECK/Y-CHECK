from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response

class CurrentTimetableAPI(APIView):
    def get(self, request):
        return Response({
            "year": 2025,
            "semester": "Fall",
            "grid": [
                {"day": "Mon", "slots": [
                    {"period": 2, "code": "SWE2009", "title": "웹프로그래밍"},
                ]},
                {"day": "Wed", "slots": [
                    {"period": 3, "code": "SWE2001", "title": "자료구조"},
                ]},
                {"day": "Thu", "slots": [
                    {"period": 5, "code": "SWE2007", "title": "알고리즘기초"},
                ]},
            ],
        })
