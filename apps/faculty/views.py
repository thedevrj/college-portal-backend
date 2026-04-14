from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Faculty
from .serializers import FacultyListSerializer, FacultyDetailSerializer

class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Faculty.objects.select_related(
        'school', 'department', 'centre'
    ).filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return FacultyListSerializer
        return FacultyDetailSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'department__slug': ['exact'],
        'school__slug': ['exact'],
        'centre__slug': ['exact'],
        'designation': ['exact'],
        'faculty_type': ['exact'],
        'campus': ['exact'],
    }
    search_fields = ['name', 'designation', 'qualification', 'research_int']
    ordering_fields = ['name', 'designation', 'date_of_joining']
    ordering = ['name']  # default A-Z
    lookup_field = 'slug'