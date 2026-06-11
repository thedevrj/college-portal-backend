from django.contrib import admin
from django.db import models
from django import forms
from simple_history.admin import SimpleHistoryAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from apps.accounts.mixins import PortalSecurityMixin
from apps.accounts.filters import SoftDeleteListFilter
from .models import (
    ResearchArea,
    ResearchFacility,
    ResearchProject,
    ResearchScholar,
    Publication,
    Patent,
    ResearchDevelopmentCellMember,
    Consultancy,
)


# Resources for Import/Export
class ResearchProjectResource(resources.ModelResource):
    class Meta:
        model = ResearchProject


class ResearchScholarResource(resources.ModelResource):
    class Meta:
        model = ResearchScholar


class PublicationResource(resources.ModelResource):
    class Meta:
        model = Publication


class PatentResource(resources.ModelResource):
    class Meta:
        model = Patent


class ConsultancyResource(resources.ModelResource):
    class Meta:
        model = Consultancy


@admin.register(ResearchArea)
class ResearchAreaAdmin(PortalSecurityMixin, SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = (
        "available_research_areas_or_Specialization",
        "department",
        "campus",
    )
    list_display_links = ("available_research_areas_or_Specialization", "department")
    list_filter = (SoftDeleteListFilter, "campus", "department")
    search_fields = ("available_research_areas_or_Specialization", "department__name")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(Consultancy)
class ConsultancyAdmin(PortalSecurityMixin, SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ("faculty", "nature_of_consultancy", "campus")
    list_display_links = ("faculty", "nature_of_consultancy")
    list_filter = (SoftDeleteListFilter, "campus", "faculty", "start_date", "end_date")
    search_fields = ("faculty__name", "nature_of_consultancy")
    autocomplete_fields = ("faculty",)
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(ResearchFacility)
class ResearchFacilityAdmin(PortalSecurityMixin, SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ("name", "incharge", "campus")
    list_filter = (SoftDeleteListFilter, "campus")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    autocomplete_fields = ("incharge",)

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        try:
            return request.user.portal_profile.is_rd_admin()
        except:
            return False


@admin.register(ResearchProject)
class ResearchProjectAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    resource_class = ResearchProjectResource
    list_display = (
        "title",
        "principal_investigator",
        "funding_agency",
        "status",
        "campus",
    )
    list_display_links = ("title", "principal_investigator")
    list_filter = (
        SoftDeleteListFilter,
        "campus",
        "status",
        "funding_agency",
        "department",
    )
    search_fields = ("title", "principal_investigator__name", "funding_agency")
    autocomplete_fields = ("principal_investigator", "co_investigators")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(ResearchScholar)
class ResearchScholarAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    resource_class = ResearchScholarResource
    list_display = (
        "scholar_name",
        "enrollment_no",
        "subject",
        "supervisor",
        "status",
        "campus",
    )
    list_display_links = ("scholar_name", "enrollment_no")
    list_filter = (SoftDeleteListFilter, "campus", "status", "department", "gender")
    search_fields = ("scholar_name", "enrollment_no", "subject", "supervisor__name")
    autocomplete_fields = ("supervisor", "co_supervisor")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(Publication)
class PublicationAdmin(PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_class = PublicationResource
    list_display = ("title", "faculty", "publication_date", "campus")
    list_display_links = ("title", "faculty")
    list_filter = (
        SoftDeleteListFilter,
        "campus",
        "publication_type",
        "publication_date",
        "department",
    )
    search_fields = (
        "title",
        "faculty__name",
        "name_of_journal_or_conference_or_publisher",
    )
    autocomplete_fields = ("faculty",)
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(Patent)
class PatentAdmin(PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_class = PatentResource
    list_display = ("title", "faculty", "date_of_filing", "status")
    list_display_links = ("title", "faculty")
    list_filter = (SoftDeleteListFilter, "status", "date_of_filing", "department")
    search_fields = ("title", "faculty__name", "patent_number")
    autocomplete_fields = ("faculty",)
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(ResearchDevelopmentCellMember)
class ResearchDevelopmentCellMemberAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ("faculty", "designation", "order")
    list_editable = ("order",)
    ordering = ("order",)
    autocomplete_fields = ("faculty",)

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        try:
            return request.user.portal_profile.is_rd_admin()
        except:
            return False
