from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField


class ResearchArea(models.Model):
    department = models.ForeignKey(
        "academics.Department", related_name="research_areas", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = RichTextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.department.name})"


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
    location = models.CharField(max_length=255, blank=True)

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
        "faculty.Faculty", related_name="co_pi_projects_new", blank=True
    )
    funding_agency = models.CharField(max_length=255)
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
    enrollment_no = models.CharField(max_length=100, unique=True)
    supervisor = models.ForeignKey(
        "faculty.Faculty",
        related_name="supervised_scholars_new",
        on_delete=models.CASCADE,
    )
    co_supervisor = models.ForeignKey(
        "faculty.Faculty",
        related_name="co_supervised_scholars_new",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    research_topic = models.CharField(max_length=500)
    registration_year = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pursuing")

    def __str__(self):
        return self.scholar_name


class Publication(models.Model):
    PUBLICATION_TYPE_CHOICES = [
        ("Journal", "Journal Paper"),
        ("Conference", "Conference Paper"),
        ("Book", "Book"),
        ("Book Chapter", "Book Chapter"),
        ("Patent", "Patent"),
        ("Others", "Others"),
    ]
    faculty = models.ForeignKey(
        "faculty.Faculty", related_name="publications", on_delete=models.CASCADE
    )
    department = models.ForeignKey(
        "academics.Department", related_name="publications", on_delete=models.CASCADE
    )
    title = models.TextField()
    journal_name = models.CharField(max_length=255, blank=True, null=True)
    publication_year = models.PositiveIntegerField()
    doi_url = models.URLField(max_length=500, blank=True, null=True)
    publication_type = models.CharField(max_length=50, choices=PUBLICATION_TYPE_CHOICES)
    citation = models.TextField(
        blank=True, help_text="Full citation string if available"
    )

    class Meta:
        ordering = ["-publication_year"]

    def __str__(self):
        return f"{self.title[:50]}... ({self.publication_year})"


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
        "academics.Department", related_name="patents", on_delete=models.CASCADE
    )
    title = models.TextField()
    patent_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Filed")
    year = models.PositiveIntegerField()
    description = RichTextField(blank=True)

    def __str__(self):
        return f"{self.title[:50]}... ({self.year})"


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
