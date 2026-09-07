from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin

from .models import CommitteeMember, EmergencyContact, FAQ, Resource


@admin.register(Resource)
class ResourceAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "category", "published_on", "is_active")
    list_filter = (SoftDeleteListFilter, "category", "is_active")
    search_fields = ("title", "description")
    exclude = ("is_deleted", "deleted_at")


@admin.register(CommitteeMember)
class CommitteeMemberAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("faculty", "designation", "committee_type", "display_order")
    list_filter = (SoftDeleteListFilter, "committee_type")
    search_fields = ("faculty__name", "designation")
    list_editable = ("display_order",)
    exclude = ("is_deleted", "deleted_at")


@admin.register(FAQ)
class FAQAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("question", "display_order", "is_active")
    list_filter = (SoftDeleteListFilter, "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("question", "answer")
    exclude = ("is_deleted", "deleted_at")


@admin.register(EmergencyContact)
class EmergencyContactAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("name", "role", "phone", "available_hours", "display_order")
    list_filter = (SoftDeleteListFilter,)
    search_fields = ("name", "role", "phone")
    list_editable = ("display_order",)
    exclude = ("is_deleted", "deleted_at")
