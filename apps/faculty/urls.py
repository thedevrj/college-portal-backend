from rest_framework.routers import DefaultRouter
from .views import FacultyViewSet

router = DefaultRouter()
router.register("faculty", FacultyViewSet)

urlpatterns = router.urls