from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from apps.faculty.models import Faculty
from .models import (
    School,
    Department,
    Program,
    Course,
    CBCSCourse,
    DepartmentGallery,
    Notice,
    Committee,
    CommitteeMember,
    Timetable,
    StudyMaterial,
)


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
            qs = self.get_queryset(value, row, *args, **kwargs)
            if qs.exists():
                return qs.first()
            value = str(value).strip().lower()
            for obj in self.model.objects.all():
                if str(getattr(obj, self.field)).strip().lower() == value:
                    return obj
        return None


class SchoolResource(resources.ModelResource):
    dean = fields.Field(
        column_name="dean",
        attribute="dean",
        widget=FuzzyForeignKeyWidget(Faculty, "name"),
    )

    class Meta:
        model = School
        import_id_fields = ("name",)
        fields = (
            "id",
            "name",
            "dean",
            "dean_message",
            "about_school",
            "contact_email",
            "contact_phone",
        )
        skip_unchanged = True
        report_skipped = True


class DepartmentResource(resources.ModelResource):
    school = fields.Field(
        column_name="school",
        attribute="school",
        widget=FuzzyForeignKeyWidget(School, "name"),
    )
    hod = fields.Field(
        column_name="hod",
        attribute="hod",
        widget=FuzzyForeignKeyWidget(Faculty, "name"),
    )
    cbcs_courses = fields.Field(
        column_name="cbcs_courses", attribute="get_cbcs_summary", readonly=True
    )

    class Meta:
        model = Department
        import_id_fields = ("name",)
        fields = (
            "id",
            "name",
            "school",
            "hod",
            "about",
            "thrust_areas",
            "contact_email",
            "contact_phone",
            "cbcs_courses",
        )
        skip_unchanged = True
        report_skipped = True

    def get_cbcs_summary(self, obj):
        courses = obj.cbcs_courses.all()
        return ", ".join([f"{c.course_code}: {c.course_title}" for c in courses])


class ProgramResource(resources.ModelResource):
    department = fields.Field(
        column_name="department",
        attribute="department",
        widget=FuzzyForeignKeyWidget(Department, "name"),
    )

    class Meta:
        model = Program
        import_id_fields = ("name", "department")
        fields = (
            "id",
            "name",
            "department",
            "level",
            "duration",
            "intake",
            "fees",
            "eligibility",
            "admission_process",
            "program_outcomes",
        )
        skip_unchanged = True
        report_skipped = True


class CBCSCourseResource(resources.ModelResource):
    department = fields.Field(
        column_name="department",
        attribute="department",
        widget=FuzzyForeignKeyWidget(Department, "name"),
    )

    class Meta:
        model = CBCSCourse
        import_id_fields = ("course_code", "department")
        fields = (
            "id",
            "department",
            "semester",
            "course_code",
            "course_title",
            "credits",
        )
        skip_unchanged = True
        report_skipped = True


@admin.register(School)
class SchoolAdmin(ImportExportModelAdmin):
    resource_classes = [SchoolResource]
    list_display = ("name", "slug", "get_dean")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    autocomplete_fields = ("dean",)

    def get_dean(self, obj):
        return getattr(obj, "dean", None)

    get_dean.short_description = "Dean"


class DepartmentGalleryInline(admin.TabularInline):
    model = DepartmentGallery
    extra = 1


class CBCSCourseInline(admin.TabularInline):
    model = CBCSCourse
    extra = 1


@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    resource_classes = [DepartmentResource]
    list_display = ("name", "campus", "school", "hod")
    list_filter = ("campus", "school")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("hod",)
    inlines = [DepartmentGalleryInline, CBCSCourseInline]

    def get_hod(self, obj):
        return getattr(obj, "hod", None)

    get_hod.short_description = "HOD"


class CourseInline(admin.TabularInline):
    model = Course
    extra = 1


@admin.register(Program)
class ProgramAdmin(ImportExportModelAdmin):
    resource_classes = [ProgramResource]
    list_display = ("name", "department", "level", "duration", "intake")
    list_filter = ("level", "department")
    search_fields = ("name",)
    inlines = [CourseInline]

    class Media:
        js = ("js/admin_dynamic_fields.js?v=5",)


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "category", "date_posted", "is_active")
    list_filter = ("category", "department", "date_posted", "is_active")
    search_fields = ("title", "content")

    class Media:
        js = ("js/admin_dynamic_fields.js?v=5",)


class CommitteeMemberInline(admin.TabularInline):
    model = CommitteeMember
    extra = 1
    autocomplete_fields = ("faculty",)


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ("name", "department")
    list_filter = ("department",)
    inlines = [CommitteeMemberInline]
    search_fields = ("name",)

    class Media:
        js = ("js/admin_dynamic_fields.js?v=5",)


@admin.register(CBCSCourse)
class CBCSCourseAdmin(ImportExportModelAdmin):
    resource_classes = [CBCSCourseResource]
    list_display = ("course_code", "course_title", "department", "semester", "credits")
    list_filter = ("department", "semester")
    search_fields = ("course_code", "course_title")


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "program", "uploaded_at")
    list_filter = ("department", "program")
    search_fields = ("title",)


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "program", "uploaded_at")
    list_filter = ("department", "program")
    search_fields = ("title",)
