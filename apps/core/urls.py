from django.urls import path
from .views import health, schools

urlpatterns = [
    path("health/", health),
    path("schools/", schools),
]