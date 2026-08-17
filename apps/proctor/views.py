from rest_framework import viewsets, permissions
from .models import ProctorialBoardMember, ProctorialBoardMinutes, ProctorialBoardNotice
from .serializers import (
    ProctorialBoardMemberSerializer,
    ProctorialBoardMinutesSerializer,
    ProctorialBoardNoticeSerializer,
)


class ProctorialBoardMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProctorialBoardMember.objects.all()
    serializer_class = ProctorialBoardMemberSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class ProctorialBoardMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProctorialBoardMinutesSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q
        today = timezone.now().date()
        return ProctorialBoardMinutes.objects.exclude(Q(is_archived=True) | Q(archive_date__lt=today))


class ArchivedProctorialBoardMinutesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProctorialBoardMinutesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q
        today = timezone.now().date()
        return ProctorialBoardMinutes.objects.filter(Q(is_archived=True) | Q(archive_date__lt=today))


class ProctorialBoardNoticeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProctorialBoardNoticeSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q
        today = timezone.now().date()
        return ProctorialBoardNotice.objects.exclude(Q(is_archived=True) | Q(archive_date__lt=today))


class ArchivedProctorialBoardNoticeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProctorialBoardNoticeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q
        today = timezone.now().date()
        return ProctorialBoardNotice.objects.filter(Q(is_archived=True) | Q(archive_date__lt=today))
