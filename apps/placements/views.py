from rest_framework import viewsets, permissions
from .models import PlacementNotice
from .serializers import PlacementNoticeSerializer
from django.utils import timezone
from django.db.models import Q


class PlacementNoticeViewSet(viewsets.ModelViewSet):
    queryset = PlacementNotice.objects.all().order_by("-date")
    serializer_class = PlacementNoticeSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        today = timezone.now().date()
        return PlacementNotice.objects.exclude(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )


class ArchivePlacementNoticeViewSet(viewsets.ModelViewSet):
    queryset = PlacementNotice.objects.filter(is_archived=True).order_by("-date")
    serializer_class = PlacementNoticeSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        today = timezone.now().date()
        return PlacementNotice.objects.filter(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )