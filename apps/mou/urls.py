from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MOUViewSet

router = DefaultRouter()
router.register(r'mous', MOUViewSet, basename='mou')

urlpatterns = [
    path('', include(router.urls)),
]
