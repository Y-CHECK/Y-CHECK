from django.urls import path
from .register import register_api
from .login import login_api
from .mypage import mypage_api
from .main import main_profile_api, main_summary_api

urlpatterns = [
    path("api/register/", register_api, name="api-register"),
    path("api/login/", login_api, name="api-login"),
    path("api/mypage/", mypage_api, name="api-mypage"),

    # 메인페이지용
    path("api/main/profile/", main_profile_api, name="api-main-profile"),
    path("api/main/summary/", main_summary_api, name="api-main-summary"),
]
