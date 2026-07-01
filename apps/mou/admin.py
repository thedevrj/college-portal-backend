from django.contrib import admin
from django.db import models
from django import forms
from .models import MOU


@admin.register(MOU)
class MOUAdmin(admin.ModelAdmin):
    list_display = ("organization_name", "date_of_signing", "valid_till", "is_deleted")
    list_filter = ("is_deleted",)
    search_fields = ("organization_name", "description")
    date_hierarchy = "date_of_signing"
    exclude = ("is_deleted", "deleted_at")

    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }
