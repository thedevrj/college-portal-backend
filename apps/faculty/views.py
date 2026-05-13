from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Faculty
from .serializers import FacultyListSerializer, FacultyDetailSerializer
from college_backend_portal.pagination import FlexiblePagination


class FacultyFilter(django_filters.FilterSet):
    centre_slug = django_filters.CharFilter(field_name="centre__slug")
    department_slug = django_filters.CharFilter(field_name="department__slug")
    school_slug = django_filters.CharFilter(field_name="school__slug")
    centre__slug = django_filters.CharFilter(field_name="centre__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")
    school__slug = django_filters.CharFilter(field_name="school__slug")

    class Meta:
        model = Faculty
        fields = ["designation", "campus"]


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = FlexiblePagination
    queryset = Faculty.objects.select_related("school", "department", "centre").filter(
        is_active=True
    )

    def get_serializer_class(self):
        if self.action == "list":
            return FacultyListSerializer
        return FacultyDetailSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = FacultyFilter
    search_fields = ["name", "designation", "qualification", "research_int"]
    ordering_fields = [
        "name",
        "designation",
        "date_of_joining",
        "date_of_superannuation",
    ]
    ordering = ["?"]
    lookup_field = "slug"

    @action(detail=False, methods=["get"])
    def random(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        faculty = queryset.order_by("?").first()
        if faculty:
            serializer = self.get_serializer(faculty)
            return Response(serializer.data)
        return Response({"detail": "No faculty found."}, status=404)
