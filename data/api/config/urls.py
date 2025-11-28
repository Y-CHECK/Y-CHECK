from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API
    path('api/curriculum/', include('curriculum.urls')),
    path('api/', include('mainpage.urls')),   # 🔥 이 줄

    # users 앱 (로그인/회원가입)
    path('', include('users.urls')),

    # HTML 라우팅 (필요하다면 유지)
    path('main/', TemplateView.as_view(template_name="main.html"), name="main"),
    path('login/', TemplateView.as_view(template_name="login.html"), name="login"),
    path('register/', TemplateView.as_view(template_name="register.html"), name="register"),
    path('mypage/', TemplateView.as_view(template_name="mypage.html"), name="mypage"),
    path('sunbae/', TemplateView.as_view(template_name="sunbae.html"), name="sunbae"),
    path('timetable/', TemplateView.as_view(template_name="timetable.html"), name="timetable"),
    path('calculator/', TemplateView.as_view(template_name="calculator.html"), name="calculator"),
]
