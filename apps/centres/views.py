from rest_framework import viewsets
from django.db.models import Prefetch
from .models import Centre
from .serializers import CentreSerializer
from apps.faculty.models import Faculty


class CentreViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Centre.objects.select_related("school").prefetch_related(
            "faculty"
    )

    serializer_class = CentreSerializer
    lookup_field = "slug"