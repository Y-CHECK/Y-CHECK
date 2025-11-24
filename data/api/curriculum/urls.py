from django.urls import path
from . import views

urlpatterns = [
    # POST /api/curriculum/calculate/
    path("calculate/", views.calculate_graduation, name="calculate_graduation"),

    # GET /api/curriculum/courses/
    path("courses/", views.get_courses, name="get_courses"),
]