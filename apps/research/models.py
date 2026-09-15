from django.db import models
from apps.accounts.models import SoftDeleteModel
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, validate_email
import re
import unicodedata
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords
from django.utils import timezone


def clean_title_string(title: str) -> str:
    if not title:
        return ""
    text = unicodedata.normalize("NFKC", str(title))
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"[\s\u200b\xa0\ufeff]+", " ", text)
    text = text.strip()
    text = re.sub(r"[\s\.:;,-]+$", "", text)
    return text


def title_fingerprint(title: str) -> str:
    """Returns alphanumeric-only lowercase."""
    cleaned = clean_title_string(title)
    return re.sub(r"[^\w]", "", cleaned).lower()


# DOI Check
DOI_RE = re.compile(
    r"^(?:https?://(?:dx\.)?doi\.org/)?(10\.\d{4,9}/.+)$",
    re.IGNORECASE,
)


def validate_doi(value):
    """Reject values that don't match the standard DOI structure."""
    if value and not DOI_RE.match(value.strip()):
        raise ValidationError(
            "Enter a valid DOI. "
            "Accepted formats: \u201810.XXXX/suffix\u2019 "
            "or \u2018https://doi.org/10.XXXX/suffix\u2019."
        )


class ResearchArea(SoftDeleteModel):
    CAMPUS_CHOICES = [
        ("BBAU", "BBAU"),
        ("Satellite Campus Amethi", "Satellite Campus Amethi"),
    ]
    department = models.ForeignKey(
        "academics.Department", related_name="research_areas", on_delete=models.CASCADE
    )
    available_research_areas_or_Specialization = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)
    campus = models.CharField(max_length=50, choices=CAMPUS_CHOICES)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.available_research_areas_or_Specialization} ({self.department.name})"


