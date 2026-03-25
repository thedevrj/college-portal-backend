# Create your views here.
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import School, Department
from .serializers import SchoolSerializer, DepartmentSerializer

class SchoolViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = School.objects.prefetch_related(
        "departments",
        "faculty"
    )

    serializer_class = SchoolSerializer
    lookup_field = "slug"

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Department.objects.select_related(
        "school"
    ).prefetch_related(
        "faculty"
    )

    filter_backends = [DjangoFilterBackend, SearchFilter]
    # filter by school slug
    filterset_fields = {
        "school__slug": ["exact"]
    }

    # search by department name
    search_fields = ["name"]

    serializer_class = DepartmentSerializer

    lookup_field = "slug"