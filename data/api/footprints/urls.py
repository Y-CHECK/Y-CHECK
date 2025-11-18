from django.urls import path
from . import views

urlpatterns = [
    path("filters/", views.filters, name="footprints-filters"),
    path("seniors/", views.seniors, name="footprints-seniors"),
    path("seniors/<int:senior_id>/records/", views.senior_records, name="footprints-records"),
]
