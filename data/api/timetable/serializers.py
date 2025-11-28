# timetable/serializers.py
from rest_framework import serializers
from .models import Timetable, Course


class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = [
            "id",
            "year",
            "semester",
            "day",
            "period",
            "subject",
            "classroom",
            "memo",
            "is_shared",  # 공유 여부
        ]


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"
