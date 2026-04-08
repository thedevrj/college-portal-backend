from rest_framework import viewsets
from django_filters import rest_framework as filters
from .models import GlobalNotice
from .serializers import GlobalNoticeSerializer

class GlobalNoticeFilter(filters.FilterSet):
    category = filters.CharFilter(method='filter_category')

    class Meta:
        model = GlobalNotice
        fields = ['show_in_marquee']

    def filter_category(self, queryset, name, value):
        return queryset.filter(categories__contains=[value])

class GlobalNoticeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows GlobalNotices to be viewed.
    """
    queryset = GlobalNotice.objects.filter(is_active=True).order_by('-date_posted')
    serializer_class = GlobalNoticeSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = GlobalNoticeFilter
