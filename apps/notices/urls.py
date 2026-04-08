from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GlobalNoticeViewSet

router = DefaultRouter()
router.register(r'global-notices', GlobalNoticeViewSet, basename='globalnotice')

urlpatterns = [
    path('', include(router.urls)),
]
