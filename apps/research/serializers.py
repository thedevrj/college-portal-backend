from rest_framework import serializers
import re
from .models import (
    ResearchArea,
    ResearchFacility,
    ResearchProject,
    ResearchScholar,
    Publication,
    PublicationAuthor,
    Patent,
    PatentAuthor,
    ResearchDevelopmentCellMember,
    Consultancy,
    DOI_RE,
    clean_title_string,
    title_fingerprint,
)
from apps.faculty.serializers import FacultyListSerializer


class PublicationAuthorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="faculty.name", read_only=True)
    slug = serializers.CharField(source="faculty.slug", read_only=True)

    class Meta:
        model = PublicationAuthor
        fields = ["author_order", "author_role", "name", "slug"]


class PatentAuthorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="faculty.name", read_only=True)
    slug = serializers.CharField(source="faculty.slug", read_only=True)

    class Meta:
        model = PatentAuthor
        fields = ["author_order", "author_role", "name", "slug"]


class ResearchAreaSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    department_slug = serializers.CharField(source="department.slug", read_only=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=ResearchArea._meta.get_field("department").related_model.objects.all(),
        required=False,
    )

    class Meta:
        model = ResearchArea
        fields = [
            "id",
            "available_research_areas_or_Specialization",
            "description",
            "department",
            "department_name",
            "department_slug",
            "campus",
        ]


class ConsultancySerializer(serializers.ModelSerializer):
    faculty_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    department_slug = serializers.SerializerMethodField()
    department = serializers.PrimaryKeyRelatedField(
        queryset=Consultancy._meta.get_field("department").related_model.objects.all(),
        required=False,
    )

    def get_faculty_name(self, obj):
        return obj.faculty.name if obj.faculty else None

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_department_slug(self, obj):
        return obj.department.slug if obj.department else None

    class Meta:
        model = Consultancy
        fields = "__all__"

    def validate(self, attrs):
        faculty = attrs.get("faculty")
        nature_of_consultancy = attrs.get("nature_of_consultancy")
        start_date = attrs.get("start_date")
        department = attrs.get("department")

        if faculty and nature_of_consultancy and start_date and department:
            qs = Consultancy.objects.filter(
                faculty=faculty,
                nature_of_consultancy__iexact=nature_of_consultancy,
                start_date=start_date,
                department=department,
                is_deleted=False,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "A consultancy record with the same Faculty, Nature of Consultancy, Start Date, and Department already exists."
                )
        return attrs


class ResearchFacilitySerializer(serializers.ModelSerializer):
    incharge_name = serializers.SerializerMethodField()

    def get_incharge_name(self, obj):
        return obj.incharge.name if obj.incharge else None

    class Meta:
        model = ResearchFacility
        fields = "__all__"


class ResearchProjectListSerializer(serializers.ModelSerializer):
    pi_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(source="department.name", read_only=True)
    department_slug = serializers.CharField(source="department.slug", read_only=True)
    co_investigators_names = serializers.SerializerMethodField()

    def get_pi_name(self, obj):
        return obj.principal_investigator.name if obj.principal_investigator else None

    class Meta:
        model = ResearchProject
        fields = [
            "id",
            "title",
            "pi_name",
            "co_investigators_names",
            "funding_agency",
            "amount_sanctioned",
            "status",
            "department_name",
            "department_slug",
            "campus",
        ]

    def get_co_investigators_names(self, obj):
        return [faculty.name for faculty in obj.co_investigators.all()]


class ResearchProjectDetailSerializer(serializers.ModelSerializer):
    principal_investigator = FacultyListSerializer(read_only=True)
    co_investigators = FacultyListSerializer(many=True, read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    department_slug = serializers.CharField(source="department.slug", read_only=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=ResearchProject._meta.get_field(
            "department"
        ).related_model.objects.all(),
        required=False,
    )

    class Meta:
        model = ResearchProject
        fields = "__all__"

    def validate(self, attrs):
        title = attrs.get("title")
        principal_investigator = attrs.get("principal_investigator")
        department = attrs.get("department")

        if title and department:
            qs = ResearchProject.objects.filter(
                title__iexact=title,
                principal_investigator=principal_investigator,
                department=department,
                is_deleted=False,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "A project with the same Title, Principal Investigator, and Department already exists."
                )
        return attrs


class ResearchScholarListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    department_slug = serializers.CharField(source="department.slug", read_only=True)
    registration_year = serializers.SerializerMethodField()
    supervisor = FacultyListSerializer(read_only=True)
    co_supervisor = FacultyListSerializer(many=True, read_only=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=ResearchScholar._meta.get_field(
            "department"
        ).related_model.objects.all(),
        required=False,
    )

    class Meta:
        model = ResearchScholar
        fields = "__all__"

    def get_registration_year(self, obj):
        return obj.date_of_registration.year if obj.date_of_registration else None

    def validate(self, attrs):
        if attrs.get("category") == "Other" and not attrs.get("other_category"):
            raise serializers.ValidationError(
                {"other_category": "This field is required when category is 'Other'."}
            )
        if attrs.get("gender") == "Other" and not attrs.get("other_gender"):
            raise serializers.ValidationError(
                {"other_gender": "This field is required when gender is 'Other'."}
            )

        # --- Duplicate entry check ---
        scholar_name = attrs.get("scholar_name")
        department = attrs.get("department")
        supervisor = attrs.get("supervisor")
        date_of_birth = attrs.get("date_of_birth")

        if scholar_name and department:
            qs = ResearchScholar.objects.filter(
                scholar_name__iexact=scholar_name,
                department=department,
                supervisor=supervisor,
                date_of_birth=date_of_birth,
                is_deleted=False,
            )
            # On update (PATCH/PUT), exclude current instance
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "A scholar record with the same Name, Department and Supervisor "
                    "already exists. Please verify before adding a new entry."
                )

        return attrs


