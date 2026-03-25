from django.contrib import admin
from .models import Faculty
from django import forms

class FacultyAdminForm(forms.ModelForm):
    roles = forms.MultipleChoiceField(
        choices=Faculty.Role.choices,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Faculty
        fields = '__all__'

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "staff_no",
        "employee_id",
        "school",
        "department"
    )

    list_filter = (
        "school",
        "department"
    )

    search_fields = (
        "name",
        "employee_id",
        "staff_no",
        "insti_email"
    )

    prepopulated_fields = {"slug": ("name",)}

    