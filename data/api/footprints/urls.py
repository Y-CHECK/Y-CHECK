# footprints/urls.py
from django.urls import path
from .views import shared_timetables

urlpatterns = [
    path("timetables/", shared_timetables, name="shared-timetables"),
]
