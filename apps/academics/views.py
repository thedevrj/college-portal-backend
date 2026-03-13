# Create your views here.
from rest_framework import viewsets
from .models import School, Department
from .serializers import SchoolSerializer, DepartmentSerializer


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.prefetch_related("departments")
    serializer_class = SchoolSerializer
    lookup_field = "slug"
    


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.select_related("school")
    serializer_class = DepartmentSerializer