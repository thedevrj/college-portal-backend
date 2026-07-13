from django.db import transaction
from django.db.models import Prefetch
from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
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
    Consultancy,
    PublicationAuthor,
    PatentAuthor,
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

    permission_classes = [IsDepartmentAdmin]

    def perform_create(self, serializer):
        from apps.academics.permissions import IsDepartmentAdmin

        permission_checker = IsDepartmentAdmin()
        managed_depts = permission_checker._get_managed_departments(self.request.user)

        model_class = self.get_serializer().Meta.model

        if hasattr(model_class, "department") and hasattr(
            model_class._meta.get_field("department"), "remote_field"
        ):
            # Check if department is already in the validated data (i.e., passed by the frontend)
            provided_dept = serializer.validated_data.get("department")

            if managed_depts == "ALL":
                # Superusers can set any department, or if none provided, it might fail validation later if required
                serializer.save()
            else:
                if provided_dept:
                    if provided_dept not in managed_depts:
                        from rest_framework.exceptions import PermissionDenied

                        raise PermissionDenied(
                            "You do not have permission to create records for this department."
                        )
                    serializer.save()
                else:
                    if len(managed_depts) == 1:
                        serializer.save(department=managed_depts[0])
                    elif len(managed_depts) > 1:
                        from rest_framework.exceptions import ValidationError

                        raise ValidationError(
                            {
                                "department": "You manage multiple departments. Please specify which department this belongs to."
                            }
                        )
                    else:
                        from rest_framework.exceptions import PermissionDenied

                        raise PermissionDenied(
                            "You do not have permission to create records."
                        )
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


class ResearchFacilityViewSet(ResearchBaseViewSet):
    queryset = ResearchFacility.objects.all()
    serializer_class = ResearchFacilitySerializer
    lookup_field = "slug"
    search_fields = ["name", "description"]


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


