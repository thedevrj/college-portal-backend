from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BoardOfManagementMemberViewSet,
    BoardOfManagementMinutesViewSet,
    AcademicCouncilMemberViewSet,
    AcademicCouncilMinutesViewSet,
    PlanningBoardMemberViewSet,
    PlanningBoardMinutesViewSet,
    FinanceCommitteeMemberViewSet,
    FinanceCommitteeMinutesViewSet,
)

router = DefaultRouter()
router.register(r"board-of-management-members", BoardOfManagementMemberViewSet)
router.register(r"board-of-management-minutes", BoardOfManagementMinutesViewSet)
router.register(r"academic-council-members", AcademicCouncilMemberViewSet)
router.register(r"academic-council-minutes", AcademicCouncilMinutesViewSet)
router.register(r"planning-board-members", PlanningBoardMemberViewSet)
router.register(r"planning-board-minutes", PlanningBoardMinutesViewSet)
router.register(r"finance-committee-members", FinanceCommitteeMemberViewSet)
router.register(r"finance-committee-minutes", FinanceCommitteeMinutesViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
