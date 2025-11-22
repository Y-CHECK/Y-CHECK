from django.urls import path
from .views import (
    TimetableSemestersAPI,
    TimetableBySemesterAPI,
    CourseSearchAPI,
    TimetableAddCourseAPI,
)

urlpatterns = [
    path("semesters/", TimetableSemestersAPI.as_view(), name="timetable-semesters"),
    path("", TimetableBySemesterAPI.as_view(), name="timetable-by-semester"),
    path("courses/", CourseSearchAPI.as_view(), name="timetable-course-search"),
    path("add-course/", TimetableAddCourseAPI.as_view(), name="timetable-add-course"),
]
