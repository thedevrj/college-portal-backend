from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views import View
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomTokenObtainPairSerializer, ChangePasswordSerializer

from .models import PortalRole


class PortalLoginView(View):
    """
    Branded login page for all ERP portal users.
    URL: /portal/login/
    """

    template_name = "accounts/portal_login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return self._redirect_by_role(request, request.user)
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Superusers always have full access
            if user.is_superuser:
                login(request, user)
                return self._redirect_by_role(request, user)

            # For portal users, check the UserProfile flag
            try:
                is_portal = user.portal_profile.is_portal_user
            except Exception:
                is_portal = False

            if not is_portal:
                return render(
                    request,
                    self.template_name,
                    {
                        "error": "Your account does not have portal access. Contact your HOD or IT Admin."
                    },
                )
            login(request, user)

            # Force sync permissions on every login to avoid "stale" dashboards
            try:
                user.portal_profile.sync_permissions()
            except:
                pass

            return self._redirect_by_role(request, user)
        else:
            return render(
                request,
                self.template_name,
                {"error": "Invalid username or password. Please try again."},
            )

    def _redirect_by_role(self, request, user):
        """Redirect the user to the correct dashboard based on their role."""
        if user.is_superuser:
            return redirect("/admin/")

        access = user.access_entries.filter(is_active=True).first()
        if access is None:
            return render(
                request,
                self.template_name,
                {
                    "error": "No portal access role found for your account. Contact IT Admin."
                },
            )

        if access.role == PortalRole.RD_ADMIN:
            return redirect("/admin/research/")

        if access.role in [PortalRole.HOD, PortalRole.DEPT_STAFF]:
            return redirect("/admin/research/")

        return redirect("/admin/")


class PortalLogoutView(View):
    """
    Logs the user out and redirects to the login page.
    URL: /portal/logout/
    """

    def get(self, request):
        logout(request)
        return redirect("/portal/login/")

    def post(self, request):
        logout(request)
        return redirect("/portal/login/")


@login_required
def portal_profile(request):
    """
    Simple profile page for logged-in portal users.
    URL: /portal/profile/
    """
    return render(request, "accounts/portal_profile.html", {"user": request.user})


from django.http import JsonResponse
from django.apps import apps
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def get_entities_api(request):
    """
    API endpoint for the dynamic PortalAccess form in the Django Admin.
    URL: /portal/api/get-entities/
    Params: ?type=DEPARTMENT (or SCHOOL, CENTRE, etc.)
    """
    entity_type = request.GET.get("type", "").strip().upper()

    # Mapping of EntityType to the actual Model
    # As you add more entities in the future, just add them to this map!
    ENTITY_MODEL_MAP = {
        "DEPARTMENT": ("academics", "Department"),
        "SCHOOL": ("academics", "School"),
        "CENTRE": (
            "centres",
            "Centre",
        ),  # Uncomment or add when Centre model is created
    }

    if entity_type not in ENTITY_MODEL_MAP:
        return JsonResponse({"entities": []})

    app_label, model_name = ENTITY_MODEL_MAP[entity_type]

    try:
        ModelClass = apps.get_model(app_label, model_name)
        # Assuming all models have an 'id' and 'name' field
        entities = list(ModelClass.objects.all().values("id", "name"))
        return JsonResponse({"entities": entities})
    except LookupError:
        return JsonResponse({"entities": []})


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view that includes the 'force_password_change' flag.
    """
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordView(APIView):
    """
    API endpoint to change password and clear the 'force_password_change' flag.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Clear the force change flag
            try:
                profile = user.portal_profile
                profile.force_password_change = False
                profile.save()
            except Exception:
                pass
                
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
