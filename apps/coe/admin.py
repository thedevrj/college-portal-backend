from django.contrib import admin
from django.forms import DateInput
from django.db import models
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin
from .models import (
    COENotice,
    PHDPreSubmissionSeminar,
    RDCUNotice,
    MPHILVivaVoceDate,
    PHDVivaVoceDate,
)


@admin.register(COENotice)
class COENoticeAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "date", "file")
    list_filter = (SoftDeleteListFilter, "is_archived", "date")
    search_fields = ("title",)
    date_hierarchy = "date"
    ordering = ("-date",)
    exclude = ("is_deleted", "deleted_at")
    formfield_overrides = {
        models.DateField: {"widget": DateInput(attrs={"type": "date"})},
    }


@admin.register(PHDVivaVoceDate)
class PHDVivaVoceDateAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "date", "file")
    list_filter = (SoftDeleteListFilter, "is_archived", "date")
    search_fields = ("title",)
    date_hierarchy = "date"
    ordering = ("-date",)
    exclude = ("is_deleted", "deleted_at")
    formfield_overrides = {
        models.DateField: {"widget": DateInput(attrs={"type": "date"})},
    }


@admin.register(MPHILVivaVoceDate)
class MPHILVivaVoceDateAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "date", "file")
    list_filter = (SoftDeleteListFilter, "is_archived", "date")
    search_fields = ("title",)
    date_hierarchy = "date"
    ordering = ("-date",)
    exclude = ("is_deleted", "deleted_at")
    formfield_overrides = {
        models.DateField: {"widget": DateInput(attrs={"type": "date"})},
    }


@admin.register(PHDPreSubmissionSeminar)
class PHDPreSubmissionSeminarAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "date", "file")
    list_filter = (SoftDeleteListFilter, "is_archived", "date")
    search_fields = ("title",)
    date_hierarchy = "date"
    ordering = ("-date",)
    exclude = ("is_deleted", "deleted_at")
    formfield_overrides = {
        models.DateField: {"widget": DateInput(attrs={"type": "date"})},
    }


@admin.register(RDCUNotice)
class RDCUNoticeAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "date", "file")
    list_filter = (SoftDeleteListFilter, "is_archived", "date")
    search_fields = ("title",)
    date_hierarchy = "date"
    ordering = ("-date",)
    exclude = ("is_deleted", "deleted_at")
    formfield_overrides = {
        models.DateField: {"widget": DateInput(attrs={"type": "date"})},
    }
