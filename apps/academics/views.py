from rest_framework import viewsets, filters
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

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
    BaseProgramSerializer,
    ProgramListSerializer,
    ProgramDetailSerializer,
    CourseSerializer,
    CBCSCourseSerializer,
    NoticeListSerializer,
    NoticeDetailSerializer,
    CommitteeSerializer,
    MinutesSerializer,
    TimetableSerializer,
    StudyMaterialSerializer,
)


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.select_related("dean").prefetch_related("departments")
    lookup_field = "slug"
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "list":
            return SchoolListSerializer
        return SchoolDetailSerializer


class SchoolBoardCommitteeFilter(django_filters.FilterSet):
    school_slug = django_filters.CharFilter(field_name="school__slug")
    school__slug = django_filters.CharFilter(field_name="school__slug")

    class Meta:
        model = SchoolBoardCommittee
        fields = []


class SchoolBoardCommitteeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SchoolBoardCommittee.objects.all().prefetch_related("members")
    serializer_class = SchoolBoardCommitteeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SchoolBoardCommitteeFilter
    pagination_class = None


class SchoolBoardMOMFilter(django_filters.FilterSet):
    school_slug = django_filters.CharFilter(field_name="school__slug")
    school__slug = django_filters.CharFilter(field_name="school__slug")

    class Meta:
        model = SchoolBoardMOM
        fields = ["date_of_meeting"]


class SchoolBoardMOMViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SchoolBoardMOM.objects.all()
    serializer_class = SchoolBoardMOMSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SchoolBoardMOMFilter


class DepartmentFilter(django_filters.FilterSet):
    school_slug = django_filters.CharFilter(field_name="school__slug")
    school__slug = django_filters.CharFilter(field_name="school__slug")

    class Meta:
        model = Department
        fields = ["campus"]


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.select_related("school", "hod")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DepartmentFilter
    search_fields = ["name"]
    lookup_field = "slug"
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "list":
            return DepartmentListSerializer
        return DepartmentDetailSerializer


class ProgramFilter(django_filters.FilterSet):
    centre_slug = django_filters.CharFilter(field_name="centre__slug")
    department_slug = django_filters.CharFilter(field_name="department__slug")
    centre__slug = django_filters.CharFilter(field_name="centre__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")

    class Meta:
        model = Program
        fields = ["level", "department", "centre"]


class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Program.objects.select_related(
        "department", "department__school", "centre"
    ).prefetch_related("courses")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProgramFilter
    search_fields = ["name"]

    def get_serializer_class(self):
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


class CBCSCourseFilter(django_filters.FilterSet):
    centre_slug = django_filters.CharFilter(field_name="centre__slug")
    department_slug = django_filters.CharFilter(field_name="department__slug")
    centre__slug = django_filters.CharFilter(field_name="centre__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")

    class Meta:
        model = CBCSCourse
        fields = ["semester"]


class CBCSCourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CBCSCourse.objects.all()
    serializer_class = CBCSCourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CBCSCourseFilter
    search_fields = ["course_title", "course_code"]


class NoticeFilter(django_filters.FilterSet):
    centre_slug = django_filters.CharFilter(field_name="centre__slug")
    department_slug = django_filters.CharFilter(field_name="department__slug")
    centre__slug = django_filters.CharFilter(field_name="centre__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")

    class Meta:
        model = Notice
        fields = ["category"]


class NoticeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Notice.objects.filter(is_active=True)
        .select_related("department", "centre")
        .order_by("-date_posted")
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = NoticeFilter
    search_fields = ["title", "content"]

    def get_serializer_class(self):
        if self.action == "list":
            return NoticeListSerializer
        return NoticeDetailSerializer


class CommitteeFilter(django_filters.FilterSet):
    centre_slug = django_filters.CharFilter(field_name="centre__slug")
    department_slug = django_filters.CharFilter(field_name="department__slug")
    centre__slug = django_filters.CharFilter(field_name="centre__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")

    class Meta:
        model = Committee
        fields = []


class CommitteeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CommitteeFilter
    pagination_class = None


class MinutesFilter(django_filters.FilterSet):
    centre_slug = django_filters.CharFilter(field_name="centre__slug")
    department_slug = django_filters.CharFilter(field_name="department__slug")
    centre__slug = django_filters.CharFilter(field_name="centre__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")

    class Meta:
        model = MinutesOfTheMeeting
        fields = []


class MinutesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MinutesOfTheMeeting.objects.all()
    serializer_class = MinutesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MinutesFilter


class TimetableFilter(django_filters.FilterSet):
    centre_slug = django_filters.CharFilter(field_name="centre__slug")
    department_slug = django_filters.CharFilter(field_name="department__slug")
    centre__slug = django_filters.CharFilter(field_name="centre__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")

    class Meta:
        model = Timetable
        fields = ["program"]


class TimetableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TimetableFilter
    search_fields = ["title", "program__name"]


class StudyMaterialFilter(django_filters.FilterSet):
    centre_slug = django_filters.CharFilter(field_name="centre__slug")
    department_slug = django_filters.CharFilter(field_name="department__slug")
    centre__slug = django_filters.CharFilter(field_name="centre__slug")
    department__slug = django_filters.CharFilter(field_name="department__slug")

    class Meta:
        model = StudyMaterial
        fields = ["program"]


class StudyMaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudyMaterial.objects.all()
    serializer_class = StudyMaterialSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = StudyMaterialFilter
    search_fields = ["title", "program__name"]
