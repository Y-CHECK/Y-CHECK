"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # ======================================================
    # 1) Django Admin
    # ======================================================
    path('admin/', admin.site.urls),


    # ======================================================
    # 2) API 라우트 (백엔드 기능)
    # ======================================================

    # 사용자 관련 API (회원가입/로그인 등)
    path('', include('users.urls')),

    # 교과목 API
    path('api/curriculum/', include('curriculum.urls')),

    # 시간표 API
    path("api/timetable/", include("timetable.urls")),

    # 선배 발자취 API
    path("api/footprints/", include("footprints.urls")),


    # ======================================================
    # 3) HTML 페이지 라우트
    #    (web/html 내부의 정적 HTML 랜더링)
    # ======================================================

    # 메인 페이지
    path('main/', TemplateView.as_view(template_name="main.html"), name="main"),

    # 로그인 / 회원가입 페이지
    path('login/', TemplateView.as_view(template_name="login.html"), name="login"),
    path('register/', TemplateView.as_view(template_name="register.html"), name="register"),

    # 마이페이지
    path('mypage/', TemplateView.as_view(template_name="mypage.html"), name="mypage"),

    # 선배 발자취 페이지
    path('sunbae/', TemplateView.as_view(template_name="sunbae.html"), name="sunbae"),

    # 시간표 페이지
    path('timetable/', TemplateView.as_view(template_name="timetable.html"), name="timetable"),

    # 졸업요건 계산기
    path('calculator/', TemplateView.as_view(template_name="calculator.html"), name="calculator"),
]
