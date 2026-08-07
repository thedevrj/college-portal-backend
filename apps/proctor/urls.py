from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProctorialBoardMemberViewSet,
    ProctorialBoardMinutesViewSet,
    ArchivedProctorialBoardMinutesViewSet,
    ProctorialBoardNoticeViewSet,
    ArchivedProctorialBoardNoticeViewSet,
)

router = DefaultRouter()
router.register(r"proctorial-board-members", ProctorialBoardMemberViewSet, basename="proctorial-board-member")
router.register(r"proctorial-board-minutes", ProctorialBoardMinutesViewSet, basename="proctorial-board-minutes")
router.register(r"archived-proctorial-board-minutes", ArchivedProctorialBoardMinutesViewSet, basename="archived-proctorial-board-minutes")
router.register(r"proctorial-board-notices", ProctorialBoardNoticeViewSet, basename="proctorial-board-notices")
router.register(r"archived-proctorial-board-notices", ArchivedProctorialBoardNoticeViewSet, basename="archived-proctorial-board-notices")

urlpatterns = [
    path("", include(router.urls)),
]
