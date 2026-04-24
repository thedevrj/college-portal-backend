from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    ResearchArea,
    ResearchFacility,
    ResearchProject,
    ResearchScholar,
    Publication,
    Patent,
    ResearchDevelopmentCellMember,
    Consultancy,
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


class ResearchAreaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResearchArea.objects.all()
    serializer_class = ResearchAreaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["department__slug", "department__id", "campus"]
    search_fields = ["available_research_areas_or_Specialization", "description"]
    pagination_class = None


class ResearchFacilityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResearchFacility.objects.all()
    serializer_class = ResearchFacilitySerializer
    lookup_field = "slug"
    search_fields = ["name", "description"]
    pagination_class = None


class ConsultancyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Consultancy.objects.select_related("faculty", "department")
    serializer_class = ConsultancySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "nature_of_consultancy": ["exact"],
        "department__slug": ["exact"],
        "faculty__slug": ["exact"],
        "campus": ["exact"],
        "start_date": ["year", "exact"],
        "end_date": ["year", "exact"],
    }
    search_fields = ["nature_of_consultancy"]
    ordering_fields = ["amount_sanctioned", "start_date", "end_date"]
    pagination_class = None


class ResearchProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResearchProject.objects.select_related(
        "principal_investigator", "department"
    ).prefetch_related("co_investigators")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "status": ["exact"],
        "funding_agency": ["exact"],
        "department__slug": ["exact"],
        "principal_investigator__slug": ["exact"],
        "campus": ["exact"],
        "start_date": ["year", "exact"],
    }
    search_fields = ["title", "description", "funding_agency"]
    ordering_fields = ["amount_sanctioned", "start_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return ResearchProjectListSerializer
        return ResearchProjectDetailSerializer


class ResearchScholarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResearchScholar.objects.select_related("supervisor", "department")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "status": ["exact"],
        "date_of_registration": ["year", "exact"],
        "department__slug": ["exact"],
        "supervisor__slug": ["exact"],
        "gender": ["exact"],
        "campus": ["exact"],
    }
    search_fields = ["scholar_name", "enrollment_no", "research_topic", "state"]
    ordering_fields = ["date_of_registration", "scholar_name"]

    def get_serializer_class(self):
        return ResearchScholarListSerializer


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Publication.objects.select_related("faculty", "department")
    serializer_class = PublicationSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "publication_type": ["exact"],
        "publication_date": ["year", "exact"],
        "faculty__slug": ["exact"],
        "department__slug": ["exact"],
        "campus": ["exact"],
    }
    search_fields = ["title", "name_of_journal_or_conference_or_publisher"]
    ordering_fields = ["publication_date"]


class PatentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Patent.objects.select_related("faculty", "department")
    serializer_class = PatentSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "status": ["exact"],
        "date_of_filing": ["exact", "year"],
        "faculty__slug": ["exact"],
        "department__slug": ["exact"],
        "campus": ["exact"],
    }
    search_fields = ["title", "patent_number"]
    ordering_fields = ["date_of_filing"]


class ResearchDevelopmentCellMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResearchDevelopmentCellMember.objects.select_related("faculty")
    serializer_class = ResearchDevelopmentCellMemberSerializer
    ordering = ["order", "faculty__name"]
    pagination_class = None