class PublicationSerializer(serializers.ModelSerializer):
    # Structured author list: [{author_order, author_role, name, slug}]
    # Uses the publicationauthor_set prefetch set in PublicationViewSet.
    authors = PublicationAuthorSerializer(
        source="publicationauthor_set", many=True, read_only=True
    )

    class Meta:
        model = Publication
        fields = "__all__"

    def validate(self, attrs):
        if attrs.get("publication_type") == "Others" and not attrs.get(
            "other_publication_type"
        ):
            raise serializers.ValidationError(
                {
                    "other_publication_type": "This field is required when publication_type is 'Others'."
                }
            )
        if attrs.get("indexing") == "Others" and not attrs.get("others_indexing"):
            raise serializers.ValidationError(
                {"others_indexing": "This field is required when indexing is 'Others'."}
            )

        title = attrs.get("title")
        if title:
            title = clean_title_string(title)
            attrs["title"] = title

        doi_url = attrs.get("doi_url")

        # --- DOI format check ---
        if doi_url:
            doi_url = doi_url.strip()
            if not DOI_RE.match(doi_url):
                raise serializers.ValidationError(
                    {
                        "doi_url": (
                            "Enter a valid DOI. "
                            "Accepted formats: \u201810.XXXX/suffix\u2019 "
                            "or \u2018https://doi.org/10.XXXX/suffix\u2019."
                        )
                    }
                )
            # Normalize to canonical URL form for the uniqueness check below
            match = DOI_RE.match(doi_url)
            if match:
                doi_url = f"https://doi.org/{match.group(1)}"

        # --- Uniqueness check ---
        if doi_url:
            qs_doi = Publication.objects.filter(
                doi_url__iexact=doi_url,
                is_deleted=False,
            )
            if self.instance:
                qs_doi = qs_doi.exclude(pk=self.instance.pk)
            duplicate = qs_doi.first()
            if duplicate:
                raise serializers.ValidationError(
                    {
                        "doi_url": "A publication with this DOI URL already exists.",
                        "duplicate_id": duplicate.id,
                    }
                )
        elif title:
            qs_title = Publication.objects.filter(
                title__iexact=title,
                is_deleted=False,
            )
            if self.instance:
                qs_title = qs_title.exclude(pk=self.instance.pk)
            duplicate = qs_title.first()
            if duplicate:
                raise serializers.ValidationError(
                    {
                        "title": "A publication with this exact title already exists. Did you mean to claim it instead?",
                        "duplicate_id": duplicate.id,
                    }
                )

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get("full_author_list"):
            # .all() uses the prefetch cache; Meta.ordering on PublicationAuthor handles order
            authors = instance.internal_authors.all()
            data["full_author_list"] = ", ".join([author.name for author in authors])
        return data


class PatentSerializer(serializers.ModelSerializer):
    # Structured inventor list: [{author_order, author_role, name, slug}]
    # Uses the patentauthor_set prefetch set in PatentViewSet.
    inventors = PatentAuthorSerializer(
        source="patentauthor_set", many=True, read_only=True
    )

    class Meta:
        model = Patent
        fields = "__all__"

    def validate(self, attrs):
        title = attrs.get("title")
        if title:
            title = clean_title_string(title)
            attrs["title"] = title

        patent_number = attrs.get("patent_number")
        if patent_number:
            patent_number = patent_number.strip()
            attrs["patent_number"] = patent_number

        # we check for patent_number for uniqueness. If no patent_number then check for title.

        if patent_number:
            qs_number = Patent.objects.filter(
                patent_number__iexact=patent_number,
                is_deleted=False,
            )
            if self.instance:
                qs_number = qs_number.exclude(pk=self.instance.pk)
            duplicate = qs_number.first()
            if duplicate:
                raise serializers.ValidationError(
                    {
                        "patent_number": "A patent with this Patent Number already exists.",
                        "duplicate_id": duplicate.id,
                    }
                )
        elif title:
            qs_title = Patent.objects.filter(
                title__iexact=title,
                is_deleted=False,
            )
            if self.instance:
                qs_title = qs_title.exclude(pk=self.instance.pk)
            duplicate = qs_title.first()
            if duplicate:
                raise serializers.ValidationError(
                    {
                        "title": "A patent with this exact title already exists. Did you mean to claim it instead?",
                        "duplicate_id": duplicate.id,
                    }
                )

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get("full_inventor_list"):
            # .all() uses the prefetch cache; Meta.ordering on PatentAuthor handles order
            inventors = instance.internal_inventors.all()
            data["full_inventor_list"] = ", ".join(
                [inventor.name for inventor in inventors]
            )
        return data


class ResearchDevelopmentCellMemberSerializer(serializers.ModelSerializer):
    faculty = FacultyListSerializer(read_only=True)

    class Meta:
        model = ResearchDevelopmentCellMember
        fields = ["id", "faculty", "designation", "order"]
