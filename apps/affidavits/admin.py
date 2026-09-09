from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin

from .models import Affidavit, AffidavitFAQ, AffidavitGuidelines, SampleAffidavit

@admin.register(SampleAffidavit)
class SampleAffidavitAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "affidavit_category")
    list_filter = (SoftDeleteListFilter, "affidavit_category")
    search_fields = ("title", "affidavit_category")
    exclude = ("is_deleted", "deleted_at")

@admin.register(Affidavit)
class AffidavitAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = (
        "tracking_id",
        "student_name",
        "roll_number",
        "enrollment_number",
        "department",
        "status",
        "submitted_on",
    )
    list_filter = (SoftDeleteListFilter, "status", "department", "submitted_on")
    search_fields = (
        "tracking_id",
        "student_name",
        "roll_number",
        "enrollment_number",
        "department__name",
        "student_email",
        "student_phone",
        "parent_name",
    )
    readonly_fields = ("tracking_id", "submitted_on", "updated_on")
    list_editable = ("status",)
    date_hierarchy = "submitted_on"
    exclude = ("is_deleted", "deleted_at")


@admin.register(AffidavitFAQ)
class AffidavitFAQAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("question", "order")
    list_filter = (SoftDeleteListFilter,)
    search_fields = ("question", "answer")
    list_editable = ("order",)
    ordering = ("order", "id")
    exclude = ("is_deleted", "deleted_at")


@admin.register(AffidavitGuidelines)
class AffidavitGuidelinesAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title",)
    list_filter = (SoftDeleteListFilter,)
    search_fields = ("title", "content")
    exclude = ("is_deleted", "deleted_at")
