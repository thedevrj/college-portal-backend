from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    ResearchArea, ResearchFacility, ResearchProject, ResearchScholar,
    Publication, Patent, ResearchDevelopmentCellMember
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

@admin.register(ResearchArea)
class ResearchAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department',)
    search_fields = ('name', 'department__name')

@admin.register(ResearchFacility)
class ResearchFacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'incharge', 'location')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'location')

@admin.register(ResearchProject)
class ResearchProjectAdmin(ImportExportModelAdmin):
    resource_class = ResearchProjectResource
    list_display = ('title', 'principal_investigator', 'funding_agency', 'status', 'amount_sanctioned')
    list_filter = ('status', 'funding_agency', 'department')
    search_fields = ('title', 'principal_investigator__name', 'funding_agency')
    filter_horizontal = ('co_investigators',)

@admin.register(ResearchScholar)
class ResearchScholarAdmin(ImportExportModelAdmin):
    resource_class = ResearchScholarResource
    list_display = ('scholar_name', 'enrollment_no', 'supervisor', 'registration_year', 'status')
    list_filter = ('status', 'registration_year', 'department')
    search_fields = ('scholar_name', 'enrollment_no', 'supervisor__name')

@admin.register(Publication)
class PublicationAdmin(ImportExportModelAdmin):
    resource_class = PublicationResource
    list_display = ('title', 'faculty', 'publication_year', 'publication_type')
    list_filter = ('publication_type', 'publication_year', 'department')
    search_fields = ('title', 'faculty__name', 'journal_name')

@admin.register(Patent)
class PatentAdmin(ImportExportModelAdmin):
    resource_class = PatentResource
    list_display = ('title', 'faculty', 'year', 'status')
    list_filter = ('status', 'year', 'department')
    search_fields = ('title', 'faculty__name', 'patent_number')

@admin.register(ResearchDevelopmentCellMember)
class ResearchDevelopmentCellMemberAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'designation', 'order')
    list_editable = ('order',)
    ordering = ('order',)
