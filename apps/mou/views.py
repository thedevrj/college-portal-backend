from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import MOU
from .serializers import MOUSerializer


class MOUFilter(django_filters.FilterSet):
    mou_date = django_filters.DateFromToRangeFilter(field_name="date_of_signing")


from django.utils import timezone
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

class MOUViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MOUSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = MOUFilter
    search_fields = ["organization_name", "Nature_of_organization"]
    ordering_fields = ["date_of_signing"]
    ordering = ["-date_of_signing"]

    def get_queryset(self):
        today = timezone.now().date()
        return MOU.objects.filter(is_deleted=False).exclude(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )

class ArchivedMOUViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Archived MOUs to be viewed.
    Only authenticated members (staff/faculty) can access this endpoint.
    """
    serializer_class = MOUSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = MOUFilter
    search_fields = ["organization_name", "Nature_of_organization"]
    ordering_fields = ["date_of_signing"]
    ordering = ["-date_of_signing"]

    def get_queryset(self):
        today = timezone.now().date()
        return MOU.objects.filter(is_deleted=False).filter(
            Q(is_archived=True) | Q(archive_date__lt=today)
        )

