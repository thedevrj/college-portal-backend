from rest_framework import viewsets
from django.db.models import Prefetch
from .models import Centre
from .serializers import CentreDetailSerializer
from apps.faculty.models import Faculty


class CentreViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Centre.objects.select_related("school").prefetch_related("faculty")

    def get_serializer_class(self):
        return CentreDetailSerializer

    lookup_field = "slug"
