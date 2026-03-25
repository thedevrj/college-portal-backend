from rest_framework import serializers
from .models import Faculty


class FacultySerializer(serializers.ModelSerializer):

    photo = serializers.SerializerMethodField()

    class Meta:
        model = Faculty
        fields = [
            "employee_id",
            "name",
            "slug",
            "designation",
            "roles",
            "insti_email",
            "other_email",
            "phone1",
            "photo",
            "bio",
            "staff_no",
        ]

    def get_photo(self, obj):
        request = self.context.get("request")

        if obj.photo and request:
            return (obj.photo.url)

        return None