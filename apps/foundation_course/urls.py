from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FoundationCourseViewSet,
    FoundationCourseMaterialViewSet,
)

router = DefaultRouter()
router.register(
    r"foundation-courses", FoundationCourseViewSet, basename="foundation-course"
)
router.register(
    r"foundation-course-materials",
    FoundationCourseMaterialViewSet,
    basename="foundation-course-material",
)

urlpatterns = [
    path("", include(router.urls)),
]
