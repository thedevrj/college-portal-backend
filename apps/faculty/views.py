from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Faculty
from .serializers import FacultySerializer

class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department__slug', 'school__slug', 'designation']
    lookup_field = 'slug'