from django.contrib import admin
from django.db import models
from django import forms
from .models import MOU


@admin.register(MOU)
class MOUAdmin(admin.ModelAdmin):
    list_display = (
        "organization_name",
        "date_of_signing",
        "valid_till",
    )
    search_fields = ("organization_name", "Nature_of_organization")
    date_hierarchy = "date_of_signing"
    exclude = ("is_deleted", "deleted_at")

    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }

    def get_queryset(self, request):
        """Exclude archived or expired MOUs from the main active admin view"""
        from django.utils import timezone
        from django.db.models import Q

        qs = super().get_queryset(request)
        today = timezone.now().date()
        return qs.exclude(Q(is_archived=True) | Q(archive_date__lt=today))
