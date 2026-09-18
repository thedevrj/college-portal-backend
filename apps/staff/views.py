from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Staff
from .serializers import StaffSerializer

class StaffViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Non-Teaching Staff
    """
    queryset = Staff.objects.filter(is_active=True)
    serializer_class = StaffSerializer
    permission_classes = [AllowAny]
    search_fields = ["name", "designation", "department_section_cell", "staff_no"]
    ordering_fields = '__all__'
    filterset_fields = ["department_section_cell", "staff_type", "campus"]
