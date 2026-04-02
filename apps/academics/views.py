from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    School, Department, Program, Notice, Committee, 
    ResearchProject, ResearchScholar, Timetable, StudyMaterial
)
from .serializers import (
    SchoolSerializer, DepartmentSerializer, ProgramSerializer, NoticeSerializer,
    CommitteeSerializer, ResearchProjectSerializer, ResearchScholarSerializer,
    TimetableSerializer, StudyMaterialSerializer
)

class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    lookup_field = 'slug'

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['school__slug']
    lookup_field = 'slug'

class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department__slug', 'level']

class NoticeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notice.objects.filter(is_active=True).order_by('-date_posted')
    serializer_class = NoticeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department__slug']

class CommitteeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department__slug']

class ResearchProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResearchProject.objects.all()
    serializer_class = ResearchProjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department__slug', 'status']

class ResearchScholarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResearchScholar.objects.all()
    serializer_class = ResearchScholarSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department__slug', 'registration_year']

class TimetableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department__slug', 'program']

class StudyMaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudyMaterial.objects.all()
    serializer_class = StudyMaterialSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department__slug', 'program']