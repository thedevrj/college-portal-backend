from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters

from .models import (
    AdmissionSession,
    AdmissionUpdate,
    AdmissionBrochure,
    AdmissionSchedule,
    AdmissionContact,
    AdmissionLink,
    AdmissionMeritList,
    AdmissionCommitteeMember,
    AdmissionCommitteeMinutes,
)
from rest_framework import permissions
from .serializers import (
    AdmissionSessionSerializer,
    AdmissionUpdateSerializer,
    AdmissionBrochureSerializer,
    AdmissionScheduleSerializer,
    AdmissionContactSerializer,
    AdmissionLinkSerializer,
    AdmissionMeritListSerializer,
    AdmissionCommitteeMemberSerializer,
    AdmissionCommitteeMinutesSerializer,
)


class AdmissionSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionSession.objects.filter(is_active=True)
    serializer_class = AdmissionSessionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["session_name"]
    pagination_class = None


class AdmissionUpdateFilter(django_filters.FilterSet):
    class Meta:
        model = AdmissionUpdate
        fields = ["session", "category"]


class AdmissionUpdateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionUpdate.objects.filter(is_active=True).select_related("session")
    serializer_class = AdmissionUpdateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AdmissionUpdateFilter
    search_fields = ["title", "description"]


class AdmissionMeritListFilter(django_filters.FilterSet):
    class Meta:
        model = AdmissionMeritList
        fields = ["session", "category"]


class AdmissionMeritListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionMeritList.objects.filter(is_active=True).select_related(
        "session"
    )
    serializer_class = AdmissionMeritListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AdmissionMeritListFilter
    search_fields = ["title", "description"]


class AdmissionBrochureFilter(django_filters.FilterSet):
    class Meta:
        model = AdmissionBrochure
        fields = ["session", "category"]


class AdmissionBrochureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionBrochure.objects.filter(is_active=True).select_related(
        "session"
    )
    serializer_class = AdmissionBrochureSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AdmissionBrochureFilter
    search_fields = ["title"]


class AdmissionScheduleFilter(django_filters.FilterSet):
    class Meta:
        model = AdmissionSchedule
        fields = ["session", "category"]


class AdmissionScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionSchedule.objects.filter(is_active=True).select_related(
        "session"
    )
    serializer_class = AdmissionScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AdmissionScheduleFilter
    search_fields = ["event_name"]


class AdmissionContactFilter(django_filters.FilterSet):
    class Meta:
        model = AdmissionContact
        fields = ["session", "category"]


class AdmissionContactViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionContact.objects.select_related("session")
    serializer_class = AdmissionContactSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AdmissionContactFilter
    search_fields = ["name", "designation"]
    pagination_class = None


class AdmissionLinkFilter(django_filters.FilterSet):
    class Meta:
        model = AdmissionLink
        fields = ["session", "category"]


class AdmissionLinkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionLink.objects.filter(is_active=True).select_related("session")
    serializer_class = AdmissionLinkSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AdmissionLinkFilter
    search_fields = ["title"]
    pagination_class = None


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
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            qs = qs.filter(is_private=False)
        return qs
