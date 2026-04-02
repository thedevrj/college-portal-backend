from django.contrib import admin
from .models import Faculty

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_id', 'designation', 'department', 'school')
    list_filter = ('department', 'school', 'designation')
    search_fields = ('name', 'employee_id', 'insti_email')
    prepopulated_fields = {'slug': ('name',)}