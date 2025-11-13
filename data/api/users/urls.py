from django.urls import path
from .register import register_api
from . import mypage

urlpatterns = [
    path('api/register/', register_api, name='api-register'),
    path("mypage/", mypage.mypage_view, name="mypage"),
]
