from django.urls import path
from .views import SeniorListAPI

urlpatterns = [
    path("", SeniorListAPI.as_view()),
]
