from rest_framework import viewsets, permissions
from .models import (
    COENotice,
    PHDPreSubmissionSeminar,
    RDCUNotice,
    MPHILVivaVoceDate,
    PHDVivaVoceDate,
)
from .serializers import (
    COENoticeSerializer,
    PHDPreSubmissionSeminarSerializer,
    RDCUNoticeSerializer,
    MPHILVivaVoceDateSerializer,
    PHDVivaVoceDateSerializer,
)


class COENoticeViewSet(viewsets.ModelViewSet):
    queryset = COENotice.objects.all().order_by("-date")
    serializer_class = COENoticeSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q

        today = timezone.now().date()
        return COENotice.objects.exclude(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )

class ArchiveCOENoticeViewSet(viewsets.ModelViewSet):
    queryset = COENotice.objects.filter(is_archived=True).order_by("-date")
    serializer_class = COENoticeSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q

        today = timezone.now().date()
        return COENotice.objects.filter(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )

class PHDVivaVoceDateViewSet(viewsets.ModelViewSet):
    queryset = PHDVivaVoceDate.objects.all().order_by("-date")
    serializer_class = PHDVivaVoceDateSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q

        today = timezone.now().date()
        return PHDVivaVoceDate.objects.exclude(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )

class ArchivePHDVivaVoceDateViewSet(viewsets.ModelViewSet):
    queryset = PHDVivaVoceDate.objects.all().order_by("-date")
    serializer_class = PHDVivaVoceDateSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q

        today = timezone.now().date()
        return PHDVivaVoceDate.objects.filter(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )

class MPHILVivaVoceDateViewSet(viewsets.ModelViewSet):
    queryset = MPHILVivaVoceDate.objects.all().order_by("-date")
    serializer_class = MPHILVivaVoceDateSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q

        today = timezone.now().date()
        return MPHILVivaVoceDate.objects.exclude(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )

class ArchiveMPHILVivaVoceDateViewSet(viewsets.ModelViewSet):
    queryset = MPHILVivaVoceDate.objects.all().order_by("-date")
    serializer_class = MPHILVivaVoceDateSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q

        today = timezone.now().date()
        return MPHILVivaVoceDate.objects.filter(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )

class PHDPreSubmissionSeminarViewSet(viewsets.ModelViewSet):
    queryset = PHDPreSubmissionSeminar.objects.all().order_by("-date")
    serializer_class = PHDPreSubmissionSeminarSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q

        today = timezone.now().date()
        return PHDPreSubmissionSeminar.objects.exclude(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )

class ArchivePHDPreSubmissionSeminarViewSet(viewsets.ModelViewSet):
    queryset = PHDPreSubmissionSeminar.objects.all().order_by("-date")
    serializer_class = PHDPreSubmissionSeminarSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q

        today = timezone.now().date()
        return PHDPreSubmissionSeminar.objects.filter(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )

class RDCUNoticeViewSet(viewsets.ModelViewSet):
    queryset = RDCUNotice.objects.all().order_by("-date")
    serializer_class = RDCUNoticeSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q

        today = timezone.now().date()
        return RDCUNotice.objects.exclude(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )


class ArchiveRDCUNoticeViewSet(viewsets.ModelViewSet):
    queryset = RDCUNotice.objects.all().order_by("-date")
    serializer_class = RDCUNoticeSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        from django.utils import timezone
        from django.db.models import Q

        today = timezone.now().date()
        return RDCUNotice.objects.filter(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )