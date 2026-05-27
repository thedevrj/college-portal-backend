from rest_framework import serializers
from .models import Faculty, InvitedTalk, CourseDesign, Membership
from apps.academics.models import School, Department
from apps.centres.models import Centre


class SchoolNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name", "slug"]


class DepartmentNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "slug"]


class CentreNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Centre
        fields = ["id", "name", "slug"]


class InvitedTalkSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitedTalk
        exclude = ["faculty", "created_at", "updated_at", "deleted_at", "is_deleted"]


class CourseDesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDesign
        exclude = ["faculty", "created_at", "updated_at", "deleted_at", "is_deleted"]


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        exclude = ["faculty", "created_at", "updated_at", "deleted_at", "is_deleted"]


class BaseFacultySerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    cv_document = serializers.SerializerMethodField()
    school = SchoolNestedSerializer(read_only=True)
    department = DepartmentNestedSerializer(read_only=True)
    centre = CentreNestedSerializer(read_only=True)

    class Meta:
        model = Faculty
        fields = "__all__"

    def get_photo(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

    def get_cv_document(self, obj):
        if obj.cv_document:
            return obj.cv_document.url
        return None


class FacultyListSerializer(BaseFacultySerializer):
    class Meta(BaseFacultySerializer.Meta):
        # return lightweight fields for the list page card/grid view
        fields = [
            "id",
            "name",
            "slug",
            "designation",
            "campus",
            "photo",
            "photo_alt_text",
            "qualification",
            "school",
            "department",
            "centre",
            "other_email",
            "phone1",
            "phone2",
            "insti_email",
            "is_active",
        ]


class FacultyDetailSerializer(BaseFacultySerializer):
    invited_talks = InvitedTalkSerializer(many=True, read_only=True)
    course_designs = CourseDesignSerializer(many=True, read_only=True)
    memberships = MembershipSerializer(many=True, read_only=True)

    class Meta:
        model = Faculty
        # Return all profile fields, excluding private/internal data
        exclude = [
            "staff_no",
            "dob",
        ]
