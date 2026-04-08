from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import GlobalNotice
from .serializers import GlobalNoticeSerializer

class GlobalNoticeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows GlobalNotices to be viewed.
    """
    queryset = GlobalNotice.objects.filter(is_active=True).order_by('-date_posted')
    serializer_class = GlobalNoticeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'show_in_marquee']
