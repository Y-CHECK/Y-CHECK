from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response

class SeniorListAPI(APIView):
    def get(self, request):
        return Response({
            "results": [
                {"id": 12, "display_name": "익명선배A", "track": "AI", "entrance_year": 2021},
                {"id": 27, "display_name": "익명선배B", "track": "Security", "entrance_year": 2020},
            ]
        })
