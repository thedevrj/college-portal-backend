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


class BoardOfManagementMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BoardOfManagementMinutesSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q
        today = timezone.now().date()
        return BoardOfManagementMinutes.objects.exclude(Q(is_archived=True) | Q(archive_date__lt=today))


class ArchivedBoardOfManagementMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BoardOfManagementMinutesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q
        today = timezone.now().date()
        return BoardOfManagementMinutes.objects.filter(Q(is_archived=True) | Q(archive_date__lt=today))


# --- Academic Council ViewSets ---


class AcademicCouncilMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AcademicCouncilMember.objects.all()
    serializer_class = AcademicCouncilMemberSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class AcademicCouncilMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AcademicCouncilMinutesSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q
        today = timezone.now().date()
        return AcademicCouncilMinutes.objects.exclude(Q(is_archived=True) | Q(archive_date__lt=today))


class ArchivedAcademicCouncilMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AcademicCouncilMinutesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q
        today = timezone.now().date()
        return AcademicCouncilMinutes.objects.filter(Q(is_archived=True) | Q(archive_date__lt=today))


# --- Planning Board ViewSets ---


class PlanningBoardMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlanningBoardMember.objects.all()
    serializer_class = PlanningBoardMemberSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class PlanningBoardMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlanningBoardMinutesSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q
        today = timezone.now().date()
        return PlanningBoardMinutes.objects.exclude(Q(is_archived=True) | Q(archive_date__lt=today))


class ArchivedPlanningBoardMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlanningBoardMinutesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q
        today = timezone.now().date()
        return PlanningBoardMinutes.objects.filter(Q(is_archived=True) | Q(archive_date__lt=today))


# --- Finance Committee ViewSets ---


class FinanceCommitteeMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinanceCommitteeMember.objects.all()
    serializer_class = FinanceCommitteeMemberSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class FinanceCommitteeMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FinanceCommitteeMinutesSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q
        today = timezone.now().date()
        return FinanceCommitteeMinutes.objects.exclude(Q(is_archived=True) | Q(archive_date__lt=today))


class ArchivedFinanceCommitteeMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FinanceCommitteeMinutesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q
        today = timezone.now().date()
        return FinanceCommitteeMinutes.objects.filter(Q(is_archived=True) | Q(archive_date__lt=today))
