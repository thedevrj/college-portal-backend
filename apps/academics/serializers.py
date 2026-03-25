from rest_framework import serializers
from .models import School, Department
from apps.faculty.models import Faculty
from apps.faculty.serializers import FacultySerializer
from apps.centres.serializers import CentreSerializer
from django.db.models import Q

class DepartmentSerializer(serializers.ModelSerializer):

    hod = serializers.SerializerMethodField()
    school_name = serializers.CharField(source="school.name", read_only=True)
    school_slug = serializers.CharField(source="school.slug", read_only=True)

    class Meta:
        model = Department
        fields = [
            "name",
            "slug",
            "hod",
            "school_name",
            "school_slug"
        ]

    def get_hod(self, obj):
        hod = obj.faculty.filter(roles__contains=["HOD"]).first()
        if hod:
            return FacultySerializer(hod, context=self.context).data
        return None
    
class SchoolSerializer(serializers.ModelSerializer):

    departments = DepartmentSerializer(many=True, read_only=True)
    dean = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = [
            "name",
            "slug",
            "image",
            "dean",
            "about_school",
            "departments",
            "centres"
        ]

    def get_dean(self, obj):
        dean = obj.faculty.filter(roles__contains=["DEAN"]).first()
        if dean:
            return FacultySerializer(dean, context=self.context).data
        return None

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)

        return None