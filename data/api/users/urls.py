from django.urls import path
from .register import register_api
from .login import login_api   # 추가!!

urlpatterns = [
    path('api/register/', register_api, name='api-register'),
    path('api/login/', login_api, name='api-login'),  # 추가된 라우트
]