from django.contrib import admin, messages
from django.db import models
from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from simple_history.admin import SimpleHistoryAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export.admin import ImportExportModelAdmin
from datetime import datetime
from apps.faculty.models import Faculty
from apps.academics.models import Department
from apps.accounts.mixins import PortalSecurityMixin
from apps.accounts.filters import SoftDeleteListFilter
from .models import (
    ResearchArea,
    ResearchFacility,
    ResearchProject,
    ResearchScholar,
    Publication,
    PublicationAuthor,
    Patent,
    PatentAuthor,
    ResearchDevelopmentCellMember,
    Consultancy,
)


# Resources for Import/Export
class FuzzyForeignKeyWidget(ForeignKeyWidget):
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


class FuzzyManyToManyWidget(ManyToManyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return self.model.objects.none()

        if isinstance(value, (float, int)):
            value = str(int(value))

        ids = filter(None, [i.strip() for i in value.split(self.separator)])
        objects = []
        for id_val in ids:
            qs = self.model.objects.filter(**{f"{self.field}__iexact": id_val})
            if qs.exists():
                objects.append(qs.first())
                continue

            id_val_lower = id_val.lower()
            for obj in self.model.objects.all():
                if str(getattr(obj, self.field)).strip().lower() == id_val_lower:
                    objects.append(obj)
                    break
        return objects


class BaseResearchResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        for key in list(row.keys()):
            val = row[key]
            if val is not None and str(val).lower().strip() == "none":
                row[key] = None

        if "gender" in row and row["gender"]:
            g = str(row["gender"]).strip().lower()
            if g == "male":
                row["gender"] = "Male"
            elif g == "female":
                row["gender"] = "Female"
            elif g == "other":
                row["gender"] = "Other"

        if "category" in row and row["category"]:
            c = str(row["category"]).strip().upper()
            if c in ["GENERAL", "GEN", "UR"]:
                row["category"] = "General"
            elif c == "EWS":
                row["category"] = "EWS"
            elif c == "SC":
                row["category"] = "SC"
            elif c == "ST":
                row["category"] = "ST"
            elif c == "OBC":
                row["category"] = "OBC"
            elif c == "OTHER":
                row["category"] = "Other"

        if "status" in row and row["status"]:
            s = str(row["status"]).strip().lower()
            if s == "pursuing":
                row["status"] = "Pursuing"
            elif "thesis" in s:
                row["status"] = "Thesis Submitted"
            elif s == "awarded":
                row["status"] = "Awarded"
            elif s == "ongoing":
                row["status"] = "Ongoing"
            elif s == "completed":
                row["status"] = "Completed"
            elif s == "filed":
                row["status"] = "Filed"
            elif s == "published":
                row["status"] = "Published"
            elif s == "granted":
                row["status"] = "Granted"

        date_fields = [
            "start_date",
            "end_date",
            "date_of_birth",
            "date_of_registration",
            "thesis_submission_date",
            "viva_voce_date",
            "award_date",
            "publication_date",
            "date_of_filing",
        ]

        for date_field in date_fields:
            if date_field in row:
                val = row[date_field]
                if val and isinstance(val, str):
                    val = val.strip().replace("/", "-").replace(".", "-")
                    for fmt in [
                        "%Y-%m-%d",
                        "%d-%m-%Y",
                        "%d-%m-%y",
                        "%m-%d-%Y",
                        "%m-%d-%y",
                    ]:
                        try:
                            row[date_field] = datetime.strptime(val, fmt).date()
                            break
                        except (ValueError, TypeError):
                            continue

    def import_obj(self, obj, row, dry_run, **kwargs):
        for field in self.get_import_fields():
            if field.column_name in row:
                if isinstance(field.widget, ManyToManyWidget):
                    continue
                val = row[field.column_name]
                if val is not None and str(val).strip() != "":
                    self.import_field(field, obj, row, **kwargs)


class ResearchProjectResource(BaseResearchResource):
    department = fields.Field(
        column_name="department",
        attribute="department",
        widget=FuzzyForeignKeyWidget(Department, "name"),
    )
    principal_investigator = fields.Field(
        column_name="principal_investigator",
        attribute="principal_investigator",
        widget=FuzzyForeignKeyWidget(Faculty, "name"),
    )
    co_investigators = fields.Field(
        column_name="co_investigators",
        attribute="co_investigators",
        widget=FuzzyManyToManyWidget(Faculty, field="name"),
    )

    class Meta:
        model = ResearchProject
        exclude = ("id", "is_deleted", "deleted_at")
        import_id_fields = ("title",)
        export_order = (
            "title",
            "campus",
            "department",
            "principal_investigator",
            "co_investigators",
            "funding_agency",
            "others_funding_agency",
            "amount_sanctioned",
            "status",
            "start_date",
            "end_date",
            "description",
        )


class ResearchScholarResource(BaseResearchResource):
    department = fields.Field(
        column_name="department",
        attribute="department",
        widget=FuzzyForeignKeyWidget(Department, "name"),
    )
    supervisor = fields.Field(
        column_name="supervisor",
        attribute="supervisor",
        widget=FuzzyForeignKeyWidget(Faculty, "name"),
    )
    co_supervisor = fields.Field(
        column_name="co_supervisor",
        attribute="co_supervisor",
        widget=FuzzyManyToManyWidget(Faculty, field="name"),
    )

    class Meta:
        model = ResearchScholar
        exclude = ("id", "is_deleted", "deleted_at")
        import_id_fields = ("enrollment_no",)
        export_order = (
            "scholar_name",
            "enrollment_no",
            "campus",
            "department",
            "supervisor",
            "co_supervisor",
            "research_topic",
            "specialization",
            "status",
            "date_of_registration",
            "gender",
            "other_gender",
            "category",
            "other_category",
            "date_of_birth",
            "contact_no",
            "email",
            "address",
            "state",
            "thesis_submission_date",
            "viva_voce_date",
            "award_date",
        )

    def get_instance(self, instance_loader, row):
        enrollment_no = row.get("enrollment_no")
        if not enrollment_no:
            name = row.get("scholar_name")
            if name:
                matches = self._meta.model.objects.filter(
                    scholar_name__iexact=str(name).strip()
                )
                if matches.count() == 1:
                    return matches.first()
            return None
        try:
            return super().get_instance(instance_loader, row)
        except self._meta.model.MultipleObjectsReturned:
            return self.get_queryset().filter(enrollment_no=enrollment_no).first()


class PublicationResource(BaseResearchResource):
    internal_authors = fields.Field(
        column_name="internal_authors",
        attribute="internal_authors",
        widget=FuzzyManyToManyWidget(Faculty, field="name"),
    )

    class Meta:
        model = Publication
        exclude = ("id", "is_deleted", "deleted_at")
        import_id_fields = ("doi_url",)
        export_order = (
            "title",
            "campus",
            "publication_type",
            "other_publication_type",
            "name_of_journal_or_conference_or_publisher",
            "publication_date",
            "doi_url",
            "indexing",
            "others_indexing",
            "full_author_list",
        )

    def get_instance(self, instance_loader, row):
        doi_url = row.get("doi_url")
        if not doi_url:
            title = row.get("title")
            if title:
                matches = self._meta.model.objects.filter(
                    title__iexact=str(title).strip()
                )
                if matches.count() == 1:
                    return matches.first()
            return None
        try:
            return super().get_instance(instance_loader, row)
        except self._meta.model.MultipleObjectsReturned:
            return self.get_queryset().filter(doi_url=doi_url).first()


class PatentResource(BaseResearchResource):
    internal_inventors = fields.Field(
        column_name="internal_inventors",
        attribute="internal_inventors",
        widget=FuzzyManyToManyWidget(Faculty, field="name"),
    )

    class Meta:
        model = Patent
        exclude = ("id", "is_deleted", "deleted_at")
        import_id_fields = ("patent_number",)
        export_order = (
            "title",
            "patent_number",
            "status",
            "date_of_filing",
            "full_inventor_list",
            "description",
        )

    def get_instance(self, instance_loader, row):
        patent_number = row.get("patent_number")
        if not patent_number:
            title = row.get("title")
            if title:
                matches = self._meta.model.objects.filter(
                    title__iexact=str(title).strip()
                )
                if matches.count() == 1:
                    return matches.first()
            return None
        try:
            return super().get_instance(instance_loader, row)
        except self._meta.model.MultipleObjectsReturned:
            return self.get_queryset().filter(patent_number=patent_number).first()


class ConsultancyResource(BaseResearchResource):
    department = fields.Field(
        column_name="department",
        attribute="department",
        widget=FuzzyForeignKeyWidget(Department, "name"),
    )
    faculty = fields.Field(
        column_name="faculty",
        attribute="faculty",
        widget=FuzzyForeignKeyWidget(Faculty, "name"),
    )

    class Meta:
        model = Consultancy
        exclude = ("id", "is_deleted", "deleted_at")
        import_id_fields = (
            "nature_of_consultancy",
        )  # used only as fallback; get_instance overrides the lookup
        export_order = (
            "nature_of_consultancy",
            "faculty",
            "department",
            "name_of_awarding_agency_organization",
            "amount",
            "start_date",
            "end_date",
            "campus",
        )

    def get_instance(self, instance_loader, row):
        """
        Match on the composite unique key (faculty + nature_of_consultancy +
        start_date + department) rather than the non-unique nature_of_consultancy alone.
        """
        nature = row.get("nature_of_consultancy", "")
        faculty_name = row.get("faculty", "")
        dept_name = row.get("department", "")
        start_date = row.get("start_date")

        faculty_obj = (
            Faculty.objects.filter(name__iexact=str(faculty_name).strip()).first()
            if faculty_name
            else None
        )
        dept_obj = (
            Department.objects.filter(name__iexact=str(dept_name).strip()).first()
            if dept_name
            else None
        )

        if nature and faculty_obj:
            qs = self._meta.model.objects.filter(
                nature_of_consultancy__iexact=str(nature).strip(),
                faculty=faculty_obj,
            )
            if dept_obj:
                qs = qs.filter(department=dept_obj)
            if start_date:
                qs = qs.filter(start_date=start_date)
            if qs.count() == 1:
                return qs.first()
        return None


@admin.register(ResearchArea)
class ResearchAreaAdmin(PortalSecurityMixin, SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = (
        "available_research_areas_or_Specialization",
        "department",
        "campus",
    )
    list_display_links = ("available_research_areas_or_Specialization", "department")
    list_filter = (SoftDeleteListFilter, "campus", "department")
    search_fields = ("available_research_areas_or_Specialization", "department__name")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(Consultancy)
class ConsultancyAdmin(PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_class = ConsultancyResource
    list_display = ("faculty", "nature_of_consultancy", "campus")
    list_display_links = ("faculty", "nature_of_consultancy")
    list_filter = (
        SoftDeleteListFilter,
        "campus",
        ("faculty", admin.RelatedOnlyFieldListFilter),
        "start_date",
        "end_date",
    )
    search_fields = ("faculty__name", "nature_of_consultancy")
    autocomplete_fields = ("faculty",)
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(ResearchFacility)
class ResearchFacilityAdmin(PortalSecurityMixin, SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ("name", "incharge", "campus")
    list_filter = (SoftDeleteListFilter, "campus")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    autocomplete_fields = ("incharge",)

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        try:
            return request.user.portal_profile.is_rd_admin()
        except AttributeError:
            return False


@admin.register(ResearchProject)
class ResearchProjectAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    resource_class = ResearchProjectResource
    list_display = (
        "title",
        "principal_investigator",
        "funding_agency",
        "status",
        "campus",
    )
    list_display_links = ("title", "principal_investigator")
    list_filter = (
        SoftDeleteListFilter,
        "campus",
        "status",
        "funding_agency",
        ("department", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("title", "principal_investigator__name", "funding_agency")
    autocomplete_fields = ("principal_investigator", "co_investigators")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


@admin.register(ResearchScholar)
class ResearchScholarAdmin(
    PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin
):
    resource_class = ResearchScholarResource
    list_display = (
        "scholar_name",
        "enrollment_no",
        "specialization",
        "supervisor",
        "status",
        "campus",
    )
    list_display_links = ("scholar_name", "enrollment_no")
    list_filter = (
        SoftDeleteListFilter,
        "campus",
        "status",
        ("department", admin.RelatedOnlyFieldListFilter),
        "gender",
    )
    search_fields = (
        "scholar_name",
        "enrollment_no",
        "specialization",
        "supervisor__name",
        "contact_no",
        "email",
    )
    autocomplete_fields = ("supervisor", "co_supervisor")
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }


class RequiredInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        # Note: If no inline rows are filled out by the user, save_related() in PublicationAdmin
        # and PatentAdmin will automatically link the logged-in faculty member as the author.


class PublicationAdminForm(forms.ModelForm):
    confirm_coauthor_claim = forms.BooleanField(
        required=False,
        label="Confirm Co-Authorship Claim",
        help_text="Check this box if you are a co-author of the existing publication with this title/DOI and wish to link yourself to it.",
        # Hidden by default; revealed by JS only when a duplicate is detected.
        widget=forms.CheckboxInput(attrs={"class": "claim-confirm-checkbox"}),
    )

    class Meta:
        model = Publication
        fields = "__all__"

    class Media:
        js = ("admin/js/claim_checkbox_toggle.js",)

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        doi_url = cleaned_data.get("doi_url")
        confirm_claim = cleaned_data.get("confirm_coauthor_claim", False)

        if not self.instance.pk and (title or doi_url):
            from .models import clean_title_string, title_fingerprint, DOI_RE

            existing_pub = None

            if doi_url:
                raw = doi_url.strip()
                match = DOI_RE.match(raw)
                if match:
                    formatted_doi = f"https://doi.org/{match.group(1)}"
                    existing_pub = Publication.objects.filter(
                        doi_url__iexact=formatted_doi, is_deleted=False
                    ).first()

            if not existing_pub and title:
                # Use indexed title_fp for O(1) duplicate lookup.
                cleaned_t = clean_title_string(title)
                fp = title_fingerprint(cleaned_t)
                if fp:
                    existing_pub = Publication.objects.filter(
                        title_fp=fp, is_deleted=False
                    ).first()

            if existing_pub:
                if confirm_claim:
                    self.existing_pub = existing_pub
                    self.instance._existing_pub = existing_pub
                    if hasattr(self, "_errors"):
                        self._errors.pop("title", None)
                        self._errors.pop("doi_url", None)
                else:
                    err_msg = (
                        f"WARNING: A publication with this title/DOI already exists in the system ('{existing_pub.title}'). "
                        "If you are a co-author of this paper, please check the 'Confirm Co-Authorship Claim' checkbox below and click Save again to confirm adding yourself as a co-author."
                    )
                    self.add_error("confirm_coauthor_claim", err_msg)
                    self.add_error("title", err_msg)

        return cleaned_data


class PublicationAuthorInline(admin.TabularInline):
    model = Publication.internal_authors.through
    formset = RequiredInlineFormSet
    extra = 1
    verbose_name_plural = "Internal Faculty Authors (Add co-authors here)"
    autocomplete_fields = ["faculty"]

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        return True


@admin.register(Publication)
class PublicationAdmin(PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    form = PublicationAdminForm
    resource_class = PublicationResource
    list_display = ("title", "publication_date", "campus")
    list_display_links = ("title",)
    list_filter = (
        SoftDeleteListFilter,
        "campus",
        "publication_type",
        "indexing",
        "publication_date",
    )
    search_fields = (
        "title",
        "internal_authors__name",
        "name_of_journal_or_conference_or_publisher",
    )
    inlines = [PublicationAuthorInline]
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }

    actions = ["claim_as_coauthor"]

    @admin.action(description="Claim selected publication(s) as Co-Author")
    def claim_as_coauthor(self, request, queryset):
        faculty = (
            getattr(request.user, "faculty_profile", None)
            or Faculty.objects.filter(user=request.user).first()
        )
        if not faculty:
            self.message_user(
                request,
                "Only registered faculty accounts can claim research records.",
                level=messages.ERROR,
            )
            return

        claimed_count = 0
        already_claimed = 0

        for pub in queryset:
            author, created = PublicationAuthor.objects.get_or_create(
                publication=pub,
                faculty=faculty,
                defaults={
                    "author_order": pub.publicationauthor_set.count() + 1,
                    "author_role": "Co-Author",
                },
            )
            if created:
                claimed_count += 1
            else:
                already_claimed += 1

        if claimed_count > 0:
            self.message_user(
                request,
                f"Successfully claimed {claimed_count} publication(s) as Co-Author.",
                level=messages.SUCCESS,
            )
        if already_claimed > 0:
            self.message_user(
                request,
                f"{already_claimed} publication(s) were already claimed by you.",
                level=messages.INFO,
            )

    def save_model(self, request, obj, form, change):
        if hasattr(form, "existing_pub"):
            existing_pub = form.existing_pub
            faculty = (
                getattr(request.user, "faculty_profile", None)
                or Faculty.objects.filter(user=request.user).first()
            )
            if faculty:
                author, created = PublicationAuthor.objects.get_or_create(
                    publication=existing_pub,
                    faculty=faculty,
                    defaults={
                        "author_order": existing_pub.publicationauthor_set.count() + 1,
                        "author_role": "Co-Author",
                    },
                )
                if created:
                    messages.success(
                        request,
                        f"Found existing publication '{existing_pub.title}'. You have been successfully added as a co-author!",
                    )
                else:
                    messages.info(
                        request,
                        f"You are already linked as an author to the existing publication '{existing_pub.title}'.",
                    )
            obj.pk = existing_pub.pk
            return

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance

        # If no internal authors were added via inline, auto-link the creating faculty member
        if not PublicationAuthor.objects.filter(publication=obj).exists():
            faculty_profile = None
            if (
                hasattr(request.user, "faculty_profile")
                and request.user.faculty_profile
            ):
                faculty_profile = request.user.faculty_profile
            else:
                faculty_profile = Faculty.objects.filter(user=request.user).first()

            if faculty_profile:
                PublicationAuthor.objects.create(
                    publication=obj,
                    faculty=faculty_profile,
                    author_order=1,
                    author_role="First Author",
                )


class PatentAdminForm(forms.ModelForm):
    confirm_coinventor_claim = forms.BooleanField(
        required=False,
        label="Confirm Co-Inventor Claim",
        help_text="Check this box if you are a co-inventor of the existing patent with this title/number and wish to link yourself to it.",
        # Hidden by default; revealed by JS only when a duplicate is detected.
        widget=forms.CheckboxInput(attrs={"class": "claim-confirm-checkbox"}),
    )

    class Meta:
        model = Patent
        fields = "__all__"

    class Media:
        js = ("admin/js/claim_checkbox_toggle.js",)

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        confirm_claim = cleaned_data.get("confirm_coinventor_claim", False)

        if not self.instance.pk and title:
            from .models import clean_title_string, title_fingerprint

            existing_patent = None
            # Use indexed title_fp for O(1) duplicate lookup.
            cleaned_t = clean_title_string(title)
            fp = title_fingerprint(cleaned_t)
            if fp:
                existing_patent = Patent.objects.filter(
                    title_fp=fp, is_deleted=False
                ).first()

            if existing_patent:
                if confirm_claim:
                    self.existing_patent = existing_patent
                    self.instance._existing_patent = existing_patent
                    if hasattr(self, "_errors"):
                        self._errors.pop("title", None)
                else:
                    err_msg = (
                        f"WARNING: A patent with this title already exists in the system ('{existing_patent.title}'). "
                        "If you are a co-inventor of this patent, please check the 'Confirm Co-Inventor Claim' checkbox below and click Save again to confirm adding yourself as a co-inventor."
                    )
                    self.add_error("confirm_coinventor_claim", err_msg)
                    self.add_error("title", err_msg)

        return cleaned_data


class PatentAuthorInline(admin.TabularInline):
    model = Patent.internal_inventors.through
    formset = RequiredInlineFormSet
    extra = 1
    verbose_name = "Internal Faculty Inventor"
    verbose_name_plural = "Internal Faculty Inventors (Add co-inventors here)"
    autocomplete_fields = ["faculty"]

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        return True


@admin.register(Patent)
class PatentAdmin(PortalSecurityMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    form = PatentAdminForm
    resource_class = PatentResource
    list_display = ("title", "date_of_filing", "status")
    list_display_links = ("title",)
    list_filter = (SoftDeleteListFilter, "status", "date_of_filing")
    search_fields = ("title", "internal_inventors__name", "patent_number")
    inlines = [PatentAuthorInline]
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }

    actions = ["claim_as_coinventor"]

    @admin.action(description="Claim selected patent(s) as Co-Inventor")
    def claim_as_coinventor(self, request, queryset):
        faculty = (
            getattr(request.user, "faculty_profile", None)
            or Faculty.objects.filter(user=request.user).first()
        )
        if not faculty:
            self.message_user(
                request,
                "Only registered faculty accounts can claim research records.",
                level=messages.ERROR,
            )
            return

        claimed_count = 0
        already_claimed = 0

        for patent in queryset:
            author, created = PatentAuthor.objects.get_or_create(
                patent=patent,
                faculty=faculty,
                defaults={
                    "author_order": patent.patentauthor_set.count() + 1,
                    "author_role": "Co-Inventor",
                },
            )
            if created:
                claimed_count += 1
            else:
                already_claimed += 1

        if claimed_count > 0:
            self.message_user(
                request,
                f"Successfully claimed {claimed_count} patent(s) as Co-Inventor.",
                level=messages.SUCCESS,
            )
        if already_claimed > 0:
            self.message_user(
                request,
                f"{already_claimed} patent(s) were already claimed by you.",
                level=messages.INFO,
            )

    def save_model(self, request, obj, form, change):
        if hasattr(form, "existing_patent"):
            existing_patent = form.existing_patent
            faculty = (
                getattr(request.user, "faculty_profile", None)
                or Faculty.objects.filter(user=request.user).first()
            )
            if faculty:
                author, created = PatentAuthor.objects.get_or_create(
                    patent=existing_patent,
                    faculty=faculty,
                    defaults={
                        "author_order": existing_patent.patentauthor_set.count() + 1,
                        "author_role": "Co-Inventor",
                    },
                )
                if created:
                    messages.success(
                        request,
                        f"Found existing patent '{existing_patent.title}'. You have been successfully added as a co-inventor!",
                    )
                else:
                    messages.info(
                        request,
                        f"You are already linked as an inventor to the existing patent '{existing_patent.title}'.",
                    )
            obj.pk = existing_patent.pk
            return

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance

        # If no internal inventors were added via inline, auto-link the creating faculty member
        if not PatentAuthor.objects.filter(patent=obj).exists():
            faculty_profile = None
            if (
                hasattr(request.user, "faculty_profile")
                and request.user.faculty_profile
            ):
                faculty_profile = request.user.faculty_profile
            else:
                faculty_profile = Faculty.objects.filter(user=request.user).first()

            if faculty_profile:
                PatentAuthor.objects.create(
                    patent=obj,
                    faculty=faculty_profile,
                    author_order=1,
                    author_role="Inventor",
                )


@admin.register(ResearchDevelopmentCellMember)
class ResearchDevelopmentCellMemberAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ("faculty", "designation", "order")
    list_editable = ("order",)
    ordering = ("order",)
    autocomplete_fields = ("faculty",)
    exclude = ("is_deleted", "deleted_at")

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        try:
            return request.user.portal_profile.is_rd_admin()
        except AttributeError:
            return False
