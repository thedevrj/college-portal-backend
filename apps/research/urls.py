from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ResearchAreaViewSet, ResearchFacilityViewSet, 
    ResearchProjectViewSet, ResearchScholarViewSet,
    PublicationViewSet, PatentViewSet,
    ResearchDevelopmentCellMemberViewSet
)

router = DefaultRouter()
router.register(r'research-areas', ResearchAreaViewSet)
router.register(r'research-facilities', ResearchFacilityViewSet)
router.register(r'research-projects', ResearchProjectViewSet)
router.register(r'research-scholars', ResearchScholarViewSet)
router.register(r'publications', PublicationViewSet)
router.register(r'patents', PatentViewSet)
router.register(r'rd-cell-team', ResearchDevelopmentCellMemberViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
