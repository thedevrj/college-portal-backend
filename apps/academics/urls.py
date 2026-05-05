from posixpath import basename
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SchoolViewSet,
    SchoolBoardCommitteeViewSet,
    SchoolBoardMOMViewSet,
    DepartmentViewSet,
    ProgramViewSet,
    CourseViewSet,
    CBCSCourseViewSet,
    NoticeViewSet,
    CommitteeViewSet,
    MinutesViewSet,
    TimetableViewSet,
    StudyMaterialViewSet,
)

router = DefaultRouter()
router.register(r"schools", SchoolViewSet, basename="school")
router.register(
    r"school-board-committees",
    SchoolBoardCommitteeViewSet,
    basename="school-board-committee",
)
router.register(
    r"school-board-minutes", SchoolBoardMOMViewSet, basename="school-board-mom"
)
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"programs", ProgramViewSet, basename="program")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"cbcs", CBCSCourseViewSet, basename="cbcs-course")
router.register(r"notices", NoticeViewSet, basename="notice")
router.register(r"dept-committees", CommitteeViewSet, basename="dept-committee")
router.register(r"dept-minutes", MinutesViewSet, basename="dept-minutes")
router.register(r"timetables", TimetableViewSet, basename="timetable")
router.register(r"study-materials", StudyMaterialViewSet, basename="studymaterial")

urlpatterns = [
    path("", include(router.urls)),
]
