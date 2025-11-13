from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response

class MainSummaryAPI(APIView):
    def get(self, request):
        return Response({
            "overall": {"earned": 87, "required": 130, "rate": 66.9},
            "groups": [
                {"name": "전공필수", "earned": 24, "required": 30, "lack": 6},
                {"name": "전공선택", "earned": 33, "required": 42, "lack": 9},
                {"name": "교양-인문", "earned": 3, "required": 6, "lack": 3},
            ],
        })
