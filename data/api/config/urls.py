"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
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

    path('', include('users.urls')),  # /api/register/ 같은 URL 여기로 연결
    path("api/timetable/", include("timetable.urls")),
    path("api/footprints/", include("footprints.urls")),
]
