from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.models import ContentType
from .models import UserProfile, PortalAccess, PortalRole, EntityType
from apps.academics.models import Department
from django.contrib.admin.models import LogEntry


class PortalAccessForm(forms.ModelForm):
    entity_type = forms.ChoiceField(
        choices=[("", "---------")] + EntityType.choices,
        required=False,
        label="Entity type",
    )
    dynamic_entity = forms.IntegerField(
        required=False,
        label="Select Entity",
        widget=forms.Select(choices=[("", "---------")]),
        help_text="Choose the specific organization (Department, School, etc.)",
    )

    class Meta:
        model = PortalAccess
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing an existing record, populate the dropdown with the current entity so it displays correctly
        if (
            self.instance
            and self.instance.pk
            and self.instance.entity_type
            and self.instance.object_id
        ):
            try:
                # Get the name of the currently linked entity
                entity_name = str(self.instance.entity)
                self.fields["dynamic_entity"].widget.choices = [
                    (self.instance.object_id, entity_name)
                ]
                self.fields["dynamic_entity"].initial = self.instance.object_id
            except Exception:
                pass

        # If the form is submitted (POST data exists), we need to accept the dynamic value
        # by temporarily adding it to the choices so the widget renders correctly on validation error
        if self.is_bound:
            submitted_val = self.data.get(self.add_prefix("dynamic_entity"))
            if submitted_val:
                self.fields["dynamic_entity"].widget.choices = [
                    (submitted_val, f"Selected ID: {submitted_val}")
                ]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        entity_type = cleaned_data.get("entity_type")
        dynamic_entity_id = cleaned_data.get("dynamic_entity")

        # If role is FACULTY or RD_ADMIN, they don't need an entity!
        if role in ["FACULTY", "RD_ADMIN"]:
            return cleaned_data

        # For HOD, DEAN, etc. an entity is required
        if not entity_type or not dynamic_entity_id:
            self.add_error(
                "dynamic_entity",
                f"An Entity (Department/School) is required for the {role} role.",
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        entity_type = self.cleaned_data.get("entity_type")
        dynamic_entity_id = self.cleaned_data.get("dynamic_entity")

        if entity_type and dynamic_entity_id:
            # Dynamic Mapping
            ENTITY_MODEL_MAP = {
                "DEPARTMENT": ("academics", "Department"),
                "SCHOOL": ("academics", "School"),
            }
            if entity_type in ENTITY_MODEL_MAP:
                app_label, model_name = ENTITY_MODEL_MAP[entity_type]
                instance.content_type = ContentType.objects.get(
                    app_label=app_label, model=model_name.lower()
                )
                instance.object_id = dynamic_entity_id

        if commit:
            instance.save()
        return instance


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Portal Profile"
    fields = (
        "employee_id",
        "phone",
        "profile_photo",
        "is_portal_user",
        "force_password_change",
    )


class PortalAccessInline(admin.TabularInline):
    model = PortalAccess
    form = PortalAccessForm
    fk_name = "user"
    extra = 1
    fields = ("role", "entity_type", "dynamic_entity", "is_active")

    class Media:
        js = ("/static/js/portal_access_admin.js",)


from django.db.models import Q


class PortalRoleListFilter(admin.SimpleListFilter):
    title = "Portal Role"
    parameter_name = "portal_role"

    def lookups(self, request, model_admin):
        return PortalRole.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(access_entries__role=self.value()).distinct()
        return queryset


class PortalUserListFilter(admin.SimpleListFilter):
    title = "Portal User Status"
    parameter_name = "is_portal_user"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(portal_profile__is_portal_user=True)
        elif self.value() == "no":
            return queryset.filter(
                Q(portal_profile__is_portal_user=False) | Q(portal_profile__isnull=True)
            )
        return queryset


admin.site.unregister(User)


@admin.register(User)
class PortalUserAdmin(UserAdmin):
    inlines = [UserProfileInline, PortalAccessInline]
    list_display = (
        "username",
        "email",
        "get_full_name",
        "get_is_portal_user",
        "is_staff",
    )
    list_filter = UserAdmin.list_filter + (PortalRoleListFilter, PortalUserListFilter)

    def get_is_portal_user(self, obj):
        try:
            return obj.portal_profile.is_portal_user
        except:
            return False

    get_is_portal_user.short_description = "Portal User"
    get_is_portal_user.boolean = True


@admin.register(PortalAccess)
class PortalAccessAdmin(admin.ModelAdmin):
    form = PortalAccessForm
    list_display = ("user", "role", "entity_type", "entity", "is_active")
    list_filter = ("role", "entity_type", "is_active")
    exclude = ("content_type", "object_id")  # Hide the technical fields

    class Media:
        js = ("/static/js/portal_access_admin.js",)


from django.utils.html import format_html
from django.urls import reverse, NoReverseMatch
from .models import UserProfile, PortalAccess, PortalRole, EntityType, UserActivityLog


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    # This controls what you see in the list
    list_display = (
        "action_time",
        "user",
        "content_type",
        "object_link",
        "action_description",
        "change_message",
    )
    list_filter = ("action_flag", "content_type", "user")
    search_fields = ("object_repr", "change_message", "object_id")
    date_hierarchy = "action_time"
    readonly_fields = (
        "action_time",
        "user",
        "content_type",
        "object_id",
        "object_repr",
        "action_flag",
        "change_message",
    )

    # def get_readonly_fields(self, request, obj=None):
    #     if request.user.is_superuser:
    #         # action_time is non-editable by default, so it must stay in readonly_fields to be visible
    #         return ("action_time",)
    #     return self.readonly_fields

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def action_description(self, obj):
        if obj.action_flag == 1:
            return format_html('<span style="color: green;">Addition</span>')
        elif obj.action_flag == 2:
            return format_html('<span style="color: orange;">Change</span>')
        elif obj.action_flag == 3:
            return format_html('<span style="color: red;">Deletion</span>')
        return ""

    action_description.short_description = "Action"

    def object_link(self, obj):
        if obj.action_flag == 3:  # Deletion
            return obj.object_repr
        try:
            url = reverse(
                f"admin:{obj.content_type.app_label}_{obj.content_type.model}_change",
                args=[obj.object_id],
            )
            return format_html('<a href="{}">{}</a>', url, obj.object_repr)
        except (NoReverseMatch, AttributeError):
            return obj.object_repr

    object_link.short_description = "Object"


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "ip_address")
    list_filter = ("action", "timestamp", "user")
    search_fields = ("user__username", "ip_address", "user_agent")
    date_hierarchy = "timestamp"
    readonly_fields = ("user", "action", "ip_address", "user_agent", "timestamp")

    # def get_readonly_fields(self, request, obj=None):
    #     if request.user.is_superuser:
    #         # timestamp is auto_now_add, so it must stay readonly to be visible
    #         return ("timestamp",)
    #     return self.readonly_fields

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser
