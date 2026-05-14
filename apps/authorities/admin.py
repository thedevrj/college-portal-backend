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


# --- Admin Classes ---


class AuthorityMemberInline(admin.TabularInline):
    model = AuthorityMember
    extra = 1


class AuthorityMinutesInline(admin.TabularInline):
    model = AuthorityMinutes
    extra = 1


@admin.register(Authority)
class AuthorityAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ("name", "get_name_display")
    inlines = [AuthorityMemberInline, AuthorityMinutesInline]


@admin.register(AuthorityMember)
class AuthorityMemberAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = AuthorityMemberResource
    list_display = ("name", "authority", "designation", "order")
    list_filter = ("authority", "designation")
    search_fields = ("name", "email", "phone_fax")
    ordering = ("authority", "order")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(AuthorityMinutes)
class AuthorityMinutesAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = AuthorityMinutesResource
    list_display = ("meeting_title", "authority", "date_of_meeting")
    list_filter = ("authority", "date_of_meeting")
    search_fields = ("meeting_title",)
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }
