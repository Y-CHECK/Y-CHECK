from django.urls import path
from .register import register_api
from .login import login_api
from .mypage import mypage_api
from .logout import logout_api

urlpatterns = [
    path("api/register/", register_api, name="api-register"),
    path("api/login/", login_api, name="api-login"),
    path("api/mypage/", mypage_api, name="api-mypage"),
    path("api/logout/", logout_api, name="api-logout"),  # ← 통일!
]
