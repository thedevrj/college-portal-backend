from django.contrib import admin
from apps.accounts.mixins import PortalSecurityMixin
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from .models import Centre


@admin.register(Centre)
class CentreAdmin(PortalSecurityMixin, SimpleHistoryAdmin, admin.ModelAdmin):

    list_display = ("name", "slug", "school", "head", "head_title")
    list_filter = (SoftDeleteListFilter, "school", "head_title")
    search_fields = ("name", "slug", "head__name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("head",)

    class Media:
        js = ("/static/js/admin_dynamic_fields.js",)
