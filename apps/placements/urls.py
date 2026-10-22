from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlacementNoticeViewSet, ArchivePlacementNoticeViewSet


router = DefaultRouter()
router.register("placement-notices", PlacementNoticeViewSet, basename="placement-notice")
router.register("archived-placement-notices", ArchivePlacementNoticeViewSet, basename="archived-placement-notice")
urlpatterns = [
    path("", include(router.urls)),
]
