from rest_framework import viewsets, filters
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import FoundationCourse, FoundationCourseMaterial
from .serializers import (
    FoundationCourseSerializer,
    FoundationCourseMaterialSerializer,
)


class FoundationCourseFilter(django_filters.FilterSet):
    class Meta:
        model = FoundationCourse
        fields = ["level", "semester"]


class FoundationCourseViewSet(viewsets.ModelViewSet):
    queryset = FoundationCourse.objects.filter(is_deleted=False)
    serializer_class = FoundationCourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = FoundationCourseFilter
    search_fields = ["course_title", "course_code"]
    ordering_fields = ["level", "semester", "course_code", "course_title"]
    ordering = ["level", "semester", "course_code"]


class FoundationCourseMaterialFilter(django_filters.FilterSet):
    class Meta:
        model = FoundationCourseMaterial
        fields = ["course", "material_type"]


class FoundationCourseMaterialViewSet(viewsets.ModelViewSet):
    queryset = FoundationCourseMaterial.objects.filter(is_deleted=False)
    serializer_class = FoundationCourseMaterialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = FoundationCourseMaterialFilter
    search_fields = ["title"]
    ordering_fields = ["uploaded_at", "title"]
    ordering = ["-uploaded_at"]
