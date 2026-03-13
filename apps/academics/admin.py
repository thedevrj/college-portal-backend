from django.contrib import admin
from .models import School, Department


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name","dean_name"]
    search_fields = ["name"]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name","school"]
    search_fields = ["name"]