from django.db import models
from django.utils.text import slugify
from simple_history.models import HistoricalRecords
from apps.accounts.models import SoftDeleteModel


class Staff(SoftDeleteModel):

    CAMPUS_CHOICES = [
        ("BBAU", "BBAU"),
        ("Satellite Campus Amethi", "Satellite Campus Amethi"),
    ]

    user = models.OneToOneField(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_profile",
    )
    staff_no = models.PositiveIntegerField(unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to="staff/", null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    designation = models.CharField(max_length=255, blank=True)
    department_section_cell = models.CharField(
        max_length=255, blank=True, verbose_name="Department/Section/Cell"
    )
    roles = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma separated values indicating associated sections for roles",
    )
    dob = models.DateField(null=True, blank=True)

    insti_email = models.EmailField(null=True, blank=True)
    other_email = models.EmailField(null=True, blank=True)
    phone1 = models.CharField(max_length=20, null=True, blank=True)
    phone2 = models.CharField(max_length=20, null=True, blank=True)

    staff_type = models.CharField(
        max_length=100, blank=True, help_text="e.g., Permanent, Contract"
    )
    campus = models.CharField(max_length=50, choices=CAMPUS_CHOICES, default="BBAU")

    is_active = models.BooleanField(
        default=True, help_text="Uncheck if the staff member leaves the university"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Staff"

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        from django.apps import apps

        if self.staff_no:
            try:
                Faculty = apps.get_model("faculty", "Faculty")
                if Faculty.objects.filter(staff_no=self.staff_no).exists():
                    raise ValidationError(
                        {
                            "staff_no": "A Faculty member with this staff number already exists."
                        }
                    )
            except LookupError:
                pass

    def save(self, *args, **kwargs):
        # 1. Sync or Create User if staff_no exists
        if self.staff_no:
            from django.contrib.auth.models import User
            from apps.accounts.models import UserProfile

            username = f"staff_{self.staff_no}"

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
                        password=f"Bbau@123",  # Default password
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
            self.slug = slugify(self.name) or "staff"

        base_slug = self.slug[:250]
        unique_slug = base_slug
        counter = 1

        while True:
            collision = (
                Staff.objects.filter(slug=unique_slug).exclude(pk=self.pk).first()
            )
            if not collision:
                break

            if self.staff_no and collision.staff_no == self.staff_no:
                break

            unique_slug = f"{base_slug}-{counter}"
            counter += 1

        self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.staff_no or 'No ID'})"
