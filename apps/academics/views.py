from django_filters.filters import QuerySetRequestMixin
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    School,
    SchoolBoardCommittee,
    SchoolBoardMOM,
    Department,
    Program,
    Course,
    CBCSCourse,
    Notice,
    Committee,
    MinutesOfTheMeeting,
    Timetable,
    StudyMaterial,
)
from .serializers import (
    SchoolListSerializer,
    SchoolDetailSerializer,
    SchoolBoardCommitteeSerializer,
    SchoolBoardMOMSerializer,
    DepartmentListSerializer,
    DepartmentDetailSerializer,
    ProgramListSerializer,
    ProgramDetailSerializer,
    CourseSerializer,
    CBCSCourseSerializer,
    NoticeListSerializer,
    NoticeDetailSerializer,
    CommitteeSerializer,
    MinutesSerialization,
    TimetableSerializer,
    StudyMaterialSerializer,
)


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    lookup_field = "slug"
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "list":
            return SchoolListSerializer
        return SchoolDetailSerializer


class SchoolBoardCommitteeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SchoolBoardCommittee.objects.all()
    serializer_class = SchoolBoardCommitteeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["school__slug"]
    pagination_class = None


class SchoolBoardMOMViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SchoolBoardMOM.objects.all()
    serializer_class = SchoolBoardMOMSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["school__slug"]


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["school__slug", "campus"]
    search_fields = ["name"]
    lookup_field = "slug"
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "list":
            return DepartmentListSerializer
        return DepartmentDetailSerializer


from rest_framework.decorators import action
from rest_framework.response import Response


class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Program.objects.all().prefetch_related("courses")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["department", "department__slug", "level"]
    search_fields = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProgramListSerializer
        return ProgramDetailSerializer

    @action(detail=True, methods=["get"])
    def courses(self, request, pk=None):
        program = self.get_object()
        from .serializers import CourseSerializer

        courses = CourseSerializer(program.courses.all(), many=True).data
        return Response({"courses": courses})


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["program", "program__name", "semester", "course_type"]
    search_fields = ["course_title", "course_code"]


class CBCSCourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CBCSCourse.objects.all()
    serializer_class = CBCSCourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["department", "department__slug", "semester"]
    search_fields = ["course_title", "course_code"]


class NoticeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notice.objects.filter(is_active=True).order_by("-date_posted")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["department__slug", "category"]
    search_fields = ["title", "content"]

    def get_serializer_class(self):
        if self.action == "list":
            return NoticeListSerializer
        return NoticeDetailSerializer


class CommitteeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["department__slug"]
    pagination_class = None


class MinutesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MinutesOfTheMeeting.objects.all()
    serializer_class = MinutesSerialization
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["department__slug"]


class TimetableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["department__slug", "program"]
    search_fields = ["title", "program__name"]


class StudyMaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudyMaterial.objects.all()
    serializer_class = StudyMaterialSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["department__slug", "program"]
    search_fields = ["title", "program__name"]
