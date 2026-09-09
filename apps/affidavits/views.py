from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Affidavit, AffidavitFAQ, AffidavitGuidelines, SampleAffidavit
from .serializers import (
    AffidavitSerializer,
    AffidavitFAQSerializer,
    AffidavitGuidelinesSerializer,
    SampleAffidavitSerializer,
)


class AffidavitViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Affidavit.objects.all()
    serializer_class = AffidavitSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action == "list":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=False, methods=["get"], url_path="track/(?P<tracking_id>[^/.]+)")
    def track(self, request, tracking_id=None):
        try:
            affidavit = Affidavit.objects.get(tracking_id=tracking_id)
            serializer = self.get_serializer(affidavit)

            # History of Timeline
            history_timeline = []
            prev_status = None
            prev_remarks = None

            historical_records = list(affidavit.history.all().order_by("history_date"))
            if historical_records:
                for idx, h in enumerate(historical_records):
                    status_display = h.get_status_display()
                    
                    if idx == 0 or h.history_type == "+":
                        change_desc = "Affidavit submitted online by student."
                        action_label = "Submitted"
                    else:
                        changes = []
                        if prev_status != h.status:
                            changes.append(f"Status changed to {status_display}")
                        if h.remarks and h.remarks != prev_remarks:
                            changes.append(f"Remarks: {h.remarks}")
                        change_desc = " | ".join(changes) if changes else f"Details updated (Status: {status_display})"
                        action_label = "Status Updated"

                    history_timeline.append({
                        "date": h.history_date,
                        "status": h.status,
                        "status_display": status_display,
                        "remarks": h.remarks or "",
                        "description": change_desc,
                        "action": action_label,
                    })
                    prev_status = h.status
                    prev_remarks = h.remarks
            else:
                history_timeline.append({
                    "date": affidavit.submitted_on,
                    "status": affidavit.status,
                    "status_display": affidavit.get_status_display(),
                    "remarks": affidavit.remarks or "",
                    "description": "Affidavit submitted online by student.",
                    "action": "Submitted",
                })

            response_data = {
                **serializer.data,
                "status_display": affidavit.get_status_display(),
                "history": history_timeline,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Affidavit.DoesNotExist:
            return Response(
                {"error": "Affidavit with the given tracking ID was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class AffidavitFAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AffidavitFAQ.objects.all()
    serializer_class = AffidavitFAQSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class AffidavitGuidelinesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AffidavitGuidelines.objects.all()
    serializer_class = AffidavitGuidelinesSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

class SampleAffidavitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SampleAffidavit.objects.all()
    serializer_class = SampleAffidavitSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category", None)
        if category:
            queryset = queryset.filter(affidavit_category=category)
        return queryset
