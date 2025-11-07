from django.urls import path
from .register import register_api

urlpatterns = [
    path('api/register/', register_api, name='api-register'),
]
