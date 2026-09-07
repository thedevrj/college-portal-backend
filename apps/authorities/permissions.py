from rest_framework import permissions
from apps.accounts.models import PortalRole


class BaseAuthorityPermission(permissions.BasePermission):
    """
    Base permission for all authorities, allowing SAFE_METHODS (GET) for anyone,
    and enforcing roles for modification actions.
    """
    allowed_roles = []

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        user_roles = request.user.access_entries.filter(is_active=True).values_list(
            "role", flat=True
        )

        return any(role in user_roles for role in self.allowed_roles)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        user_roles = request.user.access_entries.filter(is_active=True).values_list(
            "role", flat=True
        )

        return any(role in user_roles for role in self.allowed_roles)


class IsAcademicCouncilManager(BaseAuthorityPermission):
    allowed_roles = [PortalRole.ACADEMIC_SECTION, PortalRole.REGISTRAR]


class IsFinanceCommitteeManager(BaseAuthorityPermission):
    allowed_roles = [PortalRole.FINANCE_SECTION]


class IsPlanningBoardManager(BaseAuthorityPermission):
    allowed_roles = [PortalRole.REGISTRAR]


class IsBoardOfManagementManager(BaseAuthorityPermission):
    allowed_roles = [PortalRole.REGISTRAR]
