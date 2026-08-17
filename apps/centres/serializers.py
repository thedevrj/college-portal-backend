from rest_framework import serializers
from .models import Centre
from apps.faculty.models import Faculty
from apps.academics.models import Department
from apps.faculty.serializers import FacultyListSerializer


class CentreDetailSerializer(serializers.ModelSerializer):
    head = FacultyListSerializer(read_only=True)
    head_title = serializers.SerializerMethodField()
    school_name = serializers.CharField(source="school.name", read_only=True)
    school_slug = serializers.CharField(source="school.slug", read_only=True)
    faculty = serializers.SerializerMethodField()
    about = serializers.CharField()
    thrust_areas = serializers.CharField()

    class Meta:
        model = Centre
        fields = [
            "id",
            "name",
            "slug",
            "head",
            "head_title",
            "head_title_other",
            "description",
            "about",
            "thrust_areas",
            "school",
            "school_name",
            "school_slug",
            "faculty",
        ]

    def get_head_title(self, obj):
        if obj.head_title == "Others":
            return obj.head_title_other
        return obj.head_title

    def get_faculty(self, obj):
        qs = obj.faculty.all()
        return FacultyListSerializer(qs, many=True, context=self.context).data
