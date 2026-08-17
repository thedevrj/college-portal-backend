from django.contrib import admin
from django.db import models
from django import forms
from import_export import resources
from import_export.widgets import ManyToManyWidget
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin
from .models import Staff


class StaffResource(resources.ModelResource):
    class Meta:
        model = Staff
        import_id_fields = ("staff_no",)
        skip_unchanged = True
        report_skipped = True
        fields = (
            "staff_no",
            "name",
            "designation",
            "department_section_cell",
            "roles",
            "dob",
            "insti_email",
            "other_email",
            "phone1",
            "phone2",
            "staff_type",
            "campus",
            "is_active",
        )
        export_order = fields

    def get_instance(self, instance_loader, row):
        staff_no = row.get("staff_no")
        if staff_no is None:
            name = row.get("name")
            if name:
                matches = self._meta.model.objects.filter(
                    name__iexact=str(name).strip()
                )
                if matches.count() == 1:
                    return matches.first()
            return None
        try:
            return super().get_instance(instance_loader, row)
        except self._meta.model.MultipleObjectsReturned:
            return self.get_queryset().filter(staff_no=staff_no).first()

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """
        Strip completely blank rows (ghost rows) from Excel files instantly, 
        which otherwise cause infinite loading.
        """
        def is_row_empty(row):
            for cell in row:
                if cell is not None and str(cell).strip() != "":
                    return False
            return True

        valid_rows = []
        for row in dataset:
            if not is_row_empty(row):
                valid_rows.append(row)
        
        dataset.dict = [dict(zip(dataset.headers, r)) for r in valid_rows]

    def skip_row(self, instance, original, row, import_validation_errors=None):
        if not row.get("staff_no") and not row.get("name"):
            return True
        return super().skip_row(instance, original, row, import_validation_errors)

    def import_obj(self, obj, row, dry_run, **kwargs):
        for field in self.get_import_fields():
            if field.column_name in row:
                if isinstance(field.widget, ManyToManyWidget):
                    continue
                val = row[field.column_name]
                if val is not None and str(val).strip() != "":
                    self.import_field(field, obj, row, **kwargs)

    def before_import_row(self, row, **kwargs):
        for key in list(row.keys()):
            val = row[key]
            if val is not None and str(val).lower().strip() == "none":
                row[key] = None

        row_copy = {str(k).lower().strip(): v for k, v in row.items()}

        name_keys = ["full name", "employee name", "staff name", "name", "staff_name"]
        for k in name_keys:
            if k in row_copy and not row.get("name"):
                row["name"] = row_copy[k]
                break

        staff_no_key = next(
            (
                k
                for k in ["staff_no", "staff no", "staff_number", "staffno", "id"]
                if k in row_copy
            ),
            None,
        )
        if staff_no_key:
            val = row_copy[staff_no_key]
            if val is not None:
                clean_val = "".join(filter(str.isdigit, str(val)))
                if clean_val:
                    row["staff_no"] = int(clean_val)
                else:
                    row["staff_no"] = None

        dept_keys = [
            "dept",
            "department",
            "department name",
            "section",
            "cell",
            "department_section_cell",
        ]
        for k in dept_keys:
            if k in row_copy and not row.get("department_section_cell"):
                row["department_section_cell"] = str(row_copy[k] or "").strip()
                break

        dob_key = next(
            (
                k
                for k in ["dob", "date of birth", "birth date", "birth_date"]
                if k in row_copy
            ),
            None,
        )
        if dob_key:
            from datetime import datetime
            val = row_copy[dob_key]
            if val and isinstance(val, str):
                val = val.strip()
                try:
                    row["dob"] = datetime.strptime(val, "%d.%m.%Y").date()
                except (ValueError, TypeError):
                    try:
                        row["dob"] = datetime.strptime(
                            val.replace("/", ".").replace("-", "."), "%d.%m.%Y"
                        ).date()
                    except (ValueError, TypeError):
                        pass


@admin.register(Staff)
class StaffAdmin(PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_class = StaffResource
    list_display = (
        "name",
        "staff_no",
        "designation",
        "department_section_cell",
        "staff_type",
        "is_active",
    )
    list_filter = (SoftDeleteListFilter, "staff_type", "campus", "is_active")
    search_fields = (
        "name",
        "staff_no",
        "designation",
        "department_section_cell",
        "roles",
    )
    prepopulated_fields = {"slug": ("name",)}
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }
