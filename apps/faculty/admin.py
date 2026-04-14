from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Faculty
from apps.academics.models import School, Department
from apps.centres.models import Centre

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
    centre = fields.Field(
        column_name='centre',
        attribute='centre',
        widget=FuzzyForeignKeyWidget(Centre, 'name')
    )

    class Meta:
        model = Faculty
        # Set staff_no as primary identifier since employee_id is often None in user's sheet
        import_id_fields = ('staff_no',)
        fields = ( 'staff_no', 'name', 'dob', 'designation', 'faculty_type', 'campus', 'qualification', 'teaching_exp', 'research_exp', 'google_scholar_url', 'linkedin_url', 'website_url', 'date_of_joining', 'is_active', 'school', 'department', 'centre', 'insti_email', 'other_email', 'phone1', 'phone2', 'research_int', 'bio')
        export_order = fields
        skip_unchanged = True
        report_skipped = True



    def get_instance(self, instance_loader, row):
        """
        Prevent MultipleObjectsReturned when staff_no is None.
        If staff_no is missing, try to match by name or treat as a new object.
        """
        staff_no = row.get('staff_no')
        if staff_no is None:
            name = row.get('name')
            if name:
                matches = self._meta.model.objects.filter(name__iexact=str(name).strip())
                if matches.count() == 1:
                    return matches.first()
            return None # Force create (which may subsequently be skipped in skip_row)
            
        try:
            return super().get_instance(instance_loader, row)
        except self._meta.model.MultipleObjectsReturned:
            return self.get_queryset().filter(staff_no=staff_no).first()



    def skip_row(self, instance, original, row, import_validation_errors=None):
        """
        Skip the row only if all relationships (School, Dept, and Centre) are missing.
        """
        if not (instance.school or instance.department or instance.centre):
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

        # 6.5 Map Centre variations
        centre_keys = ['centre', 'center', 'centre name', 'center name', 'centres']
        for k in centre_keys:
            if k in row_copy and not row.get('centre'):
                row['centre'] = str(row_copy[k] or '').strip()
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

        # 8. New Profile Fields Mappings
        type_key = next((k for k in ['faculty_type', 'faculty type', 'type'] if k in row_copy), None)
        if type_key and row_copy[type_key]:
            val = str(row_copy[type_key]).strip().title() # Handle 'teaching', 'Teaching', 'TEACHING'
            if val == 'Non Teaching' or val == 'Non-teaching':
                val = 'Non-Teaching'
            row['faculty_type'] = val
            
        campus_key = next((k for k in ['campus', 'campus name'] if k in row_copy), None)
        if campus_key and row_copy[campus_key]:
            val = str(row_copy[campus_key]).strip().upper()
            if 'SATELLITE' in val or 'AMETHI' in val:
                row['campus'] = 'Satellite Campus Amethi'
            else:
                row['campus'] = 'BBAU Lucknow'

        qual_key = next((k for k in ['qualification', 'qualifications', 'degrees'] if k in row_copy), None)
        if qual_key and row_copy[qual_key]:
            row['qualification'] = str(row_copy[qual_key]).strip()
            
        teach_exp_key = next((k for k in ['teaching_exp', 'teaching exp', 'teaching experience'] if k in row_copy), None)
        if teach_exp_key and row_copy[teach_exp_key]:
            row['teaching_exp'] = str(row_copy[teach_exp_key]).strip()
            
        res_exp_key = next((k for k in ['research_exp', 'research exp', 'research experience'] if k in row_copy), None)
        if res_exp_key and row_copy[res_exp_key]:
            row['research_exp'] = str(row_copy[res_exp_key]).strip()

        # 9. Additional Profile Mappings
        gs_key = next((k for k in ['google_scholar', 'google scholar', 'google scholar url'] if k in row_copy), None)
        if gs_key and row_copy[gs_key]:
            row['google_scholar_url'] = str(row_copy[gs_key]).strip()

        li_key = next((k for k in ['linkedin', 'linkedin_url', 'linked in'] if k in row_copy), None)
        if li_key and row_copy[li_key]:
            row['linkedin_url'] = str(row_copy[li_key]).strip()

        web_key = next((k for k in ['website', 'website_url', 'personal website', 'url'] if k in row_copy), None)
        if web_key and row_copy[web_key]:
            row['website_url'] = str(row_copy[web_key]).strip()

        # Date of Joining Processing
        doj_key = next((k for k in ['date_of_joining', 'date of joining', 'joining date'] if k in row_copy), None)
        if doj_key:
            val = row_copy[doj_key]
            if val and isinstance(val, str):
                val = val.strip()
                try:
                    row['date_of_joining'] = datetime.strptime(val, '%d.%m.%Y').date()
                except (ValueError, TypeError):
                    try:
                        row['date_of_joining'] = datetime.strptime(val.replace('/', '.').replace('-', '.'), '%d.%m.%Y').date()
                    except (ValueError, TypeError):
                        pass

        # 10. Default roles to empty list
        if 'roles' not in row:
            row['roles'] = []

@admin.register(Faculty)
class FacultyAdmin(ImportExportModelAdmin):
    resource_classes = [FacultyResource]
    list_display = ('name', 'staff_no', 'faculty_type', 'designation', 'department', 'campus', 'is_active')
    list_filter = ('is_active', 'campus', 'faculty_type', 'department', 'school', 'designation')
    search_fields = ('name', 'staff_no', 'insti_email')
    prepopulated_fields = {'slug': ('name',)}