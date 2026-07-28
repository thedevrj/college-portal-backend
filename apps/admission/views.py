from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters

from .models import (
    AdmissionSession,
    AdmissionStream,
    AdmissionProspectus,
    AdmissionNotice,
    RegistrationPortal,
    CounsellingPhase,
    MeritList,
    AdmissionCommitteeMember,
    AdmissionCommitteeMinutes,
)

from .serializers import (
    AdmissionSessionSerializer,
    AdmissionStreamSerializer,
    AdmissionProspectusSerializer,
    AdmissionNoticeSerializer,
    RegistrationPortalSerializer,
    CounsellingPhaseSerializer,
    MeritListSerializer,
    AdmissionCommitteeMemberSerializer,
    AdmissionCommitteeMinutesSerializer,
)


class AdmissionSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionSession.objects.filter(is_active=True)
    serializer_class = AdmissionSessionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["session_name"]
    pagination_class = None


class AdmissionStreamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionStream.objects.filter(is_active=True).select_related("session")
    serializer_class = AdmissionStreamSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["session", "category"]
    search_fields = ["name"]
    pagination_class = None


class AdmissionProspectusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionProspectus.objects.select_related("session")
    serializer_class = AdmissionProspectusSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["session", "category"]
    search_fields = ["title"]


class AdmissionNoticeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AdmissionNoticeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["session", "category"]
    search_fields = ["title"]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q

        today = timezone.now().date()
        return (
            AdmissionNotice.objects.filter(is_active=True)
            .select_related("session")
            .exclude(Q(is_archived=True) | Q(archive_date__lt=today))
        )


class RegistrationPortalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RegistrationPortal.objects.filter(is_active=True).select_related(
        "session"
    )
    serializer_class = RegistrationPortalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["session", "category"]
    search_fields = ["portal_name"]
    pagination_class = None


class CounsellingPhaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CounsellingPhase.objects.filter(is_active=True).select_related("stream")
    serializer_class = CounsellingPhaseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["stream", "stream__session", "stream__category"]
    search_fields = ["phase_name"]
    pagination_class = None


class MeritListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MeritList.objects.select_related(
        "phase", "phase__stream", "phase__stream__session", "department", "programme"
    )
    serializer_class = MeritListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        "phase",
        "phase__stream",
        "phase__stream__category",
        "department",
        "programme",
    ]
    search_fields = ["department__name", "programme__name"]


# --- Admission Committee ViewSets ---


class AdmissionCommitteeMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionCommitteeMember.objects.all()
    serializer_class = AdmissionCommitteeMemberSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = None


class AdmissionCommitteeMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionCommitteeMinutes.objects.all()
    serializer_class = AdmissionCommitteeMinutesSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = None

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q

        qs = AdmissionCommitteeMinutes.objects.all()
        today = timezone.now().date()
        qs = qs.exclude(Q(is_archived=True) | Q(archive_date__lt=today))

        if not self.request.user.is_authenticated:
            qs = qs.filter(is_private=False)
        return qs
