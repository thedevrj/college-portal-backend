from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GrievanceCreateView,
    GrievanceStatusView,
    AdminGrievanceViewSet,
    ICCCreateView,
    ICCStatusView,
    DiscriminationCreateView,
    DiscriminationStatusView,
    FeedbackCreateView,
    FeedbackStatusView,
)

router = DefaultRouter()
router.register(r"admin/grievances", AdminGrievanceViewSet, basename="admin-grievance")

urlpatterns = [
    path("grievance/submit/",GrievanceCreateView.as_view(),name="grievance-submit",),
    path("grievance/status/<str:tracking_id>/",GrievanceStatusView.as_view(),name="grievance-status",),
    path("icc/submit/",ICCCreateView.as_view(),name="icc-submit",),
    path("icc/status/<str:tracking_id>/", ICCStatusView.as_view(), name="icc-status"),
    path("discrimination/submit/",DiscriminationCreateView.as_view(),name="discrimination-submit",),
    path("discrimination/status/<str:tracking_id>/",DiscriminationStatusView.as_view(),name="discrimination-status",),
    path("feedback/submit/",FeedbackCreateView.as_view(),name="feedback-submit",),
    path("feedback/status/<str:tracking_id>/",FeedbackStatusView.as_view(),name="feedback-status",),
    path("", include(router.urls)),
]
