from rest_framework import viewsets, permissions

from .models import Resource, CommitteeMember, FAQ, EmergencyContact
from .serializers import (
    ResourceSerializer,
    CommitteeMemberSerializer,
    FAQSerializer,
    EmergencyContactSerializer,
)


class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Resource.objects.filter(is_active=True)
    serializer_class = ResourceSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category", None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class CommitteeMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommitteeMember.objects.all()
    serializer_class = CommitteeMemberSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        committee_type = self.request.query_params.get("committee_type", None)
        if committee_type:
            queryset = queryset.filter(committee_type=committee_type)
        return queryset


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class EmergencyContactViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmergencyContact.objects.all()
    serializer_class = EmergencyContactSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
