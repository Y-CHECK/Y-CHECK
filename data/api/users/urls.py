from django.urls import path
from .register import register_api
from .login import login_api
from .mypage import mypage_api   # ✅ 방금 만든 함수

urlpatterns = [
    path("api/register/", register_api, name="api-register"),
    path("api/login/", login_api, name="api-login"),
    path("api/mypage/", mypage_api, name="api-mypage"),  # ✅ 마이페이지 API
]