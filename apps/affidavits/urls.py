from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AffidavitViewSet,
    AffidavitFAQViewSet,
    AffidavitGuidelinesViewSet,
    SampleAffidavitViewSet
)

router = DefaultRouter()
router.register(r"affidavits", AffidavitViewSet, basename="affidavit")
router.register(r"affidavit-faqs", AffidavitFAQViewSet, basename="affidavit-faq")
router.register(r"affidavit-guidelines", AffidavitGuidelinesViewSet, basename="affidavit-guideline")
router.register(r"sample-affidavits", SampleAffidavitViewSet, basename="sample-affidavit")

urlpatterns = [
    path("", include(router.urls)),
]
