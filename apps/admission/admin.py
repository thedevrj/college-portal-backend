from django.contrib import admin
from django.db import models
from django import forms
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin
from .models import (
    AdmissionSession,
    AdmissionStream,
    AdmissionProspectus,
    AdmissionNotice,
    RegistrationPortal,
    CounsellingPhase,
    MeritList,
    AdmissionCommitteeMember,
    AdmissionCommitteeMinutes,
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


@admin.register(AdmissionStream)
class AdmissionStreamAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = ("id", "name", "session", "order", "is_active")
    list_filter = (SoftDeleteListFilter, "session", "is_active")
    search_fields = ("id", "name")
    list_editable = ("order", "is_active")


@admin.register(AdmissionProspectus)
class AdmissionProspectusAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = ("id", "title", "session", "category", "upload_date")
    list_filter = (SoftDeleteListFilter, "session", "category")
    search_fields = ("id", "title")


@admin.register(AdmissionNotice)
class AdmissionNoticeAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = ("id", "title", "session", "category", "date_posted", "is_active")
    list_filter = (SoftDeleteListFilter, "session", "category", "is_active")
    search_fields = ("id", "title")


@admin.register(RegistrationPortal)
class RegistrationPortalAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = ("id", "portal_name", "session", "category", "registration_start", "registration_end", "is_active")
    list_filter = (SoftDeleteListFilter, "session", "category", "is_active")
    search_fields = ("id", "portal_name")
    formfield_overrides = {
        models.DateField: {
            "widget": forms.DateInput(attrs={"type": "date"})
        },
    }


@admin.register(CounsellingPhase)
class CounsellingPhaseAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = ("id", "phase_name", "stream", "order", "is_active")
    list_filter = (SoftDeleteListFilter, "stream", "is_active")
    search_fields = ("id", "phase_name")
    list_editable = ("order", "is_active")


@admin.register(MeritList)
class MeritListAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = ("id", "department", "phase", "upload_date")
    list_filter = (SoftDeleteListFilter, "phase__stream", "phase", "department")
    search_fields = ("id", "department__name")


@admin.register(AdmissionCommitteeMember)
class AdmissionCommitteeMemberAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = ("name", "designation", "email", "order")
    list_filter = (SoftDeleteListFilter,)
    search_fields = ("name", "designation", "email")
    list_editable = ("order",)


@admin.register(AdmissionCommitteeMinutes)
class AdmissionCommitteeMinutesAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = ("meeting_title", "date_of_meeting", "is_private")
    list_filter = (SoftDeleteListFilter, "is_private")
    search_fields = ("meeting_title",)
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }
