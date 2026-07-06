from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import MOU
from .serializers import MOUSerializer


class MOUFilter(django_filters.FilterSet):
    mou_date = django_filters.DateFromToRangeFilter(field_name="date_of_signing")


class MOUViewSet(viewsets.ModelViewSet):
    queryset = MOU.objects.filter(is_deleted=False)
    serializer_class = MOUSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = MOUFilter
    search_fields = ["organization_name", "Nature_of_organization"]
    ordering_fields = ["date_of_signing"]
    ordering = ["-date_of_signing"]
