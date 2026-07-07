from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import RegexValidator
from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
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
        help_text="Link this faculty record to a user account for login access.",
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

    orcid_id = models.CharField(
        max_length=19,
        null=True,
        blank=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$",
                message="ORCID ID must be in the format XXXX-XXXX-XXXX-XXXX (e.g., 0000-0003-0902-4386).",
            )
        ],
        help_text="ORCID ID (e.g., 0000-0003-0902-4386)",
    )

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

        import re
        from django.core.validators import validate_email

        for phone_field in ["phone1", "phone2"]:
            val = getattr(self, phone_field)
            if val:
                val = str(val).strip()
                if not re.match(r"^\d{10}$", val):
                    raise ValidationError(
                        {phone_field: "Phone number must be exactly 10 digits."}
                    )
                setattr(self, phone_field, val)

        for email_field in ["insti_email", "other_email"]:
            val = getattr(self, email_field)
            if val:
                val = str(val).strip().lower()
                try:
                    validate_email(val)
                except ValidationError:
                    raise ValidationError(
                        {email_field: "Please enter a valid email address."}
                    )
                if email_field == "insti_email" and not val.endswith("@bbau.ac.in"):
                    raise ValidationError(
                        {email_field: "Institutional email must end with @bbau.ac.in"}
                    )
                setattr(self, email_field, val)

        # Date of birth cannot be in the future
        if self.dob and self.dob > timezone.now().date():
            raise ValidationError(
                {"dob": "Date of birth cannot be in the future."}
            )

        # Date of superannuation must be after date of joining
        if (
            self.date_of_joining
            and self.date_of_superannuation
            and self.date_of_superannuation < self.date_of_joining
        ):
            raise ValidationError(
                {"date_of_superannuation": "Date of superannuation cannot be before date of joining."}
            )

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
                        password=f"bbau@{self.staff_no}",  # Default password
                    )
                    self.user = user

            # Sync User fields
            if self.user:
                self.user.email = self.insti_email or ""
                self.user.first_name = self.name.split(" ")[0]
                self.user.last_name = " ".join(self.name.split(" ")[1:])
                self.user.save()

                # Ensure UserProfile exists
                profile, created = UserProfile.objects.get_or_create(user=self.user)

                # Safety First: Only force password change if the user was just created
                # or if they don't have a portal profile yet.
                if created:
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


class InvitedTalk(SoftDeleteModel):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="invited_talks",
        help_text="Faculty member who gave the talk",
    )
    title = models.CharField(max_length=500, help_text="Title of the talk")
    event_name = models.CharField(
        max_length=500, help_text="Name of the event", null=True, blank=True
    )
    role = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="e.g., Keynote Speaker, Session Chair, Guest Lecturer",
    )
    date = models.DateField(null=True, blank=True)
    venue = models.CharField(
        max_length=500, blank=True, null=True, help_text="Location of the event"
    )
    link = models.URLField(
        blank=True, null=True, help_text="Link to the event or talk video/slides"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-date", "title"]
        verbose_name = "Invited Talk"
        verbose_name_plural = "Invited Talks"

    def __str__(self):
        return f"{self.title[:50]} - {self.faculty.name}"


class CourseDesign(SoftDeleteModel):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="course_designs",
        help_text="Faculty member who designed the course",
    )
    course_name = models.CharField(
        max_length=500,
        help_text="Name of the course designed",
        verbose_name="Course Name",
    )
    course_level = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=[
            ("UG", "Undergraduate"),
            ("PG", "Postgraduate"),
            ("Integrated", "Integrated"),
            ("PHD", "PhD"),
            ("Others", "Others"),
        ],
    )
    other_course_level = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Please specify the level if 'Others' is selected",
    )
    nature_of_contribution = models.TextField(
        blank=True, null=True, help_text="Nature of contribution eg: Alone, Team Member"
    )
    description = RichTextField(
        blank=True, null=True, help_text="Additional details about the course"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def clean(self):
        super().clean()
        if self.course_level == "Others" and not self.other_course_level:
            raise ValidationError(
                {
                    "other_course_level": "This field is required when course_level is 'Others'."
                }
            )

    class Meta:
        ordering = ["course_name"]
        verbose_name = "Course Design"
        verbose_name_plural = "Course Designs"

    def __str__(self):
        return f"{self.course_name[:50]} - {self.faculty.name}"


class Membership(SoftDeleteModel):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="memberships",
        help_text="Faculty member who is a member",
    )
    name = models.CharField(
        max_length=500,
        help_text="Name of the membership",
        verbose_name="Membership Name",
    )
    order_no = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Order number (e.g. ABC123XYZ)",
        verbose_name="Order Number",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["name"]
        verbose_name = "Membership"
        verbose_name_plural = "Member/Expert/Membership"

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {"end_date": "End date cannot be before the start date."}
            )

    def __str__(self):
        return f"{self.name[:50]} - {self.faculty.name}"
