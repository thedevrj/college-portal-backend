from django.contrib import admin
from django.db import models
from django import forms
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from apps.accounts.mixins import PortalSecurityMixin
from apps.accounts.models import PortalRole
from apps.faculty.models import Faculty
from .models import (
    School,
    SchoolBoardCommittee,
    SchoolBoardCommitteeMember,
    SchoolBoardMOM,
    Department,
    Program,
    Course,
    CBCSCourse,
    DepartmentGallery,
    DepartmentGalleryEvent,
    Notice,
    Committee,
    CommitteeMember,
    MinutesOfTheMeeting,
    Timetable,
    StudyMaterial,
)


# --- Inlines ---
class SchoolBoardCommitteeMemberInline(admin.TabularInline):
    model = SchoolBoardCommitteeMember
    extra = 1
    exclude = ("is_deleted", "deleted_at")


class DepartmentGalleryInline(admin.TabularInline):
    model = DepartmentGallery
    extra = 1
    exclude = ("is_deleted", "deleted_at", "department")


class CBCSCourseInline(admin.TabularInline):
    model = CBCSCourse
    extra = 1
    exclude = ("is_deleted", "deleted_at")


class CourseInline(admin.TabularInline):
    model = Course
    extra = 1
    exclude = ("is_deleted", "deleted_at")


class CommitteeMemberInline(admin.TabularInline):
    model = CommitteeMember
    extra = 1
    exclude = ("is_deleted", "deleted_at")


# --- Admin Classes ---


@admin.register(School)
class SchoolAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("name", "slug", "dean")
    list_display_links = ("name", "dean")
    list_filter = (SoftDeleteListFilter, "leadership_title")

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        try:
            access = request.user.access_entries.filter(is_active=True).first()
            if access and access.role == PortalRole.DEAN:
                return True
        except:
            pass
        return super().has_module_permission(request)


@admin.register(SchoolBoardCommittee)
class SchoolBoardCommitteeAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("school", "name", "description")
    list_display_links = ("school", "name")
    list_filter = (SoftDeleteListFilter, "school")
    search_fields = ("school__name", "name")
    ordering = ["school", "name"]
    inlines = [SchoolBoardCommitteeMemberInline]


@admin.register(SchoolBoardMOM)
class SchoolBoardMOMAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("school", "meeting_title", "date_of_meeting", "minutes")
    list_display_links = ("school", "meeting_title")
    list_filter = (SoftDeleteListFilter, "school", "date_of_meeting")
    search_fields = ("school__name",)
    ordering = ["-date_of_meeting"]
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(Department)
class DepartmentAdmin(PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ("name", "campus", "school", "leadership_title", "hod")
    list_display_links = ("name", "campus")
    list_filter = (SoftDeleteListFilter, "campus", "school", "leadership_title")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("hod",)
    inlines = [CBCSCourseInline]


@admin.register(Program)
class ProgramAdmin(PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ("id", "name", "department", "centre", "level", "duration", "intake")
    list_display_links = ("name", "department", "centre")
    list_filter = (SoftDeleteListFilter, "level", "department", "centre")
    search_fields = ("id", "name")
    inlines = [CourseInline]


@admin.register(Notice)
class NoticeAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = (
        "title",
        "department",
        "centre",
        "category",
        "date_posted",
        "is_active",
    )
    list_display_links = ("title", "department", "centre")
    list_filter = (
        SoftDeleteListFilter,
        "category",
        "department",
        "centre",
        "date_posted",
        "is_active",
    )
    search_fields = ("title", "content")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(Committee)
class CommitteeAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("name", "department", "centre")
    list_display_links = ("name", "department", "centre")
    list_filter = (SoftDeleteListFilter, "department", "centre")
    search_fields = ("name",)
    inlines = [CommitteeMemberInline]


@admin.register(MinutesOfTheMeeting)
class MinutesAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("meeting_title", "committee", "date_of_meeting")
    list_display_links = ("meeting_title", "committee", "date_of_meeting")
    list_filter = (SoftDeleteListFilter, "committee", "date_of_meeting")
    search_fields = ("meeting_title", "date_of_meeting")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(CBCSCourse)
class CBCSCourseAdmin(PortalSecurityMixin, ImportExportModelAdmin):
    list_display = (
        "course_code",
        "course_title",
        "department",
        "centre",
        "semester",
        "credits",
    )
    list_filter = (SoftDeleteListFilter, "department", "centre", "semester")
    search_fields = ("course_code", "course_title")


@admin.register(Course)
class CourseAdmin(PortalSecurityMixin, ImportExportModelAdmin):
    list_display = (
        "id",
        "course_code",
        "course_title",
        "program",
        "semester",
        "credits",
    )
    list_filter = (SoftDeleteListFilter, "program", "semester")
    search_fields = ("id", "course_code", "course_title")


@admin.register(DepartmentGalleryEvent)
class DepartmentGalleryEventAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "department", "date_of_event")
    list_filter = (SoftDeleteListFilter, "department", "date_of_event")
    search_fields = ("title",)
    inlines = [DepartmentGalleryInline]
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, DepartmentGallery):
                instance.department = form.instance.department
            instance.save()
        formset.save_m2m()


@admin.register(Timetable)
class TimetableAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "department", "centre", "program", "uploaded_at")
    list_filter = (SoftDeleteListFilter, "department", "centre", "program")
    search_fields = ("title",)


@admin.register(StudyMaterial)
class StudyMaterialAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "department", "centre", "program", "uploaded_at")
    list_filter = (SoftDeleteListFilter, "department", "centre", "program")
    search_fields = ("title",)
