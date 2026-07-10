from rest_framework import viewsets, permissions
from .models import (
    BoardOfManagementMember,
    BoardOfManagementMinutes,
    AcademicCouncilMember,
    AcademicCouncilMinutes,
    PlanningBoardMember,
    PlanningBoardMinutes,
    FinanceCommitteeMember,
    FinanceCommitteeMinutes,
)
from .serializers import (
    BoardOfManagementMemberSerializer,
    BoardOfManagementMinutesSerializer,
    AcademicCouncilMemberSerializer,
    AcademicCouncilMinutesSerializer,
    PlanningBoardMemberSerializer,
    PlanningBoardMinutesSerializer,
    FinanceCommitteeMemberSerializer,
    FinanceCommitteeMinutesSerializer,
)


# --- Board of Management (BoM) ViewSets ---

class BoardOfManagementMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BoardOfManagementMember.objects.all()
    serializer_class = BoardOfManagementMemberSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = None


class BoardOfManagementMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BoardOfManagementMinutes.objects.all()
    serializer_class = BoardOfManagementMinutesSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = None


# --- Academic Council ViewSets ---

class AcademicCouncilMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AcademicCouncilMember.objects.all()
    serializer_class = AcademicCouncilMemberSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = None


class AcademicCouncilMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AcademicCouncilMinutes.objects.all()
    serializer_class = AcademicCouncilMinutesSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = None


# --- Planning Board ViewSets ---

class PlanningBoardMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlanningBoardMember.objects.all()
    serializer_class = PlanningBoardMemberSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = None


class PlanningBoardMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlanningBoardMinutes.objects.all()
    serializer_class = PlanningBoardMinutesSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = None


# --- Finance Committee ViewSets ---

class FinanceCommitteeMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinanceCommitteeMember.objects.all()
    serializer_class = FinanceCommitteeMemberSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = None


class FinanceCommitteeMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinanceCommitteeMinutes.objects.all()
    serializer_class = FinanceCommitteeMinutesSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = None
