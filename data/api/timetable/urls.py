from django.urls import path
from .views import TimetableSemestersAPI, TimetableBySemesterAPI

urlpatterns = [
    path("semesters/", TimetableSemestersAPI.as_view(), name="timetable-semesters"),
    path("", TimetableBySemesterAPI.as_view(), name="timetable-by-semester"),
]
