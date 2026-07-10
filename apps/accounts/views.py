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

        # Strict validation on username to prevent injection attempts or overly long inputs
        if not username.isalnum() and "_" not in username and "@" not in username:
            return render(
                request,
                self.template_name,
                {"error": "Invalid username format."},
            )

        if len(username) > 150 or len(password) > 128:
            return render(
                request,
                self.template_name,
                {"error": "Input length exceeds allowed limits."},
            )

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
            if user.is_staff:
                return redirect("/admin/")
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

    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            # Clear the force change flag
            try:
                profile = user.portal_profile
                profile.force_password_change = False
                profile.save()
            except Exception:
                pass

            return Response(
                {"message": "Password updated successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.authentication import SessionAuthentication


class AdminDashboardStatsView(APIView):

    # admin dashboard stats

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Unauthorized"}, status=403)

        def get_count(app_label, model_name, filter_kwargs=None):
            try:
                model = apps.get_model(app_label, model_name)
                qs = model.objects.all()
                if filter_kwargs:
                    qs = qs.filter(**filter_kwargs)
                return qs.count()
            except LookupError:
                return 0

        # Academics
        total_departments = get_count("academics", "Department")
        total_programs = get_count("academics", "Program")

        # People
        total_faculty = get_count("faculty", "Faculty")
        total_staff = get_count("staff", "Staff")

        # Research
        total_publications = get_count("research", "Publication")
        total_projects = get_count("research", "ResearchProject")
        total_patents = get_count("research", "Patent")
        total_research_output = total_publications + total_projects + total_patents

        # Admissions
        total_merit_lists = get_count("admission", "MeritList")

        active_session_name = "None"
        try:
            SessionModel = apps.get_model("admission", "AdmissionSession")
            active_session = SessionModel.objects.filter(is_active=True).first()
            if active_session:
                active_session_name = active_session.session_name
        except LookupError:
            pass

        return Response(
            {
                "academics": {
                    "departments": total_departments,
                    "programs": total_programs,
                },
                "people": {"faculty": total_faculty, "staff": total_staff},
                "research": {"total_output": total_research_output},
                "admission": {
                    "active_session": active_session_name,
                    "merit_lists": total_merit_lists,
                },
            }
        )
