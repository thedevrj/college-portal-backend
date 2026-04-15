from rest_framework import serializers
from .models import (
    ResearchArea, ResearchFacility, ResearchProject, ResearchScholar,
    Publication, Patent, ResearchDevelopmentCellMember
)
from apps.faculty.serializers import FacultyListSerializer

class ResearchAreaSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    class Meta:
        model = ResearchArea
        fields = ['id', 'name', 'description', 'department', 'department_name']

class ResearchFacilitySerializer(serializers.ModelSerializer):
    incharge_name = serializers.CharField(source='incharge.name', read_only=True)
    class Meta:
        model = ResearchFacility
        fields = '__all__'

class ResearchProjectListSerializer(serializers.ModelSerializer):
    pi_name = serializers.CharField(source='principal_investigator.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_slug = serializers.CharField(source='department.slug', read_only=True)
    co_investigators_names = serializers.SerializerMethodField()
    
    class Meta:
        model = ResearchProject
        fields = [
            'id', 'title', 'pi_name', 'co_investigators_names', 'funding_agency', 
            'amount_sanctioned', 'status', 'department_name', 'department_slug'
        ]

    def get_co_investigators_names(self, obj):
        return [faculty.name for faculty in obj.co_investigators.all()]

class ResearchProjectDetailSerializer(serializers.ModelSerializer):
    principal_investigator = FacultyListSerializer(read_only=True)
    co_investigators = FacultyListSerializer(many=True, read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_slug = serializers.CharField(source='department.slug', read_only=True)

    class Meta:
        model = ResearchProject
        fields = '__all__'

class ResearchScholarListSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.CharField(source='supervisor.name', read_only=True)
    co_supervisor_name = serializers.CharField(source='co_supervisor.name', read_only=True, default=None)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_slug = serializers.CharField(source='department.slug', read_only=True)

    class Meta:
        model = ResearchScholar
        fields = [
            'id', 'scholar_name', 'enrollment_no', 'supervisor_name', 'co_supervisor_name',
            'registration_year', 'status', 'department_name', 'department_slug'
        ]

class ResearchScholarDetailSerializer(serializers.ModelSerializer):
    supervisor = FacultyListSerializer(read_only=True)
    co_supervisor = FacultyListSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = ResearchScholar
        fields = '__all__'

class PublicationSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Publication
        fields = '__all__'

class PatentSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Patent
        fields = '__all__'

class ResearchDevelopmentCellMemberSerializer(serializers.ModelSerializer):
    faculty = FacultyListSerializer(read_only=True)

    class Meta:
        model = ResearchDevelopmentCellMember
        fields = ['id', 'faculty', 'designation', 'order']
