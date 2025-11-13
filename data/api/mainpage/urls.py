from django.urls import path
from .views import MainSummaryAPI

urlpatterns = [
    path("summary/", MainSummaryAPI.as_view()),
]
