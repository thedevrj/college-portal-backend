from rest_framework import permissions

class IsDepartmentAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users who are linked to a department
    to manage data for that department.
    """

    def has_permission(self, request, view):
        # Allow read-only for anyone if appropriate, 
        # or require authentication for all actions
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated and hasattr(request.user, 'managed_department')

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the object has a 'department' field and if it matches the user's department
        if hasattr(obj, 'department'):
            return obj.department == request.user.managed_department
        
        # Specific check for models where 'faculty' might be the link, 
        # but usually we'll check against department.
        return False
