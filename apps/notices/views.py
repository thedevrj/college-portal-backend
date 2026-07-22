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


class GlobalNoticeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows GlobalNotices to be viewed.
    Public users see only public notices.
    Authenticated users see both public and private notices.
    """

    def get_queryset(self):
        queryset = GlobalNotice.objects.filter(is_active=True).order_by("-date_posted")
        if not self.request.user.is_authenticated:
            return queryset.filter(is_private=False)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return GlobalNoticeListSerializer
        return GlobalNoticeDetailSerializer

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = GlobalNoticeFilter
