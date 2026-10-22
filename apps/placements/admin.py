from django.contrib import admin
from django.forms import DateInput
from django.db import models
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin
from .models import (
    PlacementNotice,
)

@admin.register(PlacementNotice)
class PlacementNoticeAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "date" , "file","is_archived", "archive_date")
    list_filter = (SoftDeleteListFilter, "is_archived", "date")
    search_fields = ("title",)
    date_hierarchy = "date"
    ordering = ("-date",)
    exclude = ("is_deleted", "deleted_at")
    formfield_overrides = {
        models.DateField: {"widget": DateInput(attrs={"type": "date"})},
    }
