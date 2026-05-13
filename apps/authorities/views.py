from rest_framework import viewsets, permissions
from .models import Authority, AuthorityMember, AuthorityMinutes
from .serializers import AuthoritySerializer, AuthorityMemberSerializer, AuthorityMinutesSerializer
from .permissions import IsAuthorityManager

class AuthorityViewSet(viewsets.ModelViewSet):
    queryset = Authority.objects.all()
    serializer_class = AuthoritySerializer
    permission_classes = [IsAuthorityManager]
    lookup_field = 'name' # Allow lookup by name (ACADEMIC_COUNCIL, etc.)

class AuthorityMemberViewSet(viewsets.ModelViewSet):
    queryset = AuthorityMember.objects.all()
    serializer_class = AuthorityMemberSerializer
    permission_classes = [IsAuthorityManager]
    filterset_fields = ['authority__name']

class AuthorityMinutesViewSet(viewsets.ModelViewSet):
    queryset = AuthorityMinutes.objects.all()
    serializer_class = AuthorityMinutesSerializer
    permission_classes = [IsAuthorityManager]
    filterset_fields = ['authority__name']