class ResearchProjectFilter(django_filters.FilterSet):
    project_date = django_filters.DateFromToRangeFilter(field_name="start_date")
    department_slug = django_filters.CharFilter(field_name="department__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")
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
    search_fields = [
        "title",
        "description",
        "funding_agency",
        "principal_investigator__name",
        "co_investigators__name",
    ]
    ordering_fields = ["amount_sanctioned", "start_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return ResearchProjectListSerializer
        return ResearchProjectDetailSerializer


class ResearchScholarFilter(django_filters.FilterSet):
    registration_date = django_filters.DateFromToRangeFilter(
        field_name="date_of_registration"
    )
    department_slug = django_filters.CharFilter(field_name="department__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")
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
    search_fields = [
        "scholar_name",
        "research_topic",
        "enrollment_no",
        "state",
        "supervisor__name",
        "co_supervisor__name",
    ]
    ordering_fields = ["date_of_registration", "scholar_name"]

    def get_serializer_class(self):
        return ResearchScholarListSerializer


class PublicationFilter(django_filters.FilterSet):
    publication_date_range = django_filters.DateFromToRangeFilter(
        field_name="publication_date"
    )
    faculty_slug = django_filters.CharFilter(field_name="internal_authors__slug")
    faculty__slug = django_filters.CharFilter(field_name="internal_authors__slug")
    faculty_name = django_filters.CharFilter(
        field_name="internal_authors__name", lookup_expr="icontains"
    )
    department_slug = django_filters.CharFilter(
        field_name="internal_authors__department__slug"
    )
    centre_slug = django_filters.CharFilter(field_name="internal_authors__centre__slug")
    department__slug = django_filters.CharFilter(
        field_name="internal_authors__department__slug"
    )
    centre__slug = django_filters.CharFilter(
        field_name="internal_authors__centre__slug"
    )

    class Meta:
        model = Publication
        fields = ["publication_type", "campus"]


class PublicationViewSet(ResearchBaseViewSet):
    queryset = Publication.objects.prefetch_related(
        Prefetch(
            "publicationauthor_set",
            queryset=PublicationAuthor.objects.select_related("faculty__department"),
        ),
        "internal_authors",
    ).distinct()
    serializer_class = PublicationSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = PublicationFilter
    search_fields = [
        "title",
        "name_of_journal_or_conference_or_publisher",
        "internal_authors__name",
    ]
    ordering_fields = ["publication_date"]

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def claim(self, request, pk=None):
        publication = self.get_object()

        if (
            not hasattr(request.user, "faculty_profile")
            or not request.user.faculty_profile
        ):
            return Response(
                {"error": "Only authenticated faculty members can claim publications."},
                status=status.HTTP_403_FORBIDDEN,
            )

        faculty = request.user.faculty_profile
        try:
            author_order = int(request.data.get("author_order", 1))
            if author_order < 1:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "author_order must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        author_role = str(request.data.get("author_role", "Co-Author")).strip()
        allowed_roles = [
            "First Author",
            "Co-Author",
            "Corresponding Author",
            "Lead Author",
        ]
        if author_role not in allowed_roles:
            return Response(
                {"error": f"author_role must be one of {allowed_roles}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            author, created = PublicationAuthor.objects.get_or_create(
                publication=publication,
                faculty=faculty,
                defaults={"author_order": author_order, "author_role": author_role},
            )

        if not created:
            return Response(
                {"error": "You have already claimed this publication."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Successfully claimed publication."},
            status=status.HTTP_201_CREATED,
        )


class PatentFilter(django_filters.FilterSet):
    filing_date = django_filters.DateFromToRangeFilter(field_name="date_of_filing")
    faculty_slug = django_filters.CharFilter(field_name="internal_inventors__slug")
    faculty__slug = django_filters.CharFilter(field_name="internal_inventors__slug")
    faculty_name = django_filters.CharFilter(
        field_name="internal_inventors__name", lookup_expr="icontains"
    )
    department_slug = django_filters.CharFilter(
        field_name="internal_inventors__department__slug"
    )
    centre_slug = django_filters.CharFilter(
        field_name="internal_inventors__centre__slug"
    )
    department__slug = django_filters.CharFilter(
        field_name="internal_inventors__department__slug"
    )
    centre__slug = django_filters.CharFilter(
        field_name="internal_inventors__centre__slug"
    )

    class Meta:
        model = Patent
        fields = ["status"]


class PatentViewSet(ResearchBaseViewSet):
    queryset = Patent.objects.prefetch_related(
        Prefetch(
            "patentauthor_set",
            queryset=PatentAuthor.objects.select_related("faculty__department"),
        ),
        "internal_inventors",
    ).distinct()
    serializer_class = PatentSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = PatentFilter
    search_fields = ["title", "patent_number", "internal_inventors__name"]
    ordering_fields = ["date_of_filing"]

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def claim(self, request, pk=None):
        patent = self.get_object()

        if (
            not hasattr(request.user, "faculty_profile")
            or not request.user.faculty_profile
        ):
            return Response(
                {"error": "Only authenticated faculty members can claim patents."},
                status=status.HTTP_403_FORBIDDEN,
            )

        faculty = request.user.faculty_profile
        try:
            author_order = int(request.data.get("author_order", 1))
            if author_order < 1:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "author_order must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        author_role = str(request.data.get("author_role", "Co-Inventor")).strip()
        allowed_roles = ["First Inventor", "Co-Inventor", "Lead Inventor"]
        if author_role not in allowed_roles:
            return Response(
                {"error": f"author_role must be one of {allowed_roles}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            author, created = PatentAuthor.objects.get_or_create(
                patent=patent,
                faculty=faculty,
                defaults={"author_order": author_order, "author_role": author_role},
            )

        if not created:
            return Response(
                {"error": "You have already claimed this patent."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Successfully claimed patent."}, status=status.HTTP_201_CREATED
        )


class ResearchDevelopmentCellMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResearchDevelopmentCellMember.objects.select_related("faculty")
    serializer_class = ResearchDevelopmentCellMemberSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["order", "faculty__name"]
    ordering = ["order"]
