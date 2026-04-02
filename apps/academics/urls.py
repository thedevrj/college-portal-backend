from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SchoolViewSet, DepartmentViewSet, ProgramViewSet, NoticeViewSet,
    CommitteeViewSet, ResearchProjectViewSet, ResearchScholarViewSet,
    TimetableViewSet, StudyMaterialViewSet
)

router = DefaultRouter()
router.register(r'schools', SchoolViewSet, basename='school')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'programs', ProgramViewSet, basename='program')
router.register(r'notices', NoticeViewSet, basename='notice')
router.register(r'committees', CommitteeViewSet, basename='committee')
router.register(r'research-projects', ResearchProjectViewSet, basename='researchproject')
router.register(r'research-scholars', ResearchScholarViewSet, basename='researchscholar')
router.register(r'timetables', TimetableViewSet, basename='timetable')
router.register(r'study-materials', StudyMaterialViewSet, basename='studymaterial')

urlpatterns = [
    path('', include(router.urls)),
]