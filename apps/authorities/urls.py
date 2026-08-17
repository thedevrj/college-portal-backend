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
    ArchivedBoardOfManagementMinutesViewSet,
    ArchivedAcademicCouncilMinutesViewSet,
    ArchivedPlanningBoardMinutesViewSet,
    ArchivedFinanceCommitteeMinutesViewSet,
)

router = DefaultRouter()
router.register(r"board-of-management-members", BoardOfManagementMemberViewSet)
router.register(r"board-of-management-minutes", BoardOfManagementMinutesViewSet, basename="bom-minutes")
router.register(r"academic-council-members", AcademicCouncilMemberViewSet)
router.register(r"academic-council-minutes", AcademicCouncilMinutesViewSet, basename="ac-minutes")
router.register(r"planning-board-members", PlanningBoardMemberViewSet)
router.register(r"planning-board-minutes", PlanningBoardMinutesViewSet, basename="pb-minutes")
router.register(r"finance-committee-members", FinanceCommitteeMemberViewSet)
router.register(r"finance-committee-minutes", FinanceCommitteeMinutesViewSet, basename="fc-minutes")
router.register(r"archived-board-of-management-minutes", ArchivedBoardOfManagementMinutesViewSet, basename="archived-bom-minutes")
router.register(r"archived-academic-council-minutes", ArchivedAcademicCouncilMinutesViewSet, basename="archived-ac-minutes")
router.register(r"archived-planning-board-minutes", ArchivedPlanningBoardMinutesViewSet, basename="archived-pb-minutes")
router.register(r"archived-finance-committee-minutes", ArchivedFinanceCommitteeMinutesViewSet, basename="archived-fc-minutes")

urlpatterns = [
    path("", include(router.urls)),
]
