from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Complaint, FAQ, PolicyDocument, ComplaintActionLog
from .serializers import (
    ComplaintSerializer,
    FAQSerializer,
    PolicyDocumentSerializer,
)


class ComplaintCreateView(generics.CreateAPIView):

    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [AllowAny]
    # Optionally add throttling here if needed


class ComplaintStatusView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, tracking_id):
        complaint = get_object_or_404(Complaint, tracking_id=tracking_id)

        history = []
        history.append(
            {
                "date": complaint.submitted_at,
                "status": "pending",
                "status_display": "Pending",
                "description": "Complaint successfully submitted and is pending review.",
            }
        )

        # Action logs
        for log in complaint.action_logs.all().order_by("timestamp"):
            status_display = ""
            if log.status_changed_to:
                status_display = dict(Complaint.STATUS_CHOICES).get(
                    log.status_changed_to, log.status_changed_to
                )

            history.append(
                {
                    "date": log.timestamp,
                    "status": (
                        log.status_changed_to
                        if log.status_changed_to
                        else complaint.status
                    ),
                    "status_display": status_display,
                    "description": log.action_description,
                }
            )

        return Response(
            {
                "tracking_id": complaint.tracking_id,
                "category": complaint.get_category_display(),
                "status": complaint.status,
                "status_display": complaint.get_status_display(),
                "submitted_at": complaint.submitted_at,
                "updated_at": complaint.updated_at,
                "history": history,
            },
            status=status.HTTP_200_OK,
        )


class FAQListView(generics.ListAPIView):

    # Public API to list all FAQs.

    queryset = FAQ.objects.all().order_by("order")
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]


class PolicyDocumentListView(generics.ListAPIView):

    # Public API to list all policy documents, SOPs, and reports.

    queryset = PolicyDocument.objects.all().order_by("-uploaded_at")
    serializer_class = PolicyDocumentSerializer
    permission_classes = [AllowAny]


class AdminComplaintViewSet(viewsets.ModelViewSet):

    # Private API for Vigilance Officers to manage complaints.

    queryset = Complaint.objects.all().order_by("-submitted_at")
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_status = old_instance.status
        old_status_display = old_instance.get_status_display()

        new_instance = serializer.save()

        if old_status != new_instance.status:
            ComplaintActionLog.objects.create(
                complaint=new_instance,
                action_taken_by=self.request.user,
                action_description=f"Status updated from {old_status_display} to {new_instance.get_status_display()}",
                status_changed_to=new_instance.status,
            )
