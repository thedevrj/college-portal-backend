from django.contrib import admin
from .models import (
    School, Department, Program, Course, CBCSCourse, DepartmentGallery, Notice, Committee, 
    CommitteeMember, ResearchProject, ResearchScholar, 
    Timetable, StudyMaterial
)

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_dean')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def get_dean(self, obj):
        return getattr(obj, 'dean', None)
    get_dean.short_description = 'Dean'

class DepartmentGalleryInline(admin.TabularInline):
    model = DepartmentGallery
    extra = 1

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'get_hod', 'contact_email')
    list_filter = ('school',)
    search_fields = ('name', 'about')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DepartmentGalleryInline]

    def get_hod(self, obj):
        return getattr(obj, 'hod', None)
    get_hod.short_description = 'HOD'

class CourseInline(admin.TabularInline):
    model = Course
    extra = 1

class CBCSCourseInline(admin.TabularInline):
    model = CBCSCourse
    extra = 1

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'level', 'duration', 'intake')
    list_filter = ('level', 'department')
    search_fields = ('name',)
    inlines = [CourseInline, CBCSCourseInline]

    class Media:
        js = ('js/admin_dynamic_fields.js?v=4',)

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'date_posted', 'is_active')
    list_filter = ('department', 'date_posted', 'is_active')
    search_fields = ('title', 'content')

class CommitteeMemberInline(admin.TabularInline):
    model = CommitteeMember
    extra = 1

@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department',)
    inlines = [CommitteeMemberInline]
    search_fields = ('name',)

    class Media:
        js = ('js/admin_dynamic_fields.js?v=4',)

@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'principal_investigator', 'status')
    list_filter = ('status', 'department')
    search_fields = ('title', 'funding_agency')

@admin.register(ResearchScholar)
class ResearchScholarAdmin(admin.ModelAdmin):
    list_display = ('scholar_name', 'enrollment_no', 'department', 'supervisor')
    list_filter = ('department', 'registration_year')
    search_fields = ('scholar_name', 'enrollment_no')

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'program', 'uploaded_at')
    list_filter = ('department', 'program')
    search_fields = ('title',)

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'program', 'uploaded_at')
    list_filter = ('department', 'program')
    search_fields = ('title',)