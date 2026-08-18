from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Grievance, GrievanceActionLog
from .serializers import (
    GrievanceSerializer,
    GrievanceStatusSerializer,
    GrievanceStatusUpdateSerializer,
)
from .permissions import IsGrievanceOfficer


class GrievanceCreateView(generics.CreateAPIView):

    queryset = Grievance.objects.all()
    serializer_class = GrievanceSerializer
    permission_classes = [AllowAny]


class GrievanceStatusView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, tracking_id):
        grievance = get_object_or_404(
            Grievance, tracking_id=tracking_id, is_deleted=False
        )

        history = [
            {
                "date": grievance.submitted_at,
                "status": "pending",
                "status_display": "Pending",
                "description": "Grievance successfully submitted and is pending review.",
            }
        ]

        for log in grievance.action_logs.all().order_by("timestamp"):
            status_display = ""
            if log.status_changed_to:
                status_display = dict(Grievance.STATUS_CHOICES).get(
                    log.status_changed_to, log.status_changed_to
                )
            history.append(
                {
                    "date": log.timestamp,
                    "status": log.status_changed_to or grievance.status,
                    "status_display": status_display,
                    "description": log.action_description,
                }
            )

        serializer = GrievanceStatusSerializer(grievance)
        return Response(
            {**serializer.data, "history": history},
            status=status.HTTP_200_OK,
        )


class AdminGrievanceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Grievance.objects.filter(is_deleted=False).order_by("-submitted_at")
    serializer_class = GrievanceSerializer
    permission_classes = [IsGrievanceOfficer]
    http_method_names = ["get", "head", "options", "put", "patch"]

    def get_serializer_class(self):
        if self.action in {"update", "partial_update"}:
            return GrievanceStatusUpdateSerializer
        return GrievanceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get("status")
        nature_param = self.request.query_params.get("nature")
        complainant_param = self.request.query_params.get("complainant_type")

        if status_param:
            queryset = queryset.filter(status=status_param)
        if nature_param:
            queryset = queryset.filter(nature_of_grievance=nature_param)
        if complainant_param:
            queryset = queryset.filter(complainant_type=complainant_param)
        return queryset

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_status = old_instance.status
        old_status_display = old_instance.get_status_display()

        new_instance = serializer.save()

        if old_status != new_instance.status:
            GrievanceActionLog.objects.create(
                grievance=new_instance,
                action_taken_by=self.request.user,
                action_description=(
                    f"Status updated from '{old_status_display}' "
                    f"to '{new_instance.get_status_display()}'"
                ),
                status_changed_to=new_instance.status,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Internal Complaints Committee (ICC) Views
# ─────────────────────────────────────────────────────────────────────────────
from .models import ICCComplaint, ICCActionLog
from .serializers import ICCComplaintSerializer, ICCStatusSerializer


class ICCCreateView(generics.CreateAPIView):
    """
    POST /api/v1/portals/icc/submit/
    """

    queryset = ICCComplaint.objects.all()
    serializer_class = ICCComplaintSerializer
    permission_classes = [AllowAny]


class ICCStatusView(APIView):
    """
    GET /api/v1/portals/icc/status/<tracking_id>/
    """

    permission_classes = [AllowAny]

    def get(self, request, tracking_id):
        complaint = get_object_or_404(
            ICCComplaint, tracking_id=tracking_id, is_deleted=False
        )

        history = [
            {
                "date": complaint.submitted_at,
                "status": "pending",
                "status_display": "Pending",
                "description": "Complaint successfully submitted and is pending review.",
            }
        ]

        for log in complaint.action_logs.all().order_by("timestamp"):
            status_display = ""
            if log.status_changed_to:
                status_display = dict(ICCComplaint.STATUS_CHOICES).get(
                    log.status_changed_to, log.status_changed_to
                )
            history.append(
                {
                    "date": log.timestamp,
                    "status": log.status_changed_to or complaint.status,
                    "status_display": status_display,
                    "description": log.action_description,
                }
            )

        serializer = ICCStatusSerializer(complaint)
        return Response(
            {**serializer.data, "history": history},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# SC/ST, OBC, Disable & Minority Discrimination Views
# ─────────────────────────────────────────────────────────────────────────────
from .models import DiscriminationComplaint, DiscriminationActionLog
from .serializers import (
    DiscriminationComplaintSerializer,
    DiscriminationStatusSerializer,
)


class DiscriminationCreateView(generics.CreateAPIView):
    """
    POST /api/v1/portals/discrimination/submit/
    """

    queryset = DiscriminationComplaint.objects.all()
    serializer_class = DiscriminationComplaintSerializer
    permission_classes = [AllowAny]


class DiscriminationStatusView(APIView):
    """
    GET /api/v1/portals/discrimination/status/<tracking_id>/
    """

    permission_classes = [AllowAny]

    def get(self, request, tracking_id):
        complaint = get_object_or_404(
            DiscriminationComplaint, tracking_id=tracking_id, is_deleted=False
        )

        history = [
            {
                "date": complaint.submitted_at,
                "status": "pending",
                "status_display": "Pending",
                "description": "Complaint successfully submitted and is pending review.",
            }
        ]

        for log in complaint.action_logs.all().order_by("timestamp"):
            status_display = ""
            if log.status_changed_to:
                status_display = dict(DiscriminationComplaint.STATUS_CHOICES).get(
                    log.status_changed_to, log.status_changed_to
                )
            history.append(
                {
                    "date": log.timestamp,
                    "status": log.status_changed_to or complaint.status,
                    "status_display": status_display,
                    "description": log.action_description,
                }
            )

        serializer = DiscriminationStatusSerializer(complaint)
        return Response(
            {**serializer.data, "history": history},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Student Feedback Views
# ─────────────────────────────────────────────────────────────────────────────
from .models import StudentFeedback
from .serializers import StudentFeedbackSerializer, FeedbackStatusSerializer


class FeedbackCreateView(generics.CreateAPIView):
    """
    POST /api/v1/portals/feedback/submit/
    """

    queryset = StudentFeedback.objects.all()
    serializer_class = StudentFeedbackSerializer
    permission_classes = [AllowAny]


class FeedbackStatusView(APIView):
    """
    GET /api/v1/portals/feedback/status/<tracking_id>/
    """

    permission_classes = [AllowAny]

    def get(self, request, tracking_id):
        feedback = get_object_or_404(
            StudentFeedback, tracking_id=tracking_id, is_deleted=False
        )

        history = [
            {
                "date": feedback.submitted_at,
                "status": "pending",
                "status_display": "Pending",
                "description": "Feedback successfully submitted.",
            }
        ]

        for log in feedback.action_logs.all().order_by("timestamp"):
            status_display = ""
            if log.status_changed_to:
                status_display = dict(StudentFeedback.STATUS_CHOICES).get(
                    log.status_changed_to, log.status_changed_to
                )
            history.append(
                {
                    "date": log.timestamp,
                    "status": log.status_changed_to or feedback.status,
                    "status_display": status_display,
                    "description": log.action_description,
                }
            )

        serializer = FeedbackStatusSerializer(feedback)
        return Response(
            {**serializer.data, "history": history},
            status=status.HTTP_200_OK,
        )
