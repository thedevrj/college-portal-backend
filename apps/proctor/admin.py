from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin
from .models import ProctorialBoardMember, ProctorialBoardMinutes, ProctorialBoardNotice


@admin.register(ProctorialBoardMember)
class ProctorialBoardMemberAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = (
        "name",
        "designation",
        "in_the_capacity_of",
        "notification",
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


@admin.register(ProctorialBoardNotice)
class ProctorialBoardNoticeAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "date", "is_archived", "archive_date")
    list_filter = (SoftDeleteListFilter, "is_archived", "date")
    search_fields = ("title",)
    date_hierarchy = "date"
    ordering = ("-date",)
    exclude = ("is_deleted", "deleted_at")
