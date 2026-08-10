from django.contrib import admin
from django.utils import timezone
from django.db.models import Q
from django.db import models
from django import forms
from .models import (
    ArchivedGlobalNotice,
    ArchivedMOU,
    ArchivedAdmissionNotice,
    ArchivedAdmissionCommitteeMinutes,
    ArchivedBoardOfManagementMinutes,
    ArchivedAcademicCouncilMinutes,
    ArchivedPlanningBoardMinutes,
    ArchivedFinanceCommitteeMinutes,
    ArchivedProctorialBoardNotice,
    ArchivedProctorialBoardMinutes,
    ArchivedCOENotice,
    ArchivedPHDPreSubmissionSeminar,
    ArchivedPHDVivaVoceDate,
    ArchivedMPHILVivaVoceDate,
    ArchivedRDCUNotice,
)


class BaseArchiveAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }

    def get_readonly_fields(self, request, obj=None):
        all_fields = [f.name for f in self.model._meta.fields]
        return [f for f in all_fields if f not in ("is_archived", "archive_date")]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        today = timezone.now().date()
        return qs.filter(Q(is_archived=True) | Q(archive_date__lt=today))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ArchivedGlobalNotice)
class ArchivedGlobalNoticeAdmin(BaseArchiveAdmin):
    list_display = (
        "title",
        "display_categories",
        "date_posted",
        "archive_date",
        "is_archived",
    )
    list_filter = ("categories", "date_posted", "is_archived")
    search_fields = ("title",)

    def display_categories(self, obj):
        return ", ".join(obj.categories) if obj.categories else "-"

    display_categories.short_description = "Categories"

    @admin.action(
        description="Restore selected items from Archive", permissions=["view"]
    )
    def restore_from_archive(self, request, queryset):
        updated = queryset.update(is_archived=False, archive_date=None)
        self.message_user(
            request, f"Successfully restored {updated} item(s) back to the Active list."
        )

    actions = [restore_from_archive]


@admin.register(ArchivedMOU)
class ArchivedMOUAdmin(BaseArchiveAdmin):
    list_display = (
        "organization_name",
        "date_of_signing",
        "valid_till",
        "archive_date",
        "is_archived",
    )
    list_filter = ("date_of_signing", "is_archived")
    search_fields = ("organization_name", "Nature_of_organization")

    @admin.action(
        description="Restore selected items from Archive", permissions=["view"]
    )
    def restore_from_archive(self, request, queryset):
        updated = queryset.update(is_archived=False, archive_date=None)
        self.message_user(
            request, f"Successfully restored {updated} item(s) back to the Active list."
        )

    actions = [restore_from_archive]


@admin.register(ArchivedAdmissionNotice)
class ArchivedAdmissionNoticeAdmin(BaseArchiveAdmin):
    list_display = (
        "title",
        "session",
        "category",
        "date_posted",
        "archive_date",
        "is_archived",
    )
    list_filter = ("session", "category", "date_posted", "is_archived")
    search_fields = ("title",)

    @admin.action(
        description="Restore selected items from Archive", permissions=["view"]
    )
    def restore_from_archive(self, request, queryset):
        updated = queryset.update(is_archived=False, archive_date=None)
        self.message_user(
            request, f"Successfully restored {updated} item(s) back to the Active list."
        )

    actions = [restore_from_archive]


class BaseMinutesArchiveAdmin(BaseArchiveAdmin):
    list_display = ("meeting_title", "date_of_meeting", "archive_date", "is_archived")
    list_filter = ("date_of_meeting", "is_archived")
    search_fields = ("meeting_title",)

    @admin.action(
        description="Restore selected items from Archive", permissions=["view"]
    )
    def restore_from_archive(self, request, queryset):
        updated = queryset.update(is_archived=False, archive_date=None)
        self.message_user(
            request, f"Successfully restored {updated} item(s) back to the Active list."
        )

    actions = [restore_from_archive]


@admin.register(ArchivedAdmissionCommitteeMinutes)
class ArchivedAdmissionCommitteeMinutesAdmin(BaseMinutesArchiveAdmin):
    pass


@admin.register(ArchivedBoardOfManagementMinutes)
class ArchivedBoardOfManagementMinutesAdmin(BaseMinutesArchiveAdmin):
    pass


@admin.register(ArchivedAcademicCouncilMinutes)
class ArchivedAcademicCouncilMinutesAdmin(BaseMinutesArchiveAdmin):
    pass


@admin.register(ArchivedPlanningBoardMinutes)
class ArchivedPlanningBoardMinutesAdmin(BaseMinutesArchiveAdmin):
    pass


@admin.register(ArchivedFinanceCommitteeMinutes)
class ArchivedFinanceCommitteeMinutesAdmin(BaseMinutesArchiveAdmin):
    pass


@admin.register(ArchivedProctorialBoardMinutes)
class ArchivedProctorialBoardMinutesAdmin(BaseMinutesArchiveAdmin):
    pass


class BaseCOEAdmin(BaseArchiveAdmin):
    list_display = ("title", "date", "archive_date", "is_archived")
    list_filter = ("date", "is_archived")
    search_fields = ("title",)

    @admin.action(
        description="Restore selected items from Archive", permissions=["view"]
    )
    def restore_from_archive(self, request, queryset):
        updated = queryset.update(is_archived=False, archive_date=None)
        self.message_user(
            request, f"Successfully restored {updated} item(s) back to the Active list."
        )

    actions = [restore_from_archive]


@admin.register(ArchivedProctorialBoardNotice)
class ArchivedProctorialBoardNoticeAdmin(BaseCOEAdmin):
    pass


@admin.register(ArchivedCOENotice)
class ArchivedCOENoticeAdmin(BaseCOEAdmin):
    pass


@admin.register(ArchivedPHDPreSubmissionSeminar)
class ArchivedPHDPreSubmissionSeminarAdmin(BaseCOEAdmin):
    pass


@admin.register(ArchivedPHDVivaVoceDate)
class ArchivedPHDVivaVoceDateAdmin(BaseCOEAdmin):
    pass


@admin.register(ArchivedMPHILVivaVoceDate)
class ArchivedMPHILVivaVoceDateAdmin(BaseCOEAdmin):
    pass


@admin.register(ArchivedRDCUNotice)
class ArchivedRDCUNoticeAdmin(BaseCOEAdmin):
    pass
