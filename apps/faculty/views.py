from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Faculty
from .serializers import FacultySerializer

class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department__slug', 'school__slug', 'designation']
    search_fields = ['name', 'designation']
    lookup_field = 'slug'