from rest_framework import viewsets
from .models import Faculty
from .serializers import FacultySerializer


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Faculty.objects.select_related(
        "school",
        "department"
    )

    serializer_class = FacultySerializer

    lookup_field = "slug"