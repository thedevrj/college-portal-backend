from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GlobalNoticeViewSet, ArchivedGlobalNoticeViewSet

router = DefaultRouter()
router.register(r'archived-global-notices', ArchivedGlobalNoticeViewSet, basename='archivedglobalnotice')
router.register(r'global-notices', GlobalNoticeViewSet, basename='globalnotice')

urlpatterns = [
    path('', include(router.urls)),
]
