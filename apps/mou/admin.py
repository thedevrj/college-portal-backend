from django.contrib import admin
from django.db import models
from django import forms
from .models import MOU
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin
from simple_history.admin import SimpleHistoryAdmin


@admin.register(MOU)
class MOUAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = (
        "organization_name",
        "date_of_signing",
        "valid_till",
        "is_archived",
        "archive_date",
    )
    list_filter = (
        SoftDeleteListFilter,
        "date_of_signing",
        "is_archived",
        "archive_date",
    )
    search_fields = ("organization_name", "Nature_of_organization")
    date_hierarchy = "date_of_signing"
    exclude = ("is_deleted", "deleted_at")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }

    # def get_queryset(self, request):
    #     from django.utils import timezone
    #     from django.db.models import Q
    #     qs = super().get_queryset(request)
    #     today = timezone.now().date()
    #     return qs.exclude(Q(is_archived=True) | Q(archive_date__lt=today))
