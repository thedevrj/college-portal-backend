from django.contrib import admin
from .models import School, Department


class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 1
    prepopulated_fields = {"slug": ("name",)}


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):

    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [DepartmentInline]

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = ("name", "school")
    list_filter = ("school",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}