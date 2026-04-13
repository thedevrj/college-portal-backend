from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Faculty
from apps.academics.models import School, Department

class FuzzyForeignKeyWidget(ForeignKeyWidget):
    """
    Custom widget that attempts to find a match by stripping whitespace 
    and ignoring case sensitivity.
    """
    def get_queryset(self, value, row, *args, **kwargs):
        if value:
            value = str(value).strip()
            return self.model.objects.filter(**{f"{self.field}__iexact": value})
        return self.model.objects.none()

    def clean(self, value, row=None, *args, **kwargs):
        if value:
            # First try exact match or case-insensitive match via get_queryset
            qs = self.get_queryset(value, row, *args, **kwargs)
            if qs.exists():
                return qs.first()
            
            # If still not found, try stripping extra whitespace from database values too (more expensive)
            value = str(value).strip().lower()
            for obj in self.model.objects.all():
                if str(getattr(obj, self.field)).strip().lower() == value:
                    return obj
        return None

from datetime import datetime
from import_export import resources, fields

class FacultyResource(resources.ModelResource):
    # Use fuzzy matching for foreign keys
    school = fields.Field(
        column_name='school',
        attribute='school',
        widget=FuzzyForeignKeyWidget(School, 'name')
    )
    department = fields.Field(
        column_name='department',
        attribute='department',
        widget=FuzzyForeignKeyWidget(Department, 'name')
    )

    class Meta:
        model = Faculty
        # Set staff_no as primary identifier since employee_id is often None in user's sheet
        import_id_fields = ('staff_no',)
        fields = ('employee_id', 'staff_no', 'name', 'dob', 'designation', 'school', 'department', 'insti_email', 'other_email', 'phone1', 'phone2', 'research_int', 'bio')
        export_order = fields
        skip_unchanged = True
        report_skipped = True

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """
        Skip the row if mandatory relationships (School/Dept) could not be mapped.
        """
        if not instance.school or not instance.department:
            return True
        return super().skip_row(instance, original, row, import_validation_errors)

    def import_obj(self, obj, row, dry_run, **kwargs):
        """
        Selective Update: Only update fields that have actual data in the row.
        If a cell in Excel is empty, keep the existing value in the database.
        """
        for field in self.get_import_fields():
            # If the field is in the row and has a value
            if field.column_name in row:
                val = row[field.column_name]
                # Check if the value is meaningful (not None and not empty string)
                if val is not None and str(val).strip() != '':
                    self.import_field(field, obj, row, **kwargs)
        
        # Note: If obj exists (update), slug is already set and models.py won't change it.
        # If obj is new, models.py will generate it in save().

    def before_import_row(self, row, **kwargs):
        """
        Handle 'somewhat different' column names and data cleanup.
        """
        # 1. Broad cleanup: Turn string "None" into real None
        for key in list(row.keys()):
            val = row[key]
            if val is not None and str(val).lower().strip() == 'none':
                row[key] = None

        # Normalize keys to lowercase for easier matching
        row_copy = {str(k).lower().strip(): v for k, v in row.items()}
        
        # 2. Map Name variations
        name_keys = ['full name', 'employee name', 'faculty name', 'name', 'faculty_name']
        for k in name_keys:
            if k in row_copy and not row.get('name'):
                row['name'] = row_copy[k]
                break

        # 3. Map Employee ID variations
        id_keys = ['emp id', 'employee id', 'staff id', 'id', 'employee_id']
        for k in id_keys:
            if k in row_copy and not row.get('employee_id'):
                row['employee_id'] = row_copy[k]
                break

        # 4. Handle staff_no cleanup
        staff_no_key = next((k for k in ['staff_no', 'staff no', 'staff_number', 'staffno'] if k in row_copy), None)
        if staff_no_key:
            val = row_copy[staff_no_key]
            if val is not None:
                clean_val = ''.join(filter(str.isdigit, str(val)))
                if clean_val:
                    row['staff_no'] = int(clean_val)
                else:
                    row['staff_no'] = None

        # 5. Map Department variations
        dept_keys = ['dept', 'department', 'department name', 'department_name']
        for k in dept_keys:
            if k in row_copy and not row.get('department'):
                row['department'] = str(row_copy[k] or '').strip()
                break

        # 6. Map School variations
        school_keys = ['school', 'school name', 'faculty/school', 'school of', 'school_name']
        for k in school_keys:
            if k in row_copy and not row.get('school'):
                row['school'] = str(row_copy[k] or '').strip()
                break

        # 7. DOB Processing (Handle DD.MM.YYYY string from Excel)
        dob_key = next((k for k in ['dob', 'date of birth', 'birth date', 'birth_date'] if k in row_copy), None)
        if dob_key:
            val = row_copy[dob_key]
            if val and isinstance(val, str):
                val = val.strip()
                try:
                    # Attempt mapping from DD.MM.YYYY
                    row['dob'] = datetime.strptime(val, '%d.%m.%Y').date()
                except (ValueError, TypeError):
                    try:
                        # Fallback for DD-MM-YYYY or common variants
                        row['dob'] = datetime.strptime(val.replace('/', '.').replace('-', '.'), '%d.%m.%Y').date()
                    except (ValueError, TypeError):
                        pass

        # 8. Default roles to empty list
        if 'roles' not in row:
            row['roles'] = []

@admin.register(Faculty)
class FacultyAdmin(ImportExportModelAdmin):
    resource_classes = [FacultyResource]
    list_display = ('name', 'staff_no', 'employee_id', 'dob', 'designation', 'department', 'school')
    list_filter = ('department', 'school', 'designation')
    search_fields = ('name', 'employee_id', 'staff_no', 'insti_email')
    prepopulated_fields = {'slug': ('name',)}