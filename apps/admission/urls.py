from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AdmissionSessionViewSet,
    AdmissionUpdateViewSet,
    AdmissionBrochureViewSet,
    AdmissionScheduleViewSet,
    AdmissionContactViewSet,
    AdmissionLinkViewSet,
    AdmissionMeritListViewSet,
)

router = DefaultRouter()
router.register(r"sessions", AdmissionSessionViewSet, basename="admission-sessions")
router.register(r"updates", AdmissionUpdateViewSet, basename="admission-updates")
router.register(r"merit-lists", AdmissionMeritListViewSet, basename="admission-merit-lists")
router.register(r"brochures", AdmissionBrochureViewSet, basename="admission-brochures")
router.register(r"schedules", AdmissionScheduleViewSet, basename="admission-schedules")
router.register(r"contacts", AdmissionContactViewSet, basename="admission-contacts")
router.register(r"links", AdmissionLinkViewSet, basename="admission-links")

urlpatterns = [
    path("", include(router.urls)),
]
