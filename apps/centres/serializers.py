from rest_framework import serializers
from .models import Centre
from apps.faculty.models import Faculty
from apps.academics.models import Department
from apps.faculty.serializers import FacultySerializer

class DepartmentMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["name", "slug"]


class CentreSerializer(serializers.ModelSerializer):

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
            "director",
            "faculty",
        ]
    def get_director(self, obj):
        director = obj.faculty.filter(roles__icontains="DIRECTOR").first()
        if director:
            return FacultySerializer(director, context=self.context).data
        return None

    def get_faculty(self, obj):
        qs = obj.faculty.all()
        return FacultySerializer(qs, many=True, context=self.context).data