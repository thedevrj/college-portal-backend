from django.contrib import admin
from django.db import models
from django import forms
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export.admin import ImportExportModelAdmin
from apps.accounts.mixins import PortalSecurityMixin
from .models import Faculty, InvitedTalk, CourseDesign, Membership
from apps.academics.models import School, Department
from apps.centres.models import Centre


class FuzzyForeignKeyWidget(ForeignKeyWidget):
    """
    Custom widget that attempts to find a match by stripping whitespace
    and ignoring case sensitivity.
    """

    def get_queryset(self, value, row, *args, **kwargs):
        if value:
            value = str(value).strip()
            return self.model.objects.filter(**{f"{self.field}__iexact": value})
        return self.model.objects.none()

    def clean(self, value, row=None, *args, **kwargs):
        if value:
            # First try exact match or case-insensitive match via get_queryset
            qs = self.get_queryset(value, row, *args, **kwargs)
            if qs.exists():
                return qs.first()

            # If still not found, try stripping extra whitespace from database values too (more expensive)
            value = str(value).strip().lower()
            for obj in self.model.objects.all():
                if str(getattr(obj, self.field)).strip().lower() == value:
                    return obj
        return None


from datetime import datetime
from import_export import resources, fields


class FacultyResource(resources.ModelResource):
    # Use fuzzy matching for foreign keys
    school = fields.Field(
        column_name="school",
        attribute="school",
        widget=FuzzyForeignKeyWidget(School, "name"),
    )
    department = fields.Field(
        column_name="department",
        attribute="department",
        widget=FuzzyForeignKeyWidget(Department, "name"),
    )
    centre = fields.Field(
        column_name="centre",
        attribute="centre",
        widget=FuzzyForeignKeyWidget(Centre, "name"),
    )

    class Meta:
        model = Faculty
        # Set staff_no as primary identifier
        import_id_fields = ("staff_no",)
        fields = (
            "staff_no",
            "name",
            "dob",
            "designation",
            "campus",
            "qualification",
            "teaching_exp",
            "research_exp",
            "google_scholar_url",
            "scopus_url",
            "research_gate_url",
            "linkedin_url",
            "website_url",
            "orcid_id",
            "date_of_joining",
            "date_of_superannuation",
            "is_active",
            "school",
            "department",
            "centre",
            "insti_email",
            "other_email",
            "phone1",
            "phone2",
            "research_int",
            "bio",
        )
        export_order = fields
        skip_unchanged = True
        report_skipped = True

    def get_instance(self, instance_loader, row):
        """
        Prevent MultipleObjectsReturned when staff_no is None.
        If staff_no is missing, try to match by name or treat as a new object.
        """
        staff_no = row.get("staff_no")
        if staff_no is None:
            name = row.get("name")
            if name:
                matches = self._meta.model.objects.filter(
                    name__iexact=str(name).strip()
                )
                if matches.count() == 1:
                    return matches.first()
            return None  # Force create (which may subsequently be skipped in skip_row)

        try:
            return super().get_instance(instance_loader, row)
        except self._meta.model.MultipleObjectsReturned:
            return self.get_queryset().filter(staff_no=staff_no).first()

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """
        Skip the row only if all relationships (School, Dept, and Centre) are missing.
        """
        if not (instance.school or instance.department or instance.centre):
            return True
        return super().skip_row(instance, original, row, import_validation_errors)

    def import_obj(self, obj, row, dry_run, **kwargs):
        """
        Selective Update: Only update fields that have actual data in the row.
        If a cell in Excel is empty, keep the existing value in the database.
        """
        for field in self.get_import_fields():
            if field.column_name in row:
                if isinstance(field.widget, ManyToManyWidget):
                    continue
                val = row[field.column_name]
                # Check if the value is meaningful (not None and not empty string)
                if val is not None and str(val).strip() != "":
                    self.import_field(field, obj, row, **kwargs)

        # Note: If obj exists (update), slug is already set and models.py won't change it.
        # If obj is new, models.py will generate it in save().

    def before_import_row(self, row, **kwargs):
        """
        Handle 'somewhat different' column names and data cleanup.
        """
        # 1. Broad cleanup: Turn string "None" into real None
        for key in list(row.keys()):
            val = row[key]
            if val is not None and str(val).lower().strip() == "none":
                row[key] = None

        # Normalize keys to lowercase for easier matching
        row_copy = {str(k).lower().strip(): v for k, v in row.items()}

        # 2. Map Name variations
        name_keys = [
            "full name",
            "employee name",
            "faculty name",
            "name",
            "faculty_name",
        ]
        for k in name_keys:
            if k in row_copy and not row.get("name"):
                row["name"] = row_copy[k]
                break

        # 4. Handle staff_no cleanup
        staff_no_key = next(
            (
                k
                for k in ["staff_no", "staff no", "staff_number", "staffno"]
                if k in row_copy
            ),
            None,
        )
        if staff_no_key:
            val = row_copy[staff_no_key]
            if val is not None:
                clean_val = "".join(filter(str.isdigit, str(val)))
                if clean_val:
                    row["staff_no"] = int(clean_val)
                else:
                    row["staff_no"] = None

        # 5. Map Department variations
        dept_keys = ["dept", "department", "department name", "department_name"]
        for k in dept_keys:
            if k in row_copy and not row.get("department"):
                row["department"] = str(row_copy[k] or "").strip()
                break

        # 6. Map School variations
        school_keys = [
            "school",
            "school name",
            "faculty/school",
            "school of",
            "school_name",
        ]
        for k in school_keys:
            if k in row_copy and not row.get("school"):
                row["school"] = str(row_copy[k] or "").strip()
                break

        # 6.5 Map Centre variations
        centre_keys = ["centre", "center", "centre name", "center name", "centres"]
        for k in centre_keys:
            if k in row_copy and not row.get("centre"):
                row["centre"] = str(row_copy[k] or "").strip()
                break

        # 7. DOB Processing (Handle DD.MM.YYYY string from Excel)
        dob_key = next(
            (
                k
                for k in ["dob", "date of birth", "birth date", "birth_date"]
                if k in row_copy
            ),
            None,
        )
        if dob_key:
            val = row_copy[dob_key]
            if val and isinstance(val, str):
                val = val.strip()
                try:
                    # Attempt mapping from DD.MM.YYYY
                    row["dob"] = datetime.strptime(val, "%d.%m.%Y").date()
                except (ValueError, TypeError):
                    try:
                        # Fallback for DD-MM-YYYY or common variants
                        row["dob"] = datetime.strptime(
                            val.replace("/", ".").replace("-", "."), "%d.%m.%Y"
                        ).date()
                    except (ValueError, TypeError):
                        pass

        # 8. New Profile Fields Mappings

        campus_key = next((k for k in ["campus", "campus name"] if k in row_copy), None)
        if campus_key and row_copy[campus_key]:
            val = str(row_copy[campus_key]).strip().upper()
            if "SATELLITE" in val or "AMETHI" in val:
                row["campus"] = "Satellite Campus Amethi"
            else:
                row["campus"] = "BBAU Lucknow"

        qual_key = next(
            (
                k
                for k in ["qualification", "qualifications", "degrees"]
                if k in row_copy
            ),
            None,
        )
        if qual_key and row_copy[qual_key]:
            row["qualification"] = str(row_copy[qual_key]).strip()

        teach_exp_key = next(
            (
                k
                for k in ["teaching_exp", "teaching exp", "teaching experience"]
                if k in row_copy
            ),
            None,
        )
        if teach_exp_key and row_copy[teach_exp_key]:
            row["teaching_exp"] = str(row_copy[teach_exp_key]).strip()

        res_exp_key = next(
            (
                k
                for k in ["research_exp", "research exp", "research experience"]
                if k in row_copy
            ),
            None,
        )
        if res_exp_key and row_copy[res_exp_key]:
            row["research_exp"] = str(row_copy[res_exp_key]).strip()

        # 9. Additional Profile Mappings
        gs_key = next(
            (
                k
                for k in ["google_scholar", "google scholar", "google scholar url"]
                if k in row_copy
            ),
            None,
        )
        if gs_key and row_copy[gs_key]:
            row["google_scholar_url"] = str(row_copy[gs_key]).strip()

        li_key = next(
            (k for k in ["linkedin", "linkedin_url", "linked in"] if k in row_copy),
            None,
        )
        if li_key and row_copy[li_key]:
            row["linkedin_url"] = str(row_copy[li_key]).strip()

        scopus_key = next(
            (k for k in ["scopus_url", "scopus url", "scopus"] if k in row_copy),
            None,
        )
        if scopus_key and row_copy[scopus_key]:
            row["scopus_url"] = str(row_copy[scopus_key]).strip()

        rc_gate = next(
            (
                k
                for k in ["research_gate_url", "research gate url", "research gate"]
                if k in row_copy
            ),
            None,
        )
        if rc_gate and row_copy[rc_gate]:
            row["research_gate_url"] = str(row_copy[rc_gate]).strip()

        web_key = next(
            (
                k
                for k in ["website", "website_url", "personal website", "url"]
                if k in row_copy
            ),
            None,
        )
        if web_key and row_copy[web_key]:
            row["website_url"] = str(row_copy[web_key]).strip()

        # Date of Joining Processing
        doj_key = next(
            (
                k
                for k in ["date_of_joining", "date of joining", "joining date"]
                if k in row_copy
            ),
            None,
        )
        if doj_key:
            val = row_copy[doj_key]
            if val and isinstance(val, str):
                val = val.strip()
                try:
                    row["date_of_joining"] = datetime.strptime(val, "%d.%m.%Y").date()
                except (ValueError, TypeError):
                    try:
                        row["date_of_joining"] = datetime.strptime(
                            val.replace("/", ".").replace("-", "."), "%d.%m.%Y"
                        ).date()
                    except (ValueError, TypeError):
                        pass

        # 10. Default roles to empty list
        if "roles" not in row:
            row["roles"] = []


