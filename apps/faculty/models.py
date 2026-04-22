from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField


class Faculty(models.Model):

    CAMPUS_CHOICES = [
        ("BBAU", "BBAU"),
        ("Satellite Campus Amethi", "Satellite Campus Amethi"),
    ]

    staff_no = models.PositiveIntegerField(unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to="faculty/", null=True, blank=True)
    photo_alt_text = models.CharField(
        max_length=255, blank=True, help_text="GIGW accessibility text for the image"
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    designation = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)
    campus = models.CharField(max_length=50, choices=CAMPUS_CHOICES)
    bio = RichTextField(blank=True)

    qualification = RichTextField(blank=True)
    teaching_exp = models.CharField(
        max_length=100, blank=True, help_text="e.g., 10 Years 6 Months"
    )
    research_exp = models.CharField(
        max_length=100, blank=True, help_text="e.g., 5 Years"
    )
    research_int = RichTextField(blank=True)

    google_scholar_url = models.URLField(blank=True)
    scopus_url = models.URLField(blank=True)
    research_gate_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True, help_text="Personal or lab website")

    cv_document = models.FileField(
        upload_to="faculty_cvs/",
        null=True,
        blank=True,
        help_text="Upload CV/Resume in PDF format",
    )

    roles = models.JSONField(default=list, blank=True)

    school = models.ForeignKey(
        "academics.School",
        related_name="faculty",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    department = models.ForeignKey(
        "academics.Department",
        related_name="faculty",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    centre = models.ForeignKey(
        "centres.Centre",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculty",
    )

    insti_email = models.EmailField(null=True, blank=True)
    other_email = models.EmailField(null=True, blank=True)
    phone1 = models.CharField(max_length=10, null=True, blank=True)
    phone2 = models.CharField(max_length=10, null=True, blank=True)

    date_of_joining = models.DateField(null=True, blank=True)
    date_of_superannuation = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(
        default=True, help_text="Uncheck if the faculty member leaves the university"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Faculty"

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        from django.apps import apps

        if self.staff_no:
            try:
                Staff = apps.get_model("staff", "Staff")
                if Staff.objects.filter(staff_no=self.staff_no).exists():
                    raise ValidationError(
                        {
                            "staff_no": "A Non-Teaching Staff member with this staff number already exists."
                        }
                    )
            except LookupError:
                pass

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) or "faculty"

        # Ensure slug is unique by appending a suffix if necessary
        base_slug = self.slug[:250]  # Leave room for suffix
        unique_slug = base_slug
        counter = 1

        # Check for collisions with other records
        while True:
            collision = (
                Faculty.objects.filter(slug=unique_slug).exclude(pk=self.pk).first()
            )
            if not collision:
                break

            # If they share a valid staff_no, they represent the same faculty member
            if self.staff_no and collision.staff_no == self.staff_no:
                break

            unique_slug = f"{base_slug}-{counter}"
            counter += 1

        self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.staff_no or 'No ID'})"
