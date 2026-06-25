from django.contrib import admin
from django.db import models
from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from simple_history.admin import SimpleHistoryAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export.admin import ImportExportModelAdmin
from datetime import datetime
from apps.faculty.models import Faculty
from apps.academics.models import Department
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
class FuzzyForeignKeyWidget(ForeignKeyWidget):
    def get_queryset(self, value, row, *args, **kwargs):
        if value:
            value = str(value).strip()
            return self.model.objects.filter(**{f"{self.field}__iexact": value})
        return self.model.objects.none()

    def clean(self, value, row=None, *args, **kwargs):
        if value:
            qs = self.get_queryset(value, row, *args, **kwargs)
            if qs.exists():
                return qs.first()
            value = str(value).strip().lower()
            for obj in self.model.objects.all():
                if str(getattr(obj, self.field)).strip().lower() == value:
                    return obj
        return None

class FuzzyManyToManyWidget(ManyToManyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return self.model.objects.none()
        
        if isinstance(value, (float, int)):
            value = str(int(value))
        
        ids = filter(None, [i.strip() for i in value.split(self.separator)])
        objects = []
        for id_val in ids:
            qs = self.model.objects.filter(**{f"{self.field}__iexact": id_val})
            if qs.exists():
                objects.append(qs.first())
                continue
            
            id_val_lower = id_val.lower()
            for obj in self.model.objects.all():
                if str(getattr(obj, self.field)).strip().lower() == id_val_lower:
                    objects.append(obj)
                    break
        return objects

class BaseResearchResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        for key in list(row.keys()):
            val = row[key]
            if val is not None and str(val).lower().strip() == "none":
                row[key] = None

        if "gender" in row and row["gender"]:
            g = str(row["gender"]).strip().lower()
            if g == "male": row["gender"] = "Male"
            elif g == "female": row["gender"] = "Female"
            elif g == "other": row["gender"] = "Other"

        if "category" in row and row["category"]:
            c = str(row["category"]).strip().upper()
            if c in ["GENERAL", "GEN", "UR"]: row["category"] = "General"
            elif c == "EWS": row["category"] = "EWS"
            elif c == "SC": row["category"] = "SC"
            elif c == "ST": row["category"] = "ST"
            elif c == "OBC": row["category"] = "OBC"
            elif c == "OTHER": row["category"] = "Other"

        if "status" in row and row["status"]:
            s = str(row["status"]).strip().lower()
            if s == "pursuing": row["status"] = "Pursuing"
            elif "thesis" in s: row["status"] = "Thesis Submitted"
            elif s == "awarded": row["status"] = "Awarded"
            elif s == "ongoing": row["status"] = "Ongoing"
            elif s == "completed": row["status"] = "Completed"
            elif s == "filed": row["status"] = "Filed"
            elif s == "published": row["status"] = "Published"
            elif s == "granted": row["status"] = "Granted"

        date_fields = [
            "start_date", "end_date", "date_of_birth", "date_of_registration",
            "thesis_submission_date", "viva_voce_date", "award_date",
            "publication_date", "date_of_filing"
        ]
        
        for date_field in date_fields:
            if date_field in row:
                val = row[date_field]
                if val and isinstance(val, str):
                    val = val.strip().replace("/", "-").replace(".", "-")
                    for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d-%m-%y", "%m-%d-%Y", "%m-%d-%y"]:
                        try:
                            row[date_field] = datetime.strptime(val, fmt).date()
                            break
                        except (ValueError, TypeError):
                            continue

    def import_obj(self, obj, row, dry_run, **kwargs):
        for field in self.get_import_fields():
            if field.column_name in row:
                if isinstance(field.widget, ManyToManyWidget):
                    continue
                val = row[field.column_name]
                if val is not None and str(val).strip() != "":
                    self.import_field(field, obj, row, **kwargs)


class ResearchProjectResource(BaseResearchResource):
    department = fields.Field(column_name="department", attribute="department", widget=FuzzyForeignKeyWidget(Department, "name"))
    principal_investigator = fields.Field(column_name="principal_investigator", attribute="principal_investigator", widget=FuzzyForeignKeyWidget(Faculty, "name"))
    co_investigators = fields.Field(column_name="co_investigators", attribute="co_investigators", widget=FuzzyManyToManyWidget(Faculty, field="name"))

    class Meta:
        model = ResearchProject
        exclude = ('id', 'is_deleted', 'deleted_at')
        import_id_fields = ('title',)
        export_order = (
            "title",
            "campus",
            "department",
            "principal_investigator",
            "co_investigators",
            "funding_agency",
            "others_funding_agency",
            "amount_sanctioned",
            "status",
            "start_date",
            "end_date",
            "description",
        )


class ResearchScholarResource(BaseResearchResource):
    department = fields.Field(column_name="department", attribute="department", widget=FuzzyForeignKeyWidget(Department, "name"))
    supervisor = fields.Field(column_name="supervisor", attribute="supervisor", widget=FuzzyForeignKeyWidget(Faculty, "name"))
    co_supervisor = fields.Field(column_name="co_supervisor", attribute="co_supervisor", widget=FuzzyManyToManyWidget(Faculty, field="name"))

    class Meta:
        model = ResearchScholar
        exclude = ('id', 'is_deleted', 'deleted_at')
        import_id_fields = ('enrollment_no',)
        export_order = (
            "scholar_name",
            "enrollment_no",
            "campus",
            "department",
            "supervisor",
            "co_supervisor",
            "research_topic",
            "subject",
            "status",
            "date_of_registration",
            "gender",
            "other_gender",
            "category",
            "other_category",
            "date_of_birth",
            "contact_no",
            "email",
            "address",
            "state",
            "thesis_submission_date",
            "viva_voce_date",
            "award_date",
        )
        
    def get_instance(self, instance_loader, row):
        enrollment_no = row.get("enrollment_no")
        if not enrollment_no:
            name = row.get("scholar_name")
            if name:
                matches = self._meta.model.objects.filter(scholar_name__iexact=str(name).strip())
                if matches.count() == 1:
                    return matches.first()
            return None
        try:
            return super().get_instance(instance_loader, row)
        except self._meta.model.MultipleObjectsReturned:
            return self.get_queryset().filter(enrollment_no=enrollment_no).first()


class PublicationResource(BaseResearchResource):
    class Meta:
        model = Publication
        exclude = ('id', 'is_deleted', 'deleted_at')
        import_id_fields = ('doi_url',)
        export_order = (
            "title",
            "campus",
            "publication_type",
            "other_publication_type",
            "name_of_journal_or_conference_or_publisher",
            "publication_date",
            "doi_url",
            "indexing",
            "others_indexing",
            "full_author_list",
        )
        
    def get_instance(self, instance_loader, row):
        doi_url = row.get("doi_url")
        if not doi_url:
            title = row.get("title")
            if title:
                matches = self._meta.model.objects.filter(title__iexact=str(title).strip())
                if matches.count() == 1:
                    return matches.first()
            return None
        try:
            return super().get_instance(instance_loader, row)
        except self._meta.model.MultipleObjectsReturned:
            return self.get_queryset().filter(doi_url=doi_url).first()


class PatentResource(BaseResearchResource):
    class Meta:
        model = Patent
        exclude = ('id', 'is_deleted', 'deleted_at')
        import_id_fields = ('patent_number',)
        export_order = (
            "title",
            "patent_number",
            "status",
            "date_of_filing",
            "full_inventor_list",
            "description",
        )
        
    def get_instance(self, instance_loader, row):
        patent_number = row.get("patent_number")
        if not patent_number:
            title = row.get("title")
            if title:
                matches = self._meta.model.objects.filter(title__iexact=str(title).strip())
                if matches.count() == 1:
                    return matches.first()
            return None
        try:
            return super().get_instance(instance_loader, row)
        except self._meta.model.MultipleObjectsReturned:
            return self.get_queryset().filter(patent_number=patent_number).first()


class ConsultancyResource(BaseResearchResource):
    department = fields.Field(column_name="department", attribute="department", widget=FuzzyForeignKeyWidget(Department, "name"))
    faculty = fields.Field(column_name="faculty", attribute="faculty", widget=FuzzyForeignKeyWidget(Faculty, "name"))

    class Meta:
        model = Consultancy
        exclude = ('id', 'is_deleted', 'deleted_at')
        import_id_fields = ('nature_of_consultancy',)
        export_order = (
            "nature_of_consultancy",
            "faculty",
            "department",
            "name_of_awarding_agency_organization",
            "amount",
            "start_date",
            "end_date",
            "campus",
        )


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
class ConsultancyAdmin(PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_class = ConsultancyResource
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
    search_fields = ("scholar_name", "enrollment_no", "subject", "supervisor__name", "contact_no", "email")
    autocomplete_fields = ("supervisor", "co_supervisor")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


class RequiredInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        if not any(
            cleaned_data and not cleaned_data.get("DELETE", False)
            for cleaned_data in self.cleaned_data
        ):
            raise ValidationError(
                "You must add at least one author. Orphan records are not allowed."
            )


class PublicationAuthorInline(admin.TabularInline):
    model = Publication.internal_authors.through
    formset = RequiredInlineFormSet
    autocomplete_fields = ["faculty"]
    extra = 1


@admin.register(Publication)
class PublicationAdmin(PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_class = PublicationResource
    list_display = ("title", "publication_date", "campus")
    list_display_links = ("title",)
    list_filter = (
        SoftDeleteListFilter,
        "campus",
        "publication_type",
        "publication_date",
    )
    search_fields = (
        "title",
        "internal_authors__name",
        "name_of_journal_or_conference_or_publisher",
    )
    inlines = [PublicationAuthorInline]
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


class PatentAuthorInline(admin.TabularInline):
    model = Patent.internal_inventors.through
    formset = RequiredInlineFormSet
    autocomplete_fields = ["faculty"]
    extra = 1


@admin.register(Patent)
class PatentAdmin(PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_class = PatentResource
    list_display = ("title", "date_of_filing", "status")
    list_display_links = ("title",)
    list_filter = (SoftDeleteListFilter, "status", "date_of_filing")
    search_fields = ("title", "internal_inventors__name", "patent_number")
    inlines = [PatentAuthorInline]
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
