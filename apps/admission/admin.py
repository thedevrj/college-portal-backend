from django.contrib import admin
from django.db import models
from django import forms
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin
from .models import (
    AdmissionSession,
    AdmissionUpdate,
    AdmissionBrochure,
    AdmissionSchedule,
    AdmissionContact,
    AdmissionLink,
    AdmissionMeritList,
)


@admin.register(AdmissionSession)
class AdmissionSessionAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = ("id", "session_name", "start_date", "end_date", "is_active")
    list_filter = (SoftDeleteListFilter, "is_active")
    search_fields = ("id", "session_name")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(AdmissionUpdate)
class AdmissionUpdateAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = (
        "id",
        "title",
        "session",
        "category",
        "date_posted",
        "is_active",
    )
    list_filter = (SoftDeleteListFilter, "session", "category", "is_active")
    search_fields = ("id", "title", "description")

    class Media:
        js = ("admin/js/admission_dynamic_programs.js",)


@admin.register(AdmissionBrochure)
class AdmissionBrochureAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = ("id", "title", "session", "category", "upload_date", "is_active")
    list_filter = (SoftDeleteListFilter, "session", "category", "is_active")
    search_fields = ("id", "title")

    class Media:
        js = ("admin/js/admission_dynamic_programs.js",)


@admin.register(AdmissionSchedule)
class AdmissionScheduleAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = (
        "id",
        "event_name",
        "session",
        "category",
        "event_date",
        "is_active",
    )
    list_filter = (SoftDeleteListFilter, "session", "category", "is_active")
    search_fields = ("id", "event_name")
    formfield_overrides = {
        models.DateTimeField: {
            "widget": forms.DateTimeInput(attrs={"type": "datetime-local"})
        },
    }

    class Media:
        js = ("admin/js/admission_dynamic_programs.js",)


@admin.register(AdmissionMeritList)
class AdmissionMeritListAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = (
        "id",
        "title",
        "session",
        "category",
        "date_posted",
        "is_active",
    )
    list_filter = (SoftDeleteListFilter, "session", "category", "is_active")
    search_fields = ("id", "title", "description")

    class Media:
        js = ("admin/js/admission_dynamic_programs.js",)


@admin.register(AdmissionContact)
class AdmissionContactAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = (
        "id",
        "name",
        "designation",
        "category",
        "session",
        "email",
        "phone_number",
    )
    list_filter = (SoftDeleteListFilter, "session", "category")
    search_fields = ("id", "name", "email", "phone_number")


@admin.register(AdmissionLink)
class AdmissionLinkAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = ("id", "title", "session", "category", "url", "is_active")
    list_filter = (SoftDeleteListFilter, "session", "category", "is_active")
    search_fields = ("id", "title", "url")
