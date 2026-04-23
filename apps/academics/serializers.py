from rest_framework import serializers
from .models import (
    School,
    Department,
    Program,
    Course,
    CBCSCourse,
    DepartmentGallery,
    Notice,
    Committee,
    CommitteeMember,
    Timetable,
    StudyMaterial,
)


class BaseSchoolSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = "__all__"

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class SchoolListSerializer(BaseSchoolSerializer):
    dean = serializers.SerializerMethodField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = [
            "id",
            "name",
            "slug",
            "image",
            "contact_email",
            "contact_phone",
            "dean",
        ]

    def get_dean(self, obj):
        from apps.faculty.serializers import FacultyListSerializer

        dean = getattr(obj, "dean", None)
        if dean:
            return FacultyListSerializer(dean, context=self.context).data
        return None


class SchoolDetailSerializer(BaseSchoolSerializer):
    dean = serializers.SerializerMethodField()
    departments = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = "__all__"

    def get_dean(self, obj):
        from apps.faculty.serializers import FacultyListSerializer

        dean = getattr(obj, "dean", None)
        if dean:
            return FacultyListSerializer(dean, context=self.context).data
        return None

    def get_departments(self, obj):
        return [
            {"id": dept.id, "name": dept.name, "slug": dept.slug, "campus": dept.campus}
            for dept in obj.departments.all()
        ]


class DepartmentGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentGallery
        fields = "__all__"


class BaseDepartmentSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)
    school_slug = serializers.CharField(source="school.slug", read_only=True)

    class Meta:
        model = Department
        fields = "__all__"


class DepartmentListSerializer(BaseDepartmentSerializer):
    hod = serializers.SerializerMethodField()

    class Meta(BaseDepartmentSerializer.Meta):
        fields = [
            "id",
            "name",
            "slug",
            "campus",
            "school",
            "school_name",
            "school_slug",
            "contact_email",
            "contact_phone",
            "hod",
        ]

    def get_hod(self, obj):
        from apps.faculty.serializers import FacultyListSerializer

        hod = getattr(obj, "hod", None)
        if hod:
            return FacultyListSerializer(hod, context=self.context).data
        return None


class DepartmentDetailSerializer(BaseDepartmentSerializer):
    hod = serializers.SerializerMethodField()
    gallery_images = DepartmentGallerySerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = "__all__"

    def get_hod(self, obj):
        from apps.faculty.serializers import FacultyListSerializer

        hod = getattr(obj, "hod", None)
        if hod:
            return FacultyListSerializer(hod, context=self.context).data
        return None


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class CBCSCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CBCSCourse
        fields = "__all__"


class BaseProgramSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    school_name = serializers.CharField(source="department.school.name", read_only=True)

    class Meta:
        model = Program
        fields = "__all__"


class ProgramListSerializer(BaseProgramSerializer):
    courses = CourseSerializer(many=True, read_only=True)

    class Meta(BaseProgramSerializer.Meta):
        fields = [
            "id",
            "name",
            "level",
            "duration",
            "intake",
            "department",
            "department_name",
            "school_name",
            "fees",
            "courses",
            "syllabus",
        ]


class ProgramDetailSerializer(BaseProgramSerializer):
    courses = CourseSerializer(many=True, read_only=True)

    class Meta(BaseProgramSerializer.Meta):
        fields = "__all__"


class NoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = "__all__"


class NoticeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = "__all__"


class CommitteeMemberSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source="faculty.name", read_only=True)

    class Meta:
        model = CommitteeMember
        fields = "__all__"


class CommitteeSerializer(serializers.ModelSerializer):
    members = CommitteeMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Committee
        fields = "__all__"


class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = "__all__"


class StudyMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = "__all__"
