from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AdmissionSessionViewSet,
    AdmissionStreamViewSet,
    AdmissionProspectusViewSet,
    AdmissionNoticeViewSet,
    RegistrationPortalViewSet,
    CounsellingPhaseViewSet,
    MeritListViewSet,
    AdmissionCommitteeMemberViewSet,
    AdmissionCommitteeMinutesViewSet,
)

router = DefaultRouter()
router.register(r"sessions", AdmissionSessionViewSet, basename="admission-sessions")
router.register(r"streams", AdmissionStreamViewSet, basename="admission-streams")
router.register(r"prospectuses", AdmissionProspectusViewSet, basename="admission-prospectuses")
router.register(r"notices", AdmissionNoticeViewSet, basename="admission-notices")
router.register(r"registration-portals", RegistrationPortalViewSet, basename="admission-registration-portals")
router.register(r"counselling-phases", CounsellingPhaseViewSet, basename="admission-counselling-phases")
router.register(r"merit-lists", MeritListViewSet, basename="admission-merit-lists")
router.register(r"committee-members", AdmissionCommitteeMemberViewSet, basename="admission-committee-members")
router.register(r"committee-minutes", AdmissionCommitteeMinutesViewSet, basename="admission-committee-minutes")

urlpatterns = [
    path("", include(router.urls)),
]
