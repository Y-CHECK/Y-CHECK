from django.urls import path
from . import views

urlpatterns = [
    # 1) 졸업요건 계산 API
    path("calculate/", views.calculate_graduation, name="calculate_graduation"),

    # 2) 전체 과목 목록 조회
    path("courses/", views.get_courses, name="get_courses"),

    # 3) 로그인한 유저의 수강 과목 조회
    path("taken-courses/", views.get_taken_courses, name="get_taken_courses"),

    # 4) 로그인한 유저의 학점 요약
    path("credit-summary/", views.get_credit_summary, name="credit_summary"),

    # ✅ 5) 계산기에서 체크한 과목 저장 (NEW)
    path("taken-courses/save/", views.save_taken_courses, name="save_taken_courses"),
]
