from rest_framework import serializers
from .models import FoundationCourse, FoundationCourseMaterial


class FoundationCourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoundationCourseMaterial
        fields = [
            "id",
            "course",
            "title",
            "material_type",
            "file",
            "link",
            "uploaded_at",
        ]
        read_only_fields = ["uploaded_at"]

    def validate(self, attrs):
        file = attrs.get("file")
        link = attrs.get("link")
        if not file and not link:
            raise serializers.ValidationError(
                "Either a file attachment or an external link must be provided."
            )
        return attrs


class FoundationCourseSerializer(serializers.ModelSerializer):
    materials = FoundationCourseMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = FoundationCourse
        fields = [
            "id",
            "level",
            "semester",
            "course_code",
            "course_title",
            "credits",
            "syllabus_file",
            "materials",
        ]

    def validate(self, attrs):
        course_code = attrs.get("course_code")
        if course_code:
            qs = FoundationCourse.objects.filter(
                course_code__iexact=course_code, is_deleted=False
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {
                        "course_code": "A Foundation Course with this Course/Paper Code already exists."
                    }
                )
        return attrs
