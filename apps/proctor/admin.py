from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin
from django.db import models
from django import forms

from .models import ProctorialBoardMember, ProctorialBoardMinutes, ProctorialBoardNotice


@admin.register(ProctorialBoardMember)
class ProctorialBoardMemberAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = (
        "name",
        "designation",
        "in_the_capacity_of",
        "email_id",
        "order",
    )
    search_fields = (
        "name",
        "designation",
        "in_the_capacity_of",
        "others_in_the_capacity_of",
        "email_id",
    )
    list_filter = (SoftDeleteListFilter,)
    list_editable = ("order",)
    ordering = ("order", "id")
    exclude = ("is_deleted", "deleted_at")


@admin.register(ProctorialBoardMinutes)
class ProctorialBoardMinutesAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("meeting_title", "date_of_meeting", "is_archived", "archive_date")
    list_filter = (SoftDeleteListFilter, "is_archived", "date_of_meeting")
    search_fields = ("meeting_title",)
    date_hierarchy = "date_of_meeting"
    ordering = ("-date_of_meeting",)
    exclude = ("is_deleted", "deleted_at")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }

    def get_queryset(self, request):
        from django.utils import timezone
        from django.db.models import Q

        qs = super().get_queryset(request)
        today = timezone.now().date()
        return qs.exclude(Q(is_archived=True) | Q(archive_date__lt=today))


@admin.register(ProctorialBoardNotice)
class ProctorialBoardNoticeAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "date", "is_archived", "archive_date")
    list_filter = (SoftDeleteListFilter, "is_archived", "date")
    search_fields = ("title",)
    date_hierarchy = "date"
    ordering = ("-date",)
    exclude = ("is_deleted", "deleted_at")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }
