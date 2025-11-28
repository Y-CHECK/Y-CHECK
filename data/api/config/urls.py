"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    # --------------------------
    # 기존 백엔드 기능 유지
    # --------------------------
    path('admin/', admin.site.urls),
    path('api/curriculum/', include('curriculum.urls')),
    path('', include('users.urls')),   # 로그인, 회원가입 등 그대로 유지

    # --------------------------
    # 🔥 HTML 파일 라우팅 추가
    # (/data/web/html/ 에 있는 파일들)
    # --------------------------

    # 메인 화면
    path('main/', TemplateView.as_view(template_name="main.html"), name="main"),

    # 로그인 / 회원가입
    path('login/', TemplateView.as_view(template_name="login.html"), name="login"),
    path('register/', TemplateView.as_view(template_name="register.html"), name="register"),

    # 마이페이지
    path('mypage/', TemplateView.as_view(template_name="mypage.html"), name="mypage"),

    # 선배 발자취
    path('sunbae/', TemplateView.as_view(template_name="sunbae.html"), name="sunbae"),

    # 시간표
    path('timetable/', TemplateView.as_view(template_name="timetable.html"), name="timetable"),

    # 졸업요건 계산기
    path('calculator/', TemplateView.as_view(template_name="calculator.html"), name="calculator"),
]
