from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorityViewSet, AuthorityMemberViewSet, AuthorityMinutesViewSet

router = DefaultRouter()
router.register(r'authorities', AuthorityViewSet)
router.register(r'members', AuthorityMemberViewSet)
router.register(r'minutes', AuthorityMinutesViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
