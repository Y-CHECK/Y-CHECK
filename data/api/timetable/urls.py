from django.urls import path

from .views import (
    TimetableListCreateAPI,
    SemesterListAPI,
    CourseSearchAPI,
    AddCourseAPI,
    TimetableShareToggleAPI,
    timetable_share_status,
)

urlpatterns = [
    path("", TimetableListCreateAPI.as_view(), name="timetable-list"),
    path("semesters/", SemesterListAPI.as_view(), name="timetable-semesters"),
    path("courses/", CourseSearchAPI.as_view(), name="timetable-courses"),
    path("add-course/", AddCourseAPI.as_view(), name="timetable-add-course"),
    path("share/", TimetableShareToggleAPI.as_view(), name="timetable-share"),
    path("share-status/", timetable_share_status, name="timetable-share-status"),
]
