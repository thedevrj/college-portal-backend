from rest_framework import permissions
from apps.accounts.models import PortalRole
from .models import AuthorityType

class IsAuthorityManager(permissions.BasePermission):
    """
    Custom permission to only allow managers of specific authorities to edit them.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Superusers can do anything
        if request.user.is_superuser:
            return True

        user_roles = request.user.access_entries.filter(is_active=True).values_list('role', flat=True)
        
        # Get authority name (handle Member and Minutes objects too)
        authority_name = None
        if hasattr(obj, 'name'): # Authority object
            authority_name = obj.name
        elif hasattr(obj, 'authority'): # Member or Minutes object
            authority_name = obj.authority.name

        if not authority_name:
            return False

        # Mapping Authorities to Roles
        if authority_name in [AuthorityType.BOARD_OF_MANAGEMENT, AuthorityType.PLANNING_BOARD]:
            return PortalRole.REGISTRAR in user_roles
        
        if authority_name == AuthorityType.FINANCE_COMMITTEE:
            return PortalRole.FINANCE_SECTION in user_roles
        
        if authority_name == AuthorityType.ACADEMIC_COUNCIL:
            return PortalRole.ACADEMIC_SECTION in user_roles or PortalRole.REGISTRAR in user_roles

        return False
