from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"coe-notices", COENoticeViewSet, basename="coe-notice")
router.register(
    r"archived-coe-notices", ArchiveCOENoticeViewSet, basename="archived-coe-notice"
)

router.register(
    r"mphil-viva-voce-dates", MPHILVivaVoceDateViewSet, basename="mphil-viva-voce-date"
)
router.register(
    r"archived-mphil-viva-voce-dates",
    ArchiveMPHILVivaVoceDateViewSet,
    basename="archived-mphil-viva-voce-date",
)

router.register(
    r"phd-viva-voce-dates", PHDVivaVoceDateViewSet, basename="phd-viva-voce-date"
)
router.register(
    r"archived-phd-viva-voce-dates",
    ArchivePHDVivaVoceDateViewSet,
    basename="archived-phd-viva-voce-date",
)

router.register(
    r"phd-pre-submission-seminars",
    PHDPreSubmissionSeminarViewSet,
    basename="phd-pre-submission-seminar",
)
router.register(
    r"archived-phd-pre-submission-seminars",
    ArchivePHDPreSubmissionSeminarViewSet,
    basename="archived-phd-pre-submission-seminar",
)

router.register(r"rdcu-notices", RDCUNoticeViewSet, basename="rdcu-notice")
router.register(
    r"archived-rdcu-notices", ArchiveRDCUNoticeViewSet, basename="archived-rdcu-notice"
)

urlpatterns = [
    path("", include(router.urls)),
]
