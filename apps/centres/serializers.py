from rest_framework import serializers
from .models import Centre
from apps.faculty.models import Faculty
from apps.academics.models import Department
from apps.faculty.serializers import FacultyListSerializer

class CentreListSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)
    school_slug = serializers.CharField(source="school.slug", read_only=True)

    class Meta:
        model = Centre
        fields = [
            "id",
            "name",
            "slug",
            "school",
            "school_name",
            "school_slug",
        ]

class CentreDetailSerializer(serializers.ModelSerializer):
    director = serializers.SerializerMethodField()
    school_name = serializers.CharField(source="school.name", read_only=True)
    school_slug = serializers.CharField(source="school.slug", read_only=True)
    faculty = serializers.SerializerMethodField()

    class Meta:
        model = Centre
        fields = [
            "id",
            "name",
            "slug",
            "school",
            "school_name",
            "school_slug",
            "description",
            "director",
            "faculty",
        ]

    def get_director(self, obj):
        director = obj.faculty.filter(roles__contains="DIRECTOR").first()
        if director:
            return FacultyListSerializer(director, context=self.context).data
        return None

    def get_faculty(self, obj):
        qs = obj.faculty.all()
        return FacultyListSerializer(qs, many=True, context=self.context).data