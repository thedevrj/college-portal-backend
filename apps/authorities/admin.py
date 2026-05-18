from django.contrib import admin
from django.db import models
from django import forms
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import Authority, AuthorityMember, AuthorityMinutes

# --- Resources for Import/Export ---


class AuthorityMemberResource(resources.ModelResource):
    authority = fields.Field(
        column_name="authority",
        attribute="authority",
        widget=ForeignKeyWidget(Authority, "name"),
    )

    class Meta:
        model = AuthorityMember
        fields = (
            "id",
            "authority",
            "provision",
            "name",
            "designation",
            "email",
            "phone_fax",
            "date_of_nomination",
            "date_of_expiry",
            "order",
        )
        export_order = fields

    def before_import_row(self, row, **kwargs):
        from .models import AuthorityType
        
        # Normalize keys to lowercase to find the authority column flexibly
        row_copy = {str(k).lower().strip(): v for k, v in row.items()}
        
        # 1. Clean string "None" into real None
        for key in list(row.keys()):
            val = row[key]
            if val is not None and str(val).lower().strip() == "none":
                row[key] = None

        # 2. Map human-readable Authority names to Database Choices
        auth_key = next((k for k in ["authority", "authority name", "authority type"] if k in row_copy), None)
        if auth_key and row_copy[auth_key]:
            val = str(row_copy[auth_key]).strip().lower()
            if "academic" in val:
                row["authority"] = AuthorityType.ACADEMIC_COUNCIL.value
            elif "management" in val or "bom" in val:
                row["authority"] = AuthorityType.BOARD_OF_MANAGEMENT.value
            elif "planning" in val:
                row["authority"] = AuthorityType.PLANNING_BOARD.value
            elif "finance" in val:
                row["authority"] = AuthorityType.FINANCE_COMMITTEE.value
        
        # 3. Clean up date fields if they are empty strings
        for date_field in ["date_of_nomination", "date_of_expiry"]:
            if date_field in row and (row[date_field] == "" or row[date_field] is None):
                row[date_field] = None

        return super().before_import_row(row, **kwargs)


class AuthorityMinutesResource(resources.ModelResource):
    authority = fields.Field(
        column_name="authority",
        attribute="authority",
        widget=ForeignKeyWidget(Authority, "name"),
    )

    class Meta:
        model = AuthorityMinutes
        fields = (
            "id",
            "authority",
            "meeting_title",
            "date_of_meeting",
            "file",
        )
        export_order = fields

    def before_import_row(self, row, **kwargs):
        from .models import AuthorityType
        
        # Normalize keys to lowercase to find the authority column flexibly
        row_copy = {str(k).lower().strip(): v for k, v in row.items()}
        
        # 1. Clean string "None" into real None
        for key in list(row.keys()):
            val = row[key]
            if val is not None and str(val).lower().strip() == "none":
                row[key] = None

        # 2. Map human-readable Authority names to Database Choices
        auth_key = next((k for k in ["authority", "authority name", "authority type"] if k in row_copy), None)
        if auth_key and row_copy[auth_key]:
            val = str(row_copy[auth_key]).strip().lower()
            if "academic" in val:
                row["authority"] = AuthorityType.ACADEMIC_COUNCIL.value
            elif "management" in val or "bom" in val:
                row["authority"] = AuthorityType.BOARD_OF_MANAGEMENT.value
            elif "planning" in val:
                row["authority"] = AuthorityType.PLANNING_BOARD.value
            elif "finance" in val:
                row["authority"] = AuthorityType.FINANCE_COMMITTEE.value
        
        # 3. Clean up date fields if they are empty strings
        if "date_of_meeting" in row and (row["date_of_meeting"] == "" or row["date_of_meeting"] is None):
            row["date_of_meeting"] = None

        return super().before_import_row(row, **kwargs)


# --- Admin Classes ---


class AuthorityMemberInline(admin.TabularInline):
    model = AuthorityMember
    extra = 1


class AuthorityMinutesInline(admin.TabularInline):
    model = AuthorityMinutes
    extra = 1


@admin.register(Authority)
class AuthorityAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ("name", "get_name_display")
    inlines = [AuthorityMemberInline, AuthorityMinutesInline]


@admin.register(AuthorityMember)
class AuthorityMemberAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_class = AuthorityMemberResource
    list_display = ("name", "authority", "designation", "order")
    list_filter = ("authority", "designation")
    search_fields = ("name", "email", "phone_fax")
    ordering = ("authority", "order")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(AuthorityMinutes)
class AuthorityMinutesAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_class = AuthorityMinutesResource
    list_display = ("meeting_title", "authority", "date_of_meeting")
    list_filter = ("authority", "date_of_meeting")
    search_fields = ("meeting_title",)
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }
