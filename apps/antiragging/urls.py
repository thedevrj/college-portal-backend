from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ResourceViewSet,
    CommitteeMemberViewSet,
    FAQViewSet,
    EmergencyContactViewSet,
)

router = DefaultRouter()
router.register(r"resources", ResourceViewSet, basename="antiragging-resource")
router.register(r"antiragging-committee-members", CommitteeMemberViewSet, basename="antiragging-committee-member")
router.register(r"antiragging-faqs", FAQViewSet, basename="antiragging-faq")
router.register(r"emergency-contacts", EmergencyContactViewSet, basename="antiragging-emergency-contact")

urlpatterns = [
    path("", include(router.urls)),
]
