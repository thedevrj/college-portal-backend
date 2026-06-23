from django.db import models
from apps.accounts.models import SoftDeleteModel
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords


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
        on_delete=models.CASCADE,
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
    date_of_birth = models.DateField(null=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    supervisor = models.ForeignKey(
        "faculty.Faculty",
        related_name="supervised_scholars_new",
        on_delete=models.CASCADE,
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
    subject = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Specialization"
    )
    date_of_registration = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pursuing")
    thesis_submission_date = models.DateField(null=True, blank=True)
    viva_voce_date = models.DateField(null=True, blank=True)
    award_date = models.DateField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
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

        # --- Duplicate entry check ---
        #  This manual check covers cases where supervisor or date_of_birth is NULL.)
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
        help_text="Enter the list of all the author separated by commas ",
    )
    title = models.TextField(null=True, blank=True)
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
    doi_url = models.URLField(max_length=500, blank=True, null=True)

    indexing = models.CharField(
        max_length=50, blank=True, null=True, choices=Indexing_Choice
    )
    others_indexing = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Please specify indexing name if 'Others' is selected",
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

        if self.title:
            qs_title = Publication.objects.filter(
                title__iexact=self.title,
                is_deleted=False,
            )
            if self.pk:
                qs_title = qs_title.exclude(pk=self.pk)
            # Cannot do a simple title match because titles might naturally overlap?
            # We will rely on DOI primarily. If we want title duplicate check, we warn instead of block.

        if self.doi_url:
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
        help_text="Exact string of all inventors (e.g. 'J. Doe, M. Smith')",
    )
    title = models.TextField()
    patent_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Filed")
    date_of_filing = models.DateField(blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["patent_number"],
                condition=models.Q(is_deleted=False, patent_number__isnull=False),
                name="unique_patent_number",
            ),
        ]

    def clean(self):
        super().clean()
        if self.title:
            qs_title = Patent.objects.filter(
                title__iexact=self.title,
                is_deleted=False,
            )
            if self.pk:
                qs_title = qs_title.exclude(pk=self.pk)
            # Similar to publication, a strict block on exact title might cause issues if different groups file identically titled but distinct patents, though unlikely. We'll rely on patent_number primarily for strict blocking.

        if self.patent_number:
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

    def __str__(self):
        return f"{self.title[:50]}... ({self.date_of_filing})"


class ResearchDevelopmentCellMember(SoftDeleteModel):
    faculty = models.ForeignKey(
        "faculty.Faculty", on_delete=models.CASCADE, related_name="rd_cell_roles"
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
