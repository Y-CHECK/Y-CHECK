# data/api/mainpage/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("track-recommend/", views.track_recommend, name="track_recommend"),
]
