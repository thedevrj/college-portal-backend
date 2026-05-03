from rest_framework import serializers
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
from apps.faculty.serializers import FacultyListSerializer


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
    faculty_name = serializers.CharField(source="faculty.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    department_slug = serializers.CharField(source="department.slug", read_only=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Consultancy._meta.get_field("department").related_model.objects.all(),
        required=False,
    )

    class Meta:
        model = Consultancy
        fields = "__all__"


class ResearchFacilitySerializer(serializers.ModelSerializer):
    incharge_name = serializers.CharField(source="incharge.name", read_only=True)

    class Meta:
        model = ResearchFacility
        fields = "__all__"


class ResearchProjectListSerializer(serializers.ModelSerializer):
    pi_name = serializers.CharField(
        source="principal_investigator.name", read_only=True
    )
    department_name = serializers.CharField(source="department.name", read_only=True)
    department_slug = serializers.CharField(source="department.slug", read_only=True)
    co_investigators_names = serializers.SerializerMethodField()

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
        return attrs


class PublicationSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source="faculty.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Publication._meta.get_field("department").related_model.objects.all(),
        required=False,
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
        return attrs


class PatentSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source="faculty.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Patent._meta.get_field("department").related_model.objects.all(),
        required=False,
    )

    class Meta:
        model = Patent
        fields = "__all__"


class ResearchDevelopmentCellMemberSerializer(serializers.ModelSerializer):
    faculty = FacultyListSerializer(read_only=True)

    class Meta:
        model = ResearchDevelopmentCellMember
        fields = ["id", "faculty", "designation", "order"]
