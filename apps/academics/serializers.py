from rest_framework import serializers
from .models import School, Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "slug"]


class SchoolSerializer(serializers.ModelSerializer):

    departments = DepartmentSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()


    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "slug",
            "dean_name",
            "dean_employee_id",
            "departments",
            "image"
        ]
    def get_image(self, obj):
        
        request = self.context.get("request")

        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)

        return None