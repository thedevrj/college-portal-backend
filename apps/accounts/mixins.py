from django.contrib import admin
from .models import PortalRole, EntityType
from django.apps import apps
from django.db import models


class PortalSecurityMixin:
    """
    Advanced Mixin to enforce row-level security and UI automation.
    """

    class Media:
        css = {"all": ("css/admin_tweaks.css",)}

    def _is_owner(self, user, obj):
        """
        Industry-standard helper to check if a user owns a specific record.
        """
        if not obj:
            return False

        # Check standard faculty-related fields
        owner_fields = ["faculty", "principal_investigator", "supervisor"]
        for field in owner_fields:
            if hasattr(obj, field):
                owner_obj = getattr(obj, field)
                # If the linked object has a .user (like Faculty), check it
                if owner_obj and hasattr(owner_obj, "user") and owner_obj.user == user:
                    return True

        # Special case: The Faculty profile itself
        if self.model.__name__ == "Faculty" and hasattr(obj, "user"):
            return obj.user == user

        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # --- Soft Delete Filtering ---
        # Only show active records by default, unless superuser is using a filter
        if hasattr(self.model, "is_deleted") and not request.user.is_superuser:
            qs = qs.filter(is_deleted=False)

        if request.user.is_superuser:
            return qs

        # Enforce row-level security even for autocomplete requests to filter dropdowns
        try:
            profile = getattr(request.user, "portal_profile", None)
            if profile and profile.is_rd_admin():
                return qs

            # --- Bypass Row-Level Security for Global Models ---
            global_models = [
                "BoardOfManagementMember",
                "BoardOfManagementMinutes",
                "AcademicCouncilMember",
                "AcademicCouncilMinutes",
                "PlanningBoardMember",
                "PlanningBoardMinutes",
                "FinanceCommitteeMember",
                "FinanceCommitteeMinutes",
            ]
            if self.model.__name__ in global_models:
                return qs

            active_access = request.user.access_entries.filter(is_active=True)
            if not active_access.exists():
                return qs.none()

            # Combine querysets from ALL active roles (Multi-role support)
            final_qs = qs.none()
            for access in active_access:
                role_qs = qs.none()  # Default to none for safety

                # 1. Role-based Logic (FACULTY)
                if access.role == PortalRole.FACULTY:
                    # Faculty should NOT see structural entities in the admin
                    structural_models = [
                        "School",
                        "Department",
                        "Centre",
                        "SchoolBoardCommittee",
                        "SchoolBoardMOM",
                    ]
                    if self.model.__name__ in structural_models:
                        role_qs = qs.none()
                    else:
                        role_qs = qs.all()
                        if hasattr(self.model, "faculty"):
                            role_qs = role_qs.filter(faculty__user=request.user)
                        elif hasattr(self.model, "principal_investigator"):
                            role_qs = role_qs.filter(
                                principal_investigator__user=request.user
                            )
                        elif hasattr(self.model, "supervisor"):
                            role_qs = role_qs.filter(supervisor__user=request.user)
                        elif self.model.__name__ == "Faculty":
                            role_qs = role_qs.filter(user=request.user)
                        else:
                            role_qs = role_qs.none()

                # 2. Entity-based Logic (DEPARTMENT / SCHOOL / CENTRE)
                elif access.entity_type == EntityType.DEPARTMENT:
                    role_qs = qs.all()
                    if self.model.__name__ == "Department":
                        role_qs = role_qs.filter(pk=access.object_id)
                    elif hasattr(self.model, "department"):
                        # Use _id for direct FK filtering to avoid extra joins/leaks
                        role_qs = role_qs.filter(department_id=access.object_id)
                    else:
                        role_qs = role_qs.none()

                elif access.entity_type == EntityType.SCHOOL:
                    role_qs = qs.all()
                    if self.model.__name__ == "School":
                        role_qs = role_qs.filter(pk=access.object_id)
                    elif self.model.__name__ == "Department":
                        role_qs = role_qs.filter(school_id=access.object_id)
                    elif self.model.__name__ in [
                        "SchoolBoardCommittee",
                        "SchoolBoardMOM",
                    ]:
                        role_qs = role_qs.filter(school_id=access.object_id)
                    elif hasattr(self.model, "department"):
                        role_qs = role_qs.filter(department__school_id=access.object_id)
                    elif hasattr(self.model, "school"):
                        role_qs = role_qs.filter(school_id=access.object_id)
                    else:
                        role_qs = role_qs.none()

                elif access.entity_type == EntityType.CENTRE:
                    role_qs = qs.all()
                    if self.model.__name__ == "Centre":
                        role_qs = role_qs.filter(pk=access.object_id)
                    elif hasattr(self.model, "centre"):
                        role_qs = role_qs.filter(centre_id=access.object_id)
                    else:
                        role_qs = role_qs.none()

                final_qs = final_qs | role_qs

            return final_qs.distinct()

        except Exception:
            pass

        return qs.none()

    def has_add_permission(self, request):
        """Disable 'Add' button for the Department model itself for HODs."""
        if request.user.is_superuser:
            return True
        if self.model.__name__ == "Department":
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        # 1. Django Superusers always have full access
        if request.user.is_superuser:
            return True

        if not obj:
            return super().has_change_permission(request, obj)

        # 2. R&D Cell Admins have full access to all research
        try:
            if request.user.portal_profile.is_rd_admin():
                rd_admin_models = [
                    "ResearchProject",
                    "ResearchScholar",
                    "Publication",
                    "Patent",
                    "Consultancy",
                    "ResearchArea",
                    "ResearchDevelopmentCellMember",
                ]
                if self.model.__name__ in rd_admin_models:
                    return True
        except:
            pass

        # 3. SPECIAL CASE: Faculty Profiles
        # HODs and Deans should NOT be able to edit other faculty members' profiles
        if self.model.__name__ == "Faculty":
            return self._is_owner(request.user, obj)

        if self._is_owner(request.user, obj):
            return True

        # Check ALL active roles for permission (Multi-role support)
        active_access = request.user.access_entries.filter(is_active=True)
        for access in active_access:
            # High-level management models (Programs, Notices, etc.)
            management_models = [
                "Program",
                "Notice",
                "Timetable",
                "StudyMaterial",
                "Cbcscourse",
                "Committee",
                "MinutesOfTheMeeting",
                "DepartmentGallery",
                "Department",
            ]

            if self.model.__name__ in management_models:
                if access.entity_type == EntityType.DEPARTMENT:
                    dept_name = (
                        access.entity.name if hasattr(access.entity, "name") else None
                    )
                    if self.model.__name__ == "Department":
                        if dept_name and obj.name == dept_name:
                            return True
                    elif hasattr(obj, "department") and obj.department:
                        if dept_name and obj.department.name == dept_name:
                            return True

                elif access.entity_type == EntityType.SCHOOL:
                    if self.model.__name__ == "Department":
                        if (
                            hasattr(obj, "school_id")
                            and obj.school_id == access.object_id
                        ):
                            return True
                    elif hasattr(obj, "department") and obj.department:
                        if obj.department.school_id == access.object_id:
                            return True

        # 5. Fallback to standard Django permissions if no owner is set yet
        # (This handles old records or records being assigned)
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if self.model.__name__ == "Department":
            return False

        # --- Bypass Row-Level Security for Global Models ---
        global_models = [
            "BoardOfManagementMember",
            "BoardOfManagementMinutes",
            "AcademicCouncilMember",
            "AcademicCouncilMinutes",
            "PlanningBoardMember",
            "PlanningBoardMinutes",
            "FinanceCommitteeMember",
            "FinanceCommitteeMinutes",
        ]
        if self.model.__name__ in global_models:
            return super().has_delete_permission(request, obj)

        # Faculty should always be able to delete their OWN records
        if self._is_owner(request.user, obj):
            return True

        # Deny delete permission for standard Staff users.
        # Only HODs, Deans, and RD_Admins should be able to soft-delete other people's records.
        # Delete the code below to give delete permission to all users.
        try:
            active_roles = request.user.access_entries.filter(
                is_active=True
            ).values_list("role", flat=True)
            has_high_level_role = any(
                role in ["HOD", "DEAN", "RD_ADMIN"] for role in active_roles
            )
            if not has_high_level_role:
                return False
        except Exception:
            pass

        # Follow the same ownership/admin logic as change permission for high-level roles
        if obj and self.has_change_permission(request, obj):
            return True

        return super().has_delete_permission(request, obj)

    def delete_model(self, request, obj):
        """
        Default to soft delete for everyone (including superusers) for safety.
        Superusers can still use the 'Permanent Delete' action in the list view.
        """
        if hasattr(obj, "soft_delete"):
            obj.soft_delete()
        else:
            super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Default to bulk soft delete for everyone."""
        if hasattr(self.model, "soft_delete"):
            from django.utils import timezone

            queryset.update(is_deleted=True, deleted_at=timezone.now())
        else:
            super().delete_queryset(request, queryset)

    @admin.action(description="Move selected to Trash")
    def move_to_trash(self, request, queryset):
        """Bulk soft delete."""
        from django.utils import timezone

        queryset.update(is_deleted=True, deleted_at=timezone.now())
        self.message_user(request, "Selected items moved to Trash.")

    @admin.action(description="Permanently Delete selected")
    def permanently_delete_items(self, request, queryset):
        """Bulk permanent delete."""
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request, f"Successfully purged {count} items from the database."
        )

    @admin.action(description="Restore selected items")
    def restore_items(self, request, queryset):
        """Restore soft-deleted items."""
        queryset.update(is_deleted=False, deleted_at=None)
        self.message_user(request, "Selected items have been restored.")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if hasattr(self.model, "soft_delete") and request.user.is_superuser:
            # Give superusers all the power
            actions["move_to_trash"] = self.get_action("move_to_trash")
            actions["restore_items"] = self.get_action("restore_items")
            actions["permanently_delete_items"] = self.get_action(
                "permanently_delete_items"
            )
        return actions

    def get_exclude(self, request, obj=None):
        """Hide system-managed soft delete fields from forms."""
        exclude = super().get_exclude(request, obj) or []
        exclude = list(exclude)

        if hasattr(self.model, "is_deleted"):
            if "is_deleted" not in exclude:
                exclude.append("is_deleted")
            if "deleted_at" not in exclude:
                exclude.append("deleted_at")

        return tuple(exclude)

    def get_form(self, request, obj=None, **kwargs):
        """Pre-fill and Lock the entity field for non-superusers."""
        form = super().get_form(request, obj, **kwargs)
        if request.user.is_superuser:
            return form

        try:
            # --- GLOBAL: Lock 'slug' for ALL non-superusers across all models ---
            if "slug" in form.base_fields:
                form.base_fields["slug"].disabled = True

            # --- Lock sensitive fields on the Faculty model for ALL non-superusers ---
            if self.model.__name__ == "Faculty":
                for field in [
                    "user",
                    "is_active",
                    "department",
                    "staff_no",
                    "insti_email",
                ]:
                    if field in form.base_fields:
                        form.base_fields[field].disabled = True

            active_access_list = request.user.access_entries.filter(is_active=True)
            dept_access = active_access_list.filter(entity_type=EntityType.DEPARTMENT)
            school_access = active_access_list.filter(entity_type=EntityType.SCHOOL)

            # --- Auto-fill and Lock for Faculty Role ---
            # (Only if they DON'T have a management role like HOD or Dean)
            if not dept_access.exists() and not school_access.exists():
                faculty_access = active_access_list.filter(
                    role=PortalRole.FACULTY
                ).first()
                if faculty_access:
                    FacultyModel = apps.get_model("faculty", "Faculty")
                    faculty_profile = FacultyModel.objects.filter(
                        user=request.user
                    ).first()
                    if faculty_profile:
                        # Auto-fill ownership fields
                        for field in [
                            "faculty",
                            "principal_investigator",
                            "supervisor",
                        ]:
                            if (
                                field in form.base_fields
                                and self.model.__name__ != "Faculty"
                            ):
                                form.base_fields[field].initial = faculty_profile
                                form.base_fields[field].disabled = True

                        if "department" in form.base_fields:
                            form.base_fields["department"].initial = (
                                faculty_profile.department
                            )
                            form.base_fields["department"].disabled = True

            # --- Auto-fill and Lock for Department Role (HODs/Coordinators) ---
            if dept_access.count() == 1:
                access = dept_access.first()
                if "department" in form.base_fields:
                    form.base_fields["department"].initial = access.entity
                    form.base_fields["department"].disabled = True
            elif dept_access.count() > 1:
                # Multiple departments - allow selection (dropdown will be filtered by formfield_for_foreignkey)
                if "department" in form.base_fields:
                    form.base_fields["department"].disabled = False

            # --- Auto-fill and Lock for School Role (Deans/Directors) ---
            if school_access.count() == 1:
                access = school_access.first()
                if "school" in form.base_fields:
                    form.base_fields["school"].initial = access.entity
                    form.base_fields["school"].disabled = True
            elif school_access.count() > 1:
                if "school" in form.base_fields:
                    form.base_fields["school"].disabled = False
        except Exception:
            pass
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter foreign key dropdowns and hide deleted items."""
        # --- GLOBAL: Always hide soft-deleted items from dropdowns ---
        if hasattr(db_field.remote_field.model, "is_deleted"):
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                is_deleted=False
            )

        if not request.user.is_superuser:
            try:
                active_access = request.user.access_entries.filter(is_active=True)
                # Combine filters for all roles using OR logic (Q objects)
                combined_q = models.Q()
                for access in active_access:
                    if access.entity_type == EntityType.DEPARTMENT:
                        dept_name = (
                            access.entity.name
                            if hasattr(access.entity, "name")
                            else None
                        )
                        if db_field.name == "department":
                            combined_q |= (
                                models.Q(name=dept_name)
                                if dept_name
                                else models.Q(pk=access.object_id)
                            )
                        elif db_field.name == "program":
                            combined_q |= (
                                models.Q(department__name=dept_name)
                                if dept_name
                                else models.Q(department=access.entity)
                            )
                        elif db_field.name in [
                            "faculty",
                            "principal_investigator",
                            "supervisor",
                            "hod",
                            "dean",
                            "incharge",
                        ]:
                            combined_q |= (
                                models.Q(department__name=dept_name)
                                if dept_name
                                else models.Q(department=access.entity)
                            )

                    elif access.entity_type == EntityType.SCHOOL:
                        if db_field.name == "school":
                            combined_q |= models.Q(pk=access.object_id)
                        elif db_field.name == "department":
                            combined_q |= models.Q(school_id=access.object_id)
                        elif db_field.name == "program":
                            combined_q |= models.Q(
                                department__school_id=access.object_id
                            )
                        elif db_field.name in [
                            "faculty",
                            "principal_investigator",
                            "supervisor",
                            "hod",
                            "dean",
                            "incharge",
                        ]:
                            combined_q |= models.Q(
                                department__school_id=access.object_id
                            )

                if combined_q.children:
                    current_qs = kwargs.get(
                        "queryset", db_field.remote_field.model.objects.all()
                    )
                    kwargs["queryset"] = current_qs.filter(combined_q).distinct()

            except Exception:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            try:
                access = request.user.access_entries.filter(is_active=True).first()
                if access:
                    if access.role == PortalRole.FACULTY:
                        Faculty = apps.get_model("faculty", "Faculty")
                        faculty_profile = Faculty.objects.filter(
                            user=request.user
                        ).first()
                        if faculty_profile:
                            if hasattr(obj, "department") and not obj.department:
                                obj.department = faculty_profile.department
                            if (
                                hasattr(obj, "principal_investigator")
                                and not obj.principal_investigator
                            ):
                                obj.principal_investigator = faculty_profile
                            if hasattr(obj, "supervisor") and not obj.supervisor:
                                obj.supervisor = faculty_profile
                            if (
                                hasattr(obj, "faculty")
                                and self.model.__name__ != "Faculty"
                                and not obj.faculty
                            ):
                                obj.faculty = faculty_profile

                    elif (
                        access.entity_type == EntityType.DEPARTMENT
                        and hasattr(obj, "department")
                        and self.model.__name__ != "Department"
                    ):
                        if not obj.department:
                            obj.department = access.entity
            except Exception:
                pass
        super().save_model(request, obj, form, change)
