from rest_framework import viewsets, filters, permissions
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.academics.permissions import IsDepartmentAdmin
from .models import (
    ResearchArea,
    ResearchFacility,
    ResearchProject,
    ResearchScholar,
    Publication,
    Patent,
    ResearchDevelopmentCellMember,
    Consultancy
)
from .serializers import (
    ResearchAreaSerializer,
    ResearchFacilitySerializer,
    ResearchProjectListSerializer,
    ResearchProjectDetailSerializer,
    ResearchScholarListSerializer,
    PublicationSerializer,
    PatentSerializer,
    ResearchDevelopmentCellMemberSerializer,
    ConsultancySerializer,
)


class ResearchBaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet to handle common logic for research models.
    - Public (anonymous) users only see PUBLISHED records.
    - Authenticated users see all records (for management).
    """
    permission_classes = [IsDepartmentAdmin]

    def perform_create(self, serializer):
        if hasattr(self.request.user, "managed_department"):
            serializer.save(department=self.request.user.managed_department)
        else:
            serializer.save()


class ResearchAreaFilter(django_filters.FilterSet):
    department_slug = django_filters.CharFilter(field_name="department__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")

    class Meta:
        model = ResearchArea
        fields = ["campus"]


class ResearchAreaViewSet(ResearchBaseViewSet):
    queryset = ResearchArea.objects.all()
    serializer_class = ResearchAreaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ResearchAreaFilter
    search_fields = ["available_research_areas_or_Specialization", "description"]
    pagination_class = None


class ResearchFacilityViewSet(ResearchBaseViewSet):
    queryset = ResearchFacility.objects.all()
    serializer_class = ResearchFacilitySerializer
    lookup_field = "slug"
    search_fields = ["name", "description"]
    pagination_class = None


class ConsultancyFilter(django_filters.FilterSet):
    department_slug = django_filters.CharFilter(field_name="department__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")
    faculty_slug = django_filters.CharFilter(field_name="faculty__slug")
    faculty__slug = django_filters.CharFilter(field_name="faculty__slug")

    class Meta:
        model = Consultancy
        fields = {
            "nature_of_consultancy": ["exact"],
            "faculty__name": ["icontains"],
            "campus": ["exact"],
            "start_date": ["year", "exact", "gte", "lte"],
            "end_date": ["year", "exact", "gte", "lte"],
        }


class ConsultancyViewSet(ResearchBaseViewSet):
    queryset = Consultancy.objects.select_related("faculty", "department")
    serializer_class = ConsultancySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ConsultancyFilter
    search_fields = ["nature_of_consultancy"]
    ordering_fields = ["amount", "start_date", "end_date"]
    pagination_class = None


class ResearchProjectFilter(django_filters.FilterSet):
    project_date = django_filters.DateFromToRangeFilter(field_name="start_date")
    department_slug = django_filters.CharFilter(field_name="department__slug")
    centre_slug = django_filters.CharFilter(field_name="centre__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")
    centre__slug = django_filters.CharFilter(field_name="centre__slug")
    pi_slug = django_filters.CharFilter(field_name="principal_investigator__slug")
    pi__slug = django_filters.CharFilter(field_name="principal_investigator__slug")
    pi_name = django_filters.CharFilter(
        field_name="principal_investigator__name", lookup_expr="icontains"
    )

    class Meta:
        model = ResearchProject
        fields = ["status", "funding_agency", "campus"]


class ResearchProjectViewSet(ResearchBaseViewSet):
    queryset = ResearchProject.objects.select_related(
        "principal_investigator", "department"
    ).prefetch_related("co_investigators")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ResearchProjectFilter
    search_fields = ["title", "description", "funding_agency"]
    ordering_fields = ["amount_sanctioned", "start_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return ResearchProjectListSerializer
        return ResearchProjectDetailSerializer





class ResearchScholarFilter(django_filters.FilterSet):
    registration_date = django_filters.DateFromToRangeFilter(field_name="date_of_registration")
    department_slug = django_filters.CharFilter(field_name="department__slug")
    centre_slug = django_filters.CharFilter(field_name="centre__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")
    centre__slug = django_filters.CharFilter(field_name="centre__slug")
    supervisor_slug = django_filters.CharFilter(field_name="supervisor__slug")
    supervisor__slug = django_filters.CharFilter(field_name="supervisor__slug")
    supervisor_name = django_filters.CharFilter(
        field_name="supervisor__name", lookup_expr="icontains"
    )

    class Meta:
        model = ResearchScholar
        fields = ["status", "gender", "campus"]


class ResearchScholarViewSet(ResearchBaseViewSet):
    queryset = ResearchScholar.objects.select_related("supervisor", "department")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ResearchScholarFilter
    search_fields = ["scholar_name", "enrollment_no", "research_topic", "state"]
    ordering_fields = ["date_of_registration", "scholar_name"]

    def get_serializer_class(self):
        return ResearchScholarListSerializer


class PublicationFilter(django_filters.FilterSet):
    publication_date_range = django_filters.DateFromToRangeFilter(
        field_name="publication_date"
    )
    faculty_slug = django_filters.CharFilter(field_name="faculty__slug")
    faculty__slug = django_filters.CharFilter(field_name="faculty__slug")
    faculty_name = django_filters.CharFilter(
        field_name="faculty__name", lookup_expr="icontains"
    )
    department_slug = django_filters.CharFilter(field_name="department__slug")
    centre_slug = django_filters.CharFilter(field_name="centre__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")
    centre__slug = django_filters.CharFilter(field_name="centre__slug")

    class Meta:
        model = Publication
        fields = ["publication_type", "campus"]


class PublicationViewSet(ResearchBaseViewSet):
    queryset = Publication.objects.select_related("faculty", "department")
    serializer_class = PublicationSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = PublicationFilter
    search_fields = ["title", "name_of_journal_or_conference_or_publisher"]
    ordering_fields = ["publication_date"]


class PatentFilter(django_filters.FilterSet):
    filing_date = django_filters.DateFromToRangeFilter(field_name="date_of_filing")
    faculty_slug = django_filters.CharFilter(field_name="faculty__slug")
    faculty__slug = django_filters.CharFilter(field_name="faculty__slug")
    faculty_name = django_filters.CharFilter(
        field_name="faculty__name", lookup_expr="icontains"
    )
    department_slug = django_filters.CharFilter(field_name="department__slug")
    centre_slug = django_filters.CharFilter(field_name="centre__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")
    centre__slug = django_filters.CharFilter(field_name="centre__slug")

    class Meta:
        model = Patent
        fields = ["status", "campus"]


class PatentViewSet(ResearchBaseViewSet):
    queryset = Patent.objects.select_related("faculty", "department")
    serializer_class = PatentSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = PatentFilter
    search_fields = ["title", "patent_number"]
    ordering_fields = ["date_of_filing"]


class ResearchDevelopmentCellMemberViewSet(viewsets.ModelViewSet):
    queryset = ResearchDevelopmentCellMember.objects.select_related("faculty")
    serializer_class = ResearchDevelopmentCellMemberSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    ordering = ["order", "faculty__name"]
    pagination_class = None
