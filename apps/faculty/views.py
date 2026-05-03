from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Faculty
from .serializers import FacultyListSerializer, FacultyDetailSerializer
from college_backend_portal.pagination import FlexiblePagination


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
    filterset_fields = {
        "department__slug": ["exact"],
        "school__slug": ["exact"],
        "centre__slug": ["exact"],
        "designation": ["exact"],
        "campus": ["exact"],
    }
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
