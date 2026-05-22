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
    AdmissionCommitteeMemberViewSet,
    AdmissionCommitteeMinutesViewSet,
)

router = DefaultRouter()
router.register(r"sessions", AdmissionSessionViewSet, basename="admission-sessions")
router.register(r"updates", AdmissionUpdateViewSet, basename="admission-updates")
router.register(r"merit-lists", AdmissionMeritListViewSet, basename="admission-merit-lists")
router.register(r"brochures", AdmissionBrochureViewSet, basename="admission-brochures")
router.register(r"schedules", AdmissionScheduleViewSet, basename="admission-schedules")
router.register(r"contacts", AdmissionContactViewSet, basename="admission-contacts")
router.register(r"links", AdmissionLinkViewSet, basename="admission-links")
router.register(r"committee-members", AdmissionCommitteeMemberViewSet, basename="admission-committee-members")
router.register(r"committee-minutes", AdmissionCommitteeMinutesViewSet, basename="admission-committee-minutes")

urlpatterns = [
    path("", include(router.urls)),
]
