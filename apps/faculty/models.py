from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords
from apps.accounts.models import SoftDeleteModel

class Faculty(SoftDeleteModel):

    CAMPUS_CHOICES = [
        ("BBAU", "BBAU"),
        ("Satellite Campus Amethi", "Satellite Campus Amethi"),
    ]
    
    user = models.OneToOneField(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculty_profile",
        help_text="Link this faculty record to a user account for login access."
    )

    staff_no = models.PositiveIntegerField(
        unique=True,
    )
    photo = models.ImageField(upload_to="faculty/", null=True, blank=True)
    photo_alt_text = models.CharField(
        max_length=255, blank=True, help_text="GIGW accessibility text for the image"
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    designation = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)
    campus = models.CharField(max_length=50, choices=CAMPUS_CHOICES)

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

    bio = RichTextField(blank=True, null=True)

    qualification = RichTextField(blank=True, null=True)
    teaching_exp = models.CharField(
        max_length=100, blank=True, null=True, help_text="e.g., 10 Years 6 Months"
    )
    research_exp = models.CharField(
        max_length=100, blank=True, null=True, help_text="e.g., 5 Years"
    )
    research_int = RichTextField(blank=True, null=True)

    google_scholar_url = models.URLField(blank=True, null=True)
    scopus_url = models.URLField(blank=True, null=True)
    research_gate_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(
        blank=True, null=True, help_text="Personal or lab website"
    )

    cv_document = models.FileField(
        upload_to="faculty_cvs/",
        null=True,
        blank=True,
        help_text="Upload CV/Resume in PDF format",
    )

    roles = models.JSONField(default=list, blank=True)

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
    history = HistoricalRecords()

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
        # 1. Sync or Create User if staff_no exists
        if self.staff_no:
            from django.contrib.auth.models import User
            from apps.accounts.models import UserProfile
            username = f"faculty_{self.staff_no}"
            
            is_new = self.pk is None
            
            if not self.user:
                # Check if user already exists with this username
                existing_user = User.objects.filter(username=username).first()
                if existing_user:
                    self.user = existing_user
                else:
                    user = User.objects.create_user(
                        username=username,
                        email=self.insti_email or "",
                        password=f"bbau@{self.staff_no}" # Default password
                    )
                    self.user = user
            
            # Sync User fields
            if self.user:
                self.user.email = self.insti_email or ""
                self.user.first_name = self.name.split(" ")[0]
                self.user.last_name = " ".join(self.name.split(" ")[1:])
                self.user.save()
                
                # Ensure UserProfile exists
                profile, _ = UserProfile.objects.get_or_create(user=self.user)
                
                # If this is a newly linked account or the profile was just activated for the portal
                if not profile.is_portal_user:
                    profile.force_password_change = True
                    profile.employee_id = str(self.staff_no)
                    profile.is_portal_user = True
                    profile.save()

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
