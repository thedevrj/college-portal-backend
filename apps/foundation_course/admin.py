from django.contrib import admin
from django import forms
from django.db import models
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from import_export.admin import ImportExportModelAdmin
from apps.accounts.mixins import PortalSecurityMixin
from .models import FoundationCourse, FoundationCourseMaterial


class FoundationCourseMaterialInline(admin.TabularInline):
    model = FoundationCourseMaterial
    extra = 1
    exclude = ("is_deleted", "deleted_at")


@admin.register(FoundationCourse)
class FoundationCourseAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    list_display = ("course_code", "course_title", "level", "semester", "credits")
    list_display_links = ("course_code", "course_title")
    list_filter = (SoftDeleteListFilter, "level", "semester")
    search_fields = ("course_code", "course_title")
    inlines = [FoundationCourseMaterialInline]


@admin.register(FoundationCourseMaterial)
class FoundationCourseMaterialAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "course", "material_type", "file", "link", "uploaded_at")
    list_filter = (
        SoftDeleteListFilter,
        "material_type",
        "course__level",
        "course__semester",
    )
    search_fields = ("title", "course__course_title", "course__course_code")
