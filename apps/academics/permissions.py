from rest_framework import permissions

class IsDepartmentAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users who are linked to a department
    to manage data for that department.
    """

    def _get_managed_departments(self, user):
        if not user or not user.is_authenticated:
            return []
        
        # Superusers can manage everything
        if user.is_superuser:
            return "ALL"

        try:
            access_entries = user.access_entries.filter(entity_type='DEPARTMENT', is_active=True)
            return [access.entity for access in access_entries if access.entity]
        except Exception:
            return []

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        managed_depts = self._get_managed_departments(request.user)
        return bool(managed_depts)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        managed_depts = self._get_managed_departments(request.user)
        
        if managed_depts == "ALL":
            return True

        # For models linked directly to a department
        if hasattr(obj, 'department'):
            return obj.department in managed_depts
            
        # For Faculty models, check their department
        if hasattr(obj, 'faculty') and obj.faculty and hasattr(obj.faculty, 'department'):
            return obj.faculty.department in managed_depts

        # For Publications/Patents, check if ANY internal author/inventor belongs to the managed departments
        if hasattr(obj, 'internal_authors'):
            for author in obj.internal_authors.all():
                if author.department in managed_depts:
                    return True
            return False

        if hasattr(obj, 'internal_inventors'):
            for inventor in obj.internal_inventors.all():
                if inventor.department in managed_depts:
                    return True
            return False

        return False
