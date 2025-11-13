from django.urls import path
from .views import CurrentTimetableAPI

urlpatterns = [
    path("current/", CurrentTimetableAPI.as_view()),
]
