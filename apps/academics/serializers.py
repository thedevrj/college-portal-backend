from rest_framework import serializers
from .models import (
    School, Department, Program, Course, CBCSCourse, DepartmentGallery, Notice, Committee, 
    CommitteeMember, ResearchProject, ResearchScholar, 
    Timetable, StudyMaterial
)

class SchoolSerializer(serializers.ModelSerializer):
    dean = serializers.SerializerMethodField()
    departments = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = '__all__'

    def get_dean(self, obj):
        from apps.faculty.serializers import FacultySerializer
        dean = getattr(obj, 'dean', None)
        if dean:
            return FacultySerializer(dean, context=self.context).data
        return None

    def get_departments(self, obj):
        return [{"id": dept.id, "name": dept.name, "slug": dept.slug} for dept in obj.departments.all()]

class DepartmentGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentGallery
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    hod = serializers.SerializerMethodField()
    gallery_images = DepartmentGallerySerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = '__all__'

    def get_hod(self, obj):
        from apps.faculty.serializers import FacultySerializer
        hod = getattr(obj, 'hod', None)
        if hod:
            return FacultySerializer(hod, context=self.context).data
        return None

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class CBCSCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CBCSCourse
        fields = '__all__'

class ProgramSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)
    cbcs_courses = CBCSCourseSerializer(many=True, read_only=True)

    class Meta:
        model = Program
        fields = '__all__'

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'

class CommitteeMemberSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    class Meta:
        model = CommitteeMember
        fields = '__all__'

class CommitteeSerializer(serializers.ModelSerializer):
    members = CommitteeMemberSerializer(many=True, read_only=True)
    class Meta:
        model = Committee
        fields = '__all__'

class ResearchProjectSerializer(serializers.ModelSerializer):
    pi_name = serializers.CharField(source='principal_investigator.name', read_only=True)
    class Meta:
        model = ResearchProject
        fields = '__all__'

class ResearchScholarSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.CharField(source='supervisor.name', read_only=True)
    class Meta:
        model = ResearchScholar
        fields = '__all__'

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'

class StudyMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = '__all__'