class ResearchFacility(SoftDeleteModel):
    CAMPUS_CHOICES = [
        ("BBAU", "BBAU"),
        ("Satellite Campus Amethi", "Satellite Campus Amethi"),
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = RichTextField(blank=True, null=True)
    image = models.ImageField(upload_to="research/facilities/", null=True, blank=True)
    campus = models.CharField(max_length=50, choices=CAMPUS_CHOICES, default="BBAU")
    incharge = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_facilities",
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "Research Facilities"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ResearchProject(SoftDeleteModel):
    STATUS_CHOICES = [
        ("Ongoing", "Ongoing"),
        ("Completed", "Completed"),
    ]
    Funding_Agencies = [
        ("DST", "DST"),
        ("UGC", "UGC"),
        ("DRDO", "DRDO"),
        ("ICMR", "ICMR"),
        ("ISRO", "ISRO"),
        ("NHRC", "NHRC"),
        ("ICSSR", "ICSSR"),
        ("Others", "Others"),
    ]
    department = models.ForeignKey(
        "academics.Department",
        related_name="research_projects_new",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    campus = models.CharField(
        max_length=50,
        choices=[
            ("BBAU", "BBAU"),
            ("Satellite Campus Amethi", "Satellite Campus Amethi"),
        ],
    )
    principal_investigator = models.ForeignKey(
        "faculty.Faculty",
        related_name="pi_projects_new",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    co_investigators = models.ManyToManyField(
        "faculty.Faculty",
        related_name="co_pi_projects_new",
        blank=True,
        help_text="Select multiple time to add many co-investigator(s)",
    )
    funding_agency = models.CharField(max_length=20, choices=Funding_Agencies)
    others_funding_agency = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Please specify funding agency name if 'Others' is selected",
    )
    amount_sanctioned = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Ongoing")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = RichTextField(blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["title", "principal_investigator", "department"],
                condition=models.Q(is_deleted=False),
                name="unique_project_title_pi_dept",
            )
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        # Date order check
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                {"end_date": "End date cannot be before the start date."}
            )

        # Amount cannot be negative
        if self.amount_sanctioned is not None and self.amount_sanctioned < 0:
            raise ValidationError(
                {"amount_sanctioned": "Amount sanctioned cannot be negative."}
            )

        # Others funding agency required if funding_agency = Others
        if self.funding_agency == "Others" and not self.others_funding_agency:
            raise ValidationError(
                {
                    "others_funding_agency": "Please specify the funding agency name when 'Others' is selected."
                }
            )

        # Duplicate check
        qs = ResearchProject.objects.filter(
            title__iexact=self.title,
            principal_investigator=self.principal_investigator,
            department=self.department,
            is_deleted=False,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(
                "A project with the same Title, Principal Investigator, and Department already exists."
            )


class ResearchScholar(SoftDeleteModel):
    STATUS_CHOICES = [
        ("Pursuing", "Pursuing"),
        ("Thesis Submitted", "Thesis Submitted"),
        ("Awarded", "Awarded"),
    ]
    department = models.ForeignKey(
        "academics.Department", related_name="scholars_new", on_delete=models.CASCADE
    )
    scholar_name = models.CharField(max_length=255)
    campus = models.CharField(
        max_length=50,
        choices=[
            ("BBAU", "BBAU"),
            ("Satellite Campus Amethi", "Satellite Campus Amethi"),
        ],
    )
    enrollment_no = models.CharField(max_length=100, unique=True, blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
        null=True,
    )
    other_gender = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Please specify gender if 'Other' is selected",
    )
    category = models.CharField(
        max_length=10,
        choices=[
            ("General", "General"),
            ("EWS", "EWS"),
            ("SC", "SC"),
            ("ST", "ST"),
            ("OBC", "OBC"),
            ("Other", "Other"),
        ],
        null=True,
    )
    other_category = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(null=True,blank=True)
    contact_no = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\d{10}$", message="Phone number must be exactly 10 digits."
            )
        ],
    )
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    supervisor = models.ForeignKey(
        "faculty.Faculty",
        related_name="supervised_scholars_new",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    co_supervisor = models.ManyToManyField(
        "faculty.Faculty",
        related_name="co_supervised_scholars_new",
        blank=True,
        help_text="Select multiple time to add many co-supervisor(s)",
    )
    research_topic = models.CharField(
        max_length=500, null=True, blank=True, verbose_name="Research Topic /Title"
    )
    specialization = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Specialization"
    )
    date_of_registration = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pursuing")
    thesis_submission_date = models.DateField(null=True, blank=True)
    viva_voce_date = models.DateField(null=True, blank=True)
    award_date = models.DateField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-date_of_registration"]
        constraints = [
            models.UniqueConstraint(
                fields=["scholar_name", "department", "supervisor", "date_of_birth"],
                condition=models.Q(is_deleted=False),
                name="unique_scholar_dept_supervisor_dob",
            )
        ]

    def __str__(self):
        return self.scholar_name

    def clean(self):
        super().clean()
        # --- Conditional field validations ---
        if self.category == "Other" and not self.other_category:
            raise ValidationError(
                {"other_category": "This field is required when category is 'Other'."}
            )
        if self.gender == "Other" and not self.other_gender:
            raise ValidationError(
                {"other_gender": "This field is required when gender is 'Other'."}
            )

        # Date of birth cannot be in the future
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError(
                {"date_of_birth": "Date of birth cannot be in the future."}
            )

        # Date of registration must be after date of birth
        if (
            self.date_of_birth
            and self.date_of_registration
            and self.date_of_registration < self.date_of_birth
        ):
            raise ValidationError(
                {
                    "date_of_registration": "Date of registration cannot be before the scholar's date of birth."
                }
            )

        # Thesis submission must be after registration
        if (
            self.date_of_registration
            and self.thesis_submission_date
            and self.thesis_submission_date < self.date_of_registration
        ):
            raise ValidationError(
                {
                    "thesis_submission_date": "Thesis submission date cannot be before registration date."
                }
            )

        if( self.status == "Thesis Submitted" and not self.thesis_submission_date):
            raise ValidationError(
                {"thesis_submission_date": "Thesis submission date cannot be empty when status is 'Thesis Submitted'."}
            )

        if( self.status == "Award" and not self.award_date):
            raise ValidationError(
                {"award_date": "Award date cannot be empty when status is 'Award'."}
            )

        if self.contact_no:
            if not re.match(r"^\d{10}$", str(self.contact_no).strip()):
                raise ValidationError(
                    {"contact_no": "Phone number must be exactly 10 digits."}
                )

        if self.email:
            try:
                validate_email(self.email)
            except ValidationError:
                raise ValidationError({"email": "Please enter a valid email address."})

        # --- Duplicate entry check ---
        qs = ResearchScholar.objects.filter(
            scholar_name__iexact=self.scholar_name,
            department=self.department,
            supervisor=self.supervisor,
            date_of_birth=self.date_of_birth,
            is_deleted=False,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(
                "A scholar record with the same Name, Department and Supervisor "
                "already exists. Please verify before adding a new entry."
            )


class PublicationAuthor(models.Model):
    AUTHOR_ROLE_CHOICES = [
        ("Main Author", "Main Author"),
        ("Co-Author", "Co-Author"),
    ]
    publication = models.ForeignKey("Publication", on_delete=models.CASCADE)
    faculty = models.ForeignKey("faculty.Faculty", on_delete=models.CASCADE)
    author_order = models.PositiveIntegerField(default=1)
    author_role = models.CharField(
        max_length=50, choices=AUTHOR_ROLE_CHOICES, default="Main Author"
    )

    class Meta:
        ordering = ["author_order"]
        unique_together = [["publication", "faculty"]]

    def clean(self):
        super().clean()
        # Prevent two authors sharing the same position number on the same paper
        if self.publication_id and self.author_order is not None:
            qs = PublicationAuthor.objects.filter(
                publication_id=self.publication_id,
                author_order=self.author_order,
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    {
                        "author_order": f"Author order {self.author_order} is already taken for this publication. Please use a different position number."
                    }
                )


class PatentAuthor(models.Model):
    AUTHOR_ROLE_CHOICES = [
        ("Main Inventor", "Main Inventor"),
        ("Co-Inventor", "Co-Inventor"),
    ]
    patent = models.ForeignKey("Patent", on_delete=models.CASCADE)
    faculty = models.ForeignKey("faculty.Faculty", on_delete=models.CASCADE)
    author_order = models.PositiveIntegerField(default=1)
    author_role = models.CharField(
        max_length=50, choices=AUTHOR_ROLE_CHOICES, default="Main Inventor"
    )

    class Meta:
        ordering = ["author_order"]
        unique_together = [["patent", "faculty"]]

    def clean(self):
        super().clean()
        # Prevent two inventors sharing the same position number on the same patent
        if self.patent_id and self.author_order is not None:
            qs = PatentAuthor.objects.filter(
                patent_id=self.patent_id,
                author_order=self.author_order,
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    {
                        "author_order": f"Inventor order {self.author_order} is already taken for this patent. Please use a different position number."
                    }
                )


class Publication(SoftDeleteModel):
    PUBLICATION_TYPE_CHOICES = [
        ("Journal Paper", "Journal Paper"),
        ("Conference Paper", "Conference Paper"),
        ("Book", "Book"),
        ("Book Chapter", "Book Chapter"),
        ("Others", "Others"),
    ]
    Indexing_Choice = [
        ("Scopus", "Scopus"),
        ("Web of Science", "Web of Science"),
        ("SJR", "SJR"),
        ("Scimago", "Scimago"),
        ("Others", "Others"),
    ]
    internal_authors = models.ManyToManyField(
        "faculty.Faculty",
        through="PublicationAuthor",
        related_name="internal_publications",
        blank=True,
    )
    full_author_list = models.TextField(
        blank=True,
        null=True,
        help_text="List of all the author separated by commas if they are from other institutions or scholars",
    )
    title = models.TextField()
    campus = models.CharField(
        max_length=50,
        choices=[
            ("BBAU", "BBAU"),
            ("Satellite Campus Amethi", "Satellite Campus Amethi"),
        ],
    )
    publication_type = models.CharField(
        max_length=50, blank=True, null=True, choices=PUBLICATION_TYPE_CHOICES
    )
    other_publication_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Please specify publication type if 'Others' is selected",
    )
    name_of_journal_or_conference_or_publisher = models.CharField(
        max_length=255, blank=True, null=True
    )
    publication_date = models.DateField(null=True, blank=True)
    doi_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        validators=[validate_doi],
        help_text="Enter DOI as '10.XXXX/suffix' or 'https://doi.org/10.XXXX/suffix'.",
    )

    indexing = models.CharField(
        max_length=50, blank=True, null=True, choices=Indexing_Choice
    )
    others_indexing = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Please specify indexing name if 'Others' is selected",
    )
    title_fp = models.CharField(
        max_length=1000,
        blank=True,
        db_index=True,
        editable=False,
        help_text="Auto-generated alphanumeric fingerprint of the title for duplicate detection.",
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ["-publication_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["doi_url"],
                condition=models.Q(is_deleted=False, doi_url__isnull=False),
                name="unique_pub_doi_url",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "_existing_pub"):
            return

        if self.title:
            self.title = clean_title_string(self.title)

        if self.publication_type == "Others" and not self.other_publication_type:
            raise ValidationError(
                {
                    "other_publication_type": "This field is required when publication type is 'Others'."
                }
            )
        if self.indexing == "Others" and not self.others_indexing:
            raise ValidationError(
                {"others_indexing": "This field is required when indexing is 'Others'."}
            )

        if self.doi_url:
            # Normalize to canonical https://doi.org/... form before saving.
            raw = self.doi_url.strip()
            match = DOI_RE.match(raw)
            if match:
                self.doi_url = f"https://doi.org/{match.group(1)}"

            # DOI is the strict identifier — enforced at DB level too.
            qs_doi = Publication.objects.filter(
                doi_url__iexact=self.doi_url,
                is_deleted=False,
            )
            if self.pk:
                qs_doi = qs_doi.exclude(pk=self.pk)
            if qs_doi.exists():
                raise ValidationError(
                    {"doi_url": "A publication with this DOI URL already exists."}
                )
        else:
            # No DOI — fall back to title-based duplicate check.
            qs_title = Publication.objects.filter(
                title__iexact=self.title,
                is_deleted=False,
            )
            if self.pk:
                qs_title = qs_title.exclude(pk=self.pk)
            if qs_title.exists():
                raise ValidationError(
                    {
                        "title": (
                            "A publication with this exact title already exists. "
                            "If this is a co-authored paper, use the 'Claim' action "
                            "to link yourself to the existing record instead."
                        )
                    }
                )
            # Deep fingerprint check: single indexed DB query instead of O(N) Python loop.
            fp = title_fingerprint(self.title)
            if fp:
                # Store on instance so save() can persist it without recomputing.
                self.title_fp = fp
                qs_fp = Publication.objects.filter(
                    title_fp=fp,
                    is_deleted=False,
                )
                if self.pk:
                    qs_fp = qs_fp.exclude(pk=self.pk)
                conflict = qs_fp.first()
                if conflict:
                    raise ValidationError(
                        {
                            "title": (
                                f"A publication with a matching title already exists ('{conflict.title}'). "
                                "If this is a co-authored paper, use the 'Claim' action "
                                "to link yourself to the existing record instead."
                            )
                        }
                    )

    def save(self, *args, **kwargs):
        # Keep title_fp in sync on every save (including programmatic saves that skip clean()).
        if self.title:
            self.title_fp = title_fingerprint(self.title)
        else:
            self.title_fp = ""
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title[:50]}... ({self.publication_date})"


class Consultancy(SoftDeleteModel):
    faculty = models.ForeignKey(
        "faculty.Faculty",
        related_name="consultancies",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    department = models.ForeignKey(
        "academics.Department",
        related_name="consultancies",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    nature_of_consultancy = models.CharField(max_length=100, null=True, blank=True)
    name_of_awarding_agency_organization = models.CharField(
        max_length=100, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    campus = models.CharField(
        max_length=50,
        choices=[
            ("BBAU", "BBAU"),
            ("Satellite Campus Amethi", "Satellite Campus Amethi"),
        ],
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "Consultancies"
        constraints = [
            models.UniqueConstraint(
                fields=["faculty", "nature_of_consultancy", "start_date", "department"],
                condition=models.Q(is_deleted=False),
                name="unique_consultancy_faculty_nature_date_dept",
            )
        ]

    def clean(self):
        super().clean()

        # At least one of faculty or department must be set
        if not self.faculty and not self.department:
            raise ValidationError(
                "A consultancy must be associated with at least a Faculty member or a Department."
            )

        # Date order check
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                {"end_date": "End date cannot be before the start date."}
            )

        # Amount cannot be negative
        if self.amount is not None and self.amount < 0:
            raise ValidationError({"amount": "Consultancy amount cannot be negative."})

        # Duplicate check
        qs = Consultancy.objects.filter(
            faculty=self.faculty,
            nature_of_consultancy__iexact=self.nature_of_consultancy,
            start_date=self.start_date,
            department=self.department,
            is_deleted=False,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(
                "A consultancy record with the same Faculty, Nature of Consultancy, Start Date, and Department already exists."
            )

    def __str__(self):
        faculty_name = self.faculty.name if self.faculty else "No Faculty"
        consultancy = self.nature_of_consultancy or "No Consultancy"
        return f"{consultancy} ({faculty_name})"


class Patent(SoftDeleteModel):
    STATUS_CHOICES = [
        ("Filed", "Filed"),
        ("Published", "Published"),
        ("Granted", "Granted"),
    ]
    internal_inventors = models.ManyToManyField(
        "faculty.Faculty",
        through="PatentAuthor",
        related_name="internal_patents",
        blank=True,
    )
    full_inventor_list = models.TextField(
        blank=True,
        null=True,
        help_text="Name of all inventors seperated by commas if they are form other institutions",
    )
    title = models.TextField()
    patent_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Filed")
    date_of_filing = models.DateField(blank=True, null=True)
    description = RichTextField(blank=True, null=True)

    # Regenerated automatically on every save(); never edit directly.
    title_fp = models.CharField(
        max_length=1000,
        blank=True,
        db_index=True,
        editable=False,
        help_text="Auto-generated alphanumeric fingerprint of the title for duplicate detection.",
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ["-date_of_filing"]
        constraints = [
            models.UniqueConstraint(
                fields=["patent_number"],
                condition=models.Q(is_deleted=False, patent_number__isnull=False),
                name="unique_patent_number",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "_existing_patent"):
            return

        if self.title:
            self.title = clean_title_string(self.title)

        # Filing date cannot be in the future
        if self.date_of_filing and self.date_of_filing > timezone.now().date():
            raise ValidationError(
                {"date_of_filing": "Date of filing cannot be in the future."}
            )

        # Patent number required when status is Published or Granted
        # if self.status in ("Published", "Granted") and not self.patent_number:
        #     raise ValidationError(
        #         {"patent_number": f"Patent number is required when status is '{self.status}'."}
        #     )

        # Filing date required when status is Published or Granted
        if self.status in ("Published", "Granted") and not self.date_of_filing:
            raise ValidationError(
                {
                    "date_of_filing": f"Date of filing is required when status is '{self.status}'."
                }
            )

        if self.patent_number:
            # Patent number is the strict identifier — enforced at DB level too.
            qs_number = Patent.objects.filter(
                patent_number__iexact=self.patent_number,
                is_deleted=False,
            )
            if self.pk:
                qs_number = qs_number.exclude(pk=self.pk)
            if qs_number.exists():
                raise ValidationError(
                    {
                        "patent_number": "A patent with this Patent Number already exists."
                    }
                )
        else:
            # No patent number — fall back to title-based duplicate check.
            qs_title = Patent.objects.filter(
                title__iexact=self.title,
                is_deleted=False,
            )
            if self.pk:
                qs_title = qs_title.exclude(pk=self.pk)
            if qs_title.exists():
                raise ValidationError(
                    {
                        "title": (
                            "A patent with this exact title already exists. "
                            "If this is a co-invented patent, use the 'Claim' action "
                            "to link yourself to the existing record instead."
                        )
                    }
                )
            # Deep fingerprint check: single indexed DB query instead of O(N) Python loop.
            fp = title_fingerprint(self.title)
            if fp:
                # Store on instance so save() can persist it without recomputing.
                self.title_fp = fp
                qs_fp = Patent.objects.filter(
                    title_fp=fp,
                    is_deleted=False,
                )
                if self.pk:
                    qs_fp = qs_fp.exclude(pk=self.pk)
                conflict = qs_fp.first()
                if conflict:
                    raise ValidationError(
                        {
                            "title": (
                                f"A patent with a matching title already exists ('{conflict.title}'). "
                                "If this is a co-invented patent, use the 'Claim' action "
                                "to link yourself to the existing record instead."
                            )
                        }
                    )

    def save(self, *args, **kwargs):
        # Keep title_fp in sync on every save (including programmatic saves that skip clean()).
        if self.title:
            self.title_fp = title_fingerprint(self.title)
        else:
            self.title_fp = ""
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title[:50]}... ({self.date_of_filing})"


class ResearchDevelopmentCellMember(SoftDeleteModel):
    faculty = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.CASCADE,
        related_name="rd_cell_roles",
        verbose_name="R&D Cell Member",
    )
    designation = models.CharField(
        max_length=255, help_text="Designation in R&D Cell e.g. Director, Member"
    )
    order = models.PositiveIntegerField(default=0)
    history = HistoricalRecords()

    class Meta:
        ordering = ["order", "faculty__name"]
        verbose_name = "R&D Cell Member"
        verbose_name_plural = "R&D Cell Members"

    def __str__(self):
        return f"{self.faculty.name} - {self.designation}"
