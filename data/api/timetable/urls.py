# timetable/urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import (
    TimetableListCreateAPI,
    SemesterListAPI,
    CourseSearchAPI,
    AddCourseAPI,
    TimetableShareToggleAPI,
    timetable_share_status,
    WeeklyTimetableAPI,
    SaveTimetableAPI,
)

urlpatterns = [
    path("", TimetableListCreateAPI.as_view(), name="timetable-list"),
    path("semesters/", SemesterListAPI.as_view(), name="timetable-semesters"),
    path("courses/", CourseSearchAPI.as_view(), name="timetable-courses"),
    path("add-course/", AddCourseAPI.as_view(), name="timetable-add-course"),
    path("share/", TimetableShareToggleAPI.as_view(), name="timetable-share"),
    path("share-status/", timetable_share_status, name="timetable-share-status"),
    path("weekly/", WeeklyTimetableAPI.as_view()),
    path("save/", csrf_exempt(SaveTimetableAPI.as_view())),
]
