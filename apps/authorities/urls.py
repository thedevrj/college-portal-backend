from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorityViewSet, AuthorityMemberViewSet, AuthorityMinutesViewSet

router = DefaultRouter()
router.register(r"authorities", AuthorityViewSet)
router.register(r"authorities-members", AuthorityMemberViewSet)
router.register(r"authorities-minutes", AuthorityMinutesViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
