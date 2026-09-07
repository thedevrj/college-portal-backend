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
            return Response(serializer.data, status=status.HTTP_200_OK)
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
