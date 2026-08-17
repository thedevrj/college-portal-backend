from rest_framework.permissions import BasePermission


class IsVigilanceOfficer(BasePermission):

    message = "You do not have vigilance-officer access."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.has_perm("vigilance.manage_complaints"))
        )
