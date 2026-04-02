from rest_framework import serializers
from .models import (
    School, Department, Program, Notice, Committee, 
    CommitteeMember, ResearchProject, ResearchScholar, 
    Timetable, StudyMaterial
)

class SchoolSerializer(serializers.ModelSerializer):
    dean = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = '__all__'

    def get_dean(self, obj):
        from apps.faculty.serializers import FacultySerializer
        dean = getattr(obj, 'DEAN', None)
        if dean:
            return FacultySerializer(dean, context=self.context).data
        return None

class DepartmentSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    hod = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = '__all__'

    def get_hod(self, obj):
        from apps.faculty.serializers import FacultySerializer
        hod = getattr(obj, 'hod', None)
        if hod:
            return FacultySerializer(hod, context=self.context).data
        return None

class ProgramSerializer(serializers.ModelSerializer):
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