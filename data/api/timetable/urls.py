# timetable/urls.py
from django.urls import path
from .views import timetable_semesters, timetable_list

urlpatterns = [
    path("semesters/", timetable_semesters, name="timetable-semesters"),
    path("", timetable_list, name="timetable-list"),
]
