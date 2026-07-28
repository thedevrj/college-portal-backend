from rest_framework import viewsets
from django_filters import rest_framework as filters
from .models import GlobalNotice
from .serializers import GlobalNoticeListSerializer, GlobalNoticeDetailSerializer


class GlobalNoticeFilter(filters.FilterSet):
    category = filters.CharFilter(method="filter_category")

    class Meta:
        model = GlobalNotice
        fields = ["show_in_marquee"]

    def filter_category(self, queryset, name, value):
        return queryset.filter(categories__contains=[value])


from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q

class GlobalNoticeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows GlobalNotices to be viewed.
    Public users see only public notices.
    Authenticated users see both public and private notices.
    """

    def get_queryset(self):
        today = timezone.now().date()
        # Exclude archived/expired from active notices
        queryset = GlobalNotice.objects.filter(is_active=True).exclude(
            Q(is_archived=True) | Q(archive_date__lt=today)
        ).order_by("-date_posted")
        
        if not self.request.user.is_authenticated:
            return queryset.filter(is_private=False)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return GlobalNoticeListSerializer
        return GlobalNoticeDetailSerializer

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = GlobalNoticeFilter


class ArchivedGlobalNoticeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Archived GlobalNotices to be viewed.
    Only authenticated members (staff/faculty) can access this endpoint.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        today = timezone.now().date()
        # Include ONLY archived or expired notices
        return GlobalNotice.objects.filter(
            Q(is_archived=True) | Q(archive_date__lt=today)
        ).order_by("-date_posted")

    def get_serializer_class(self):
        if self.action == "list":
            return GlobalNoticeListSerializer
        return GlobalNoticeDetailSerializer

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = GlobalNoticeFilter

