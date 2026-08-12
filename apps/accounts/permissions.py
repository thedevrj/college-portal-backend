from rest_framework.permissions import BasePermission
from .models import PortalRole, EntityType


class IsPortalUser(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.portal_profile.is_portal_user
        except Exception:
            return False


class IsHOD(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.access_entries.filter(
            role=PortalRole.HOD, is_active=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        try:
            dept = request.user.portal_profile.get_department()
        except Exception:
            return False
        if dept is None:
            return False
        return getattr(obj, "department", None) == dept


class IsDeptStaffOrAbove(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.access_entries.filter(
            role__in=[PortalRole.HOD, PortalRole.DEPT_STAFF, PortalRole.RD_ADMIN],
            is_active=True,
        ).exists()

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        try:
            profile = request.user.portal_profile
            if profile.is_rd_admin():
                return True
            dept = profile.get_department()
        except Exception:
            return False
        if dept is None:
            return False
        return getattr(obj, "department", None) == dept


class IsRDAdmin(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            return request.user.portal_profile.is_rd_admin()
        except Exception:
            return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsRDAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        from rest_framework.permissions import SAFE_METHODS

        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        try:
            return request.user.portal_profile.is_rd_admin()
        except Exception:
            return False