from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter


class InvitedTalkInline(admin.TabularInline):
    model = InvitedTalk
    extra = 1
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


class CourseDesignInline(admin.StackedInline):
    model = CourseDesign
    extra = 1


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(Faculty)
class FacultyAdmin(PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_classes = [FacultyResource]
    list_display = (
        "name",
        "staff_no",
        "designation",
        "department",
        "campus",
        "is_active",
    )
    list_filter = (
        SoftDeleteListFilter,
        "is_active",
        "campus",
        "department",
        "school",
        "designation",
    )
    search_fields = ("name", "staff_no", "insti_email", "orcid_id")
    prepopulated_fields = {"slug": ("name",)}
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }
    inlines = [InvitedTalkInline, CourseDesignInline, MembershipInline]
    actions = ["generate_portal_accounts", "sync_orcid_profiles"]

    @admin.action(description="Sync Selected Faculty Profiles with ORCID")
    def sync_orcid_profiles(self, request, queryset):

        from apps.faculty.orcid_sync import sync_faculty_orcid

        success_count = 0
        skipped_count = 0
        error_count = 0

        for faculty in queryset:
            if not faculty.orcid_id:
                skipped_count += 1
                continue

            result = sync_faculty_orcid(faculty)
            if result["success"]:
                success_count += 1
            else:
                error_count += 1

        msg = f"ORCID Sync Completed. Successfully synced: {success_count} profile(s)."
        if skipped_count:
            msg += f" Skipped {skipped_count} (no ORCID ID set)."
        if error_count:
            msg += f" Failed to sync {error_count} profile(s)."

        self.message_user(
            request,
            msg,
            level="SUCCESS" if error_count == 0 else "WARNING",
        )

    @admin.action(description="Generate Portal Login Accounts for Selected Faculty")
    def generate_portal_accounts(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(
                request,
                "Permission Denied: Only administrators can generate accounts.",
                level="ERROR",
            )
            return

        from django.contrib.auth.models import User
        from apps.accounts.models import UserProfile, PortalAccess, PortalRole

        created_count = 0
        skipped_count = 0

        for faculty in queryset:
            # Skip if they already have an account
            if faculty.user is not None:
                skipped_count += 1
                continue

            # Use staff_no for unique username (or fallback to id if staff_no is weirdly missing)
            username = (
                f"fac_{faculty.staff_no}" if faculty.staff_no else f"fac_{faculty.id}"
            )

            # Create the User account
            user, user_created = User.objects.get_or_create(username=username)
            if user_created:
                # Set default password
                user.set_password("Bbau@2026")
                if faculty.insti_email:
                    user.email = faculty.insti_email
                user.save()

            # Link the User to the Faculty model
            faculty.user = user
            faculty.save()

            # Setup the Portal Profile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.is_portal_user = True
            profile.force_password_change = True
            if faculty.staff_no:
                profile.employee_id = str(faculty.staff_no)
            profile.save()

            # Setup the RBAC Portal Access for Faculty role
            PortalAccess.objects.get_or_create(
                user=user, role=PortalRole.FACULTY, defaults={"is_active": True}
            )

            # Trigger permission sync
            profile.sync_permissions()
            created_count += 1

        self.message_user(
            request,
            f"Successfully created {created_count} new login accounts. {skipped_count} faculty already had accounts.",
            level="SUCCESS" if created_count > 0 else "WARNING",
        )

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        try:
            profile = request.user.portal_profile
            active_roles = request.user.access_entries.filter(
                is_active=True
            ).values_list("role", flat=True)
            # If they are ONLY an RD_ADMIN, hide the module entirely from the sidebar
            if profile.is_rd_admin() and len(active_roles) == 1:
                return False
        except Exception:
            pass
        return super().has_module_permission(request)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        try:
            profile = request.user.portal_profile
            active_roles = request.user.access_entries.filter(
                is_active=True
            ).values_list("role", flat=True)
            # RD_ADMIN should never be able to add a faculty profile
            if profile.is_rd_admin() and len(active_roles) == 1:
                return False
        except Exception:
            pass
        return super().has_add_permission(request)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if "generate_portal_accounts" in actions:
                del actions["generate_portal_accounts"]
        return actions


@admin.register(InvitedTalk)
class InvitedTalkAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "faculty", "event_name", "date", "role")
    list_filter = (SoftDeleteListFilter, "role", "date")
    search_fields = ("title", "event_name", "faculty__name", "venue")
    autocomplete_fields = ["faculty"]
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(CourseDesign)
class CourseDesignAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("course_name", "faculty", "course_level")
    list_filter = (SoftDeleteListFilter, "course_level")
    search_fields = ("course_name", "faculty__name")
    autocomplete_fields = ["faculty"]


@admin.register(Membership)
class MembershipAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("name", "faculty", "start_date", "end_date")
    list_filter = (SoftDeleteListFilter, "start_date", "end_date")
    search_fields = ("name", "faculty__name")
    autocomplete_fields = ["faculty"]
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }
