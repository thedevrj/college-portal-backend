from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField


class ResearchArea(models.Model):
    department = models.ForeignKey(
        "academics.Department", related_name="research_areas", on_delete=models.CASCADE
    )
    available_research_areas_or_Specialization = models.CharField(max_length=255)
    description = RichTextField(blank=True)

    def __str__(self):
        return f"{self.available_research_areas_or_Specialization} ({self.department.name})"


class ResearchFacility(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = RichTextField(blank=True)
    image = models.ImageField(upload_to="research/facilities/", null=True, blank=True)
    incharge = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_facilities",
    )

    class Meta:
        verbose_name_plural = "Research Facilities"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ResearchProject(models.Model):
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
    principal_investigator = models.ForeignKey(
        "faculty.Faculty", related_name="pi_projects_new", on_delete=models.CASCADE
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
    description = RichTextField(blank=True)

    def __str__(self):
        return self.title


class ResearchScholar(models.Model):
    STATUS_CHOICES = [
        ("Pursuing", "Pursuing"),
        ("Thesis Submitted", "Thesis Submitted"),
        ("Awarded", "Awarded"),
    ]
    department = models.ForeignKey(
        "academics.Department", related_name="scholars_new", on_delete=models.CASCADE
    )
    scholar_name = models.CharField(max_length=255)
    enrollment_no = models.CharField(max_length=100, unique=True, null=True)
    supervisor = models.ForeignKey(
        "faculty.Faculty",
        related_name="supervised_scholars_new",
        on_delete=models.CASCADE,
    )
    co_supervisor = models.ManyToManyField(
        "faculty.Faculty",
        related_name="co_supervised_scholars_new",
        blank=True,
        help_text="Select multiple time to add many co-supervisor(s)",
    )
    research_topic = models.CharField(max_length=500, null=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    date_of_registration = models.DateField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pursuing")
    thesis_submission_date = models.DateField(null=True)
    viva_voce_date = models.DateField(null=True)
    award_date = models.DateField(null=True)

    def __str__(self):
        return self.scholar_name


class Publication(models.Model):
    PUBLICATION_TYPE_CHOICES = [
        ("Journal Paper", "Journal Paper"),
        ("Conference Paper", "Conference Paper"),
        ("Research Paper", "Research Paper"),
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
    faculty = models.ForeignKey(
        "faculty.Faculty",
        related_name="publications",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    department = models.ForeignKey(
        "academics.Department",
        related_name="publications",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    title = models.TextField()
    name_of_journal_or_conference_or_publisher = models.CharField(
        max_length=255, blank=True, null=True
    )
    publication_date = models.DateField(null=True, blank=True)
    doi_url = models.URLField(max_length=500, blank=True, null=True)
    publication_type = models.CharField(
        max_length=50, blank=True, choices=PUBLICATION_TYPE_CHOICES
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

    class Meta:
        ordering = ["-publication_date"]

    def __str__(self):
        return f"{self.title[:50]}... ({self.publication_date})"


class Patent(models.Model):
    STATUS_CHOICES = [
        ("Filed", "Filed"),
        ("Published", "Published"),
        ("Granted", "Granted"),
    ]
    faculty = models.ForeignKey(
        "faculty.Faculty", related_name="patents", on_delete=models.CASCADE
    )
    department = models.ForeignKey(
        "academics.Department",
        related_name="patents",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    title = models.TextField()
    patent_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Filed")
    date_of_filing = models.DateField(blank=True, null=True)
    description = RichTextField(blank=True)

    def __str__(self):
        return f"{self.title[:50]}... ({self.date_of_filing})"


class ResearchDevelopmentCellMember(models.Model):
    faculty = models.ForeignKey(
        "faculty.Faculty", on_delete=models.CASCADE, related_name="rd_cell_roles"
    )
    designation = models.CharField(
        max_length=255, help_text="Designation in R&D Cell e.g. Director, Member"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "faculty__name"]
        verbose_name = "R&D Cell Member"
        verbose_name_plural = "R&D Cell Members"

    def __str__(self):
        return f"{self.faculty.name} - {self.designation}"
