from django.db import models
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords
from apps.accounts.models import SoftDeleteModel


ADMISSION_CATEGORY_CHOICES = [
    ("UG", "Undergraduate (UG)"),
    ("PG", "Postgraduate (PG)"),
    ("PHD", "Ph.D."),
    ("International", "International"),
    ("Others", "Others"),
]


class AdmissionSession(SoftDeleteModel):
    session_name = models.CharField(
        max_length=100, help_text="e.g., Admissions 2026-2027"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active sessions will be displayed on the main portal by default.",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-start_date", "-id"]

    def __str__(self):
        return f"{self.session_name} {'(Active)' if self.is_active else '(Archived)'}"


class AdmissionUpdate(SoftDeleteModel):
    session = models.ForeignKey(
        AdmissionSession,
        on_delete=models.CASCADE,
        related_name="updates",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Subject / Headline",
        help_text="The main heading for this update or announcement.",
    )
    departments = models.ManyToManyField(
        "academics.Department",
        blank=True,
        help_text="Select specific departments if applicable.",
    )
    programs = models.ManyToManyField(
        "academics.Program",
        blank=True,
        help_text="Select specific programs if applicable.",
    )
    category = models.CharField(max_length=50, choices=ADMISSION_CATEGORY_CHOICES)
    other_category_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Specify if 'Others' is selected.",
    )
    description = RichTextField(blank=True, null=True)
    attachment = models.FileField(upload_to="admission/updates/", blank=True, null=True)
    date_posted = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-date_posted", "-id"]

    def clean(self):
        super().clean()
        if self.category == "Others" and not self.other_category_name:
            raise ValidationError(
                {
                    "other_category_name": "This field is required when category is 'Others'."
                }
            )

    def __str__(self):
        return f"[{self.category}] {self.title}"


class AdmissionMeritList(SoftDeleteModel):
    session = models.ForeignKey(
        AdmissionSession,
        on_delete=models.CASCADE,
        related_name="merit_lists",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Merit List / Cutoff Title",
        help_text="e.g., First Merit List for B.Tech",
    )
    departments = models.ManyToManyField(
        "academics.Department",
        blank=True,
        help_text="Select specific departments if applicable.",
    )
    programs = models.ManyToManyField(
        "academics.Program",
        blank=True,
        help_text="Select specific programs if applicable.",
    )
    category = models.CharField(max_length=50, choices=ADMISSION_CATEGORY_CHOICES)
    other_category_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Specify if 'Others' is selected.",
    )
    description = RichTextField(blank=True, null=True)
    attachment = models.FileField(
        upload_to="admission/merit_lists/", blank=True, null=True
    )
    date_posted = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-date_posted", "-id"]

    def clean(self):
        super().clean()
        if self.category == "Others" and not self.other_category_name:
            raise ValidationError(
                {
                    "other_category_name": "This field is required when category is 'Others'."
                }
            )

    def __str__(self):
        return f"[{self.category}] {self.title}"


class AdmissionBrochure(SoftDeleteModel):
    session = models.ForeignKey(
        AdmissionSession,
        on_delete=models.CASCADE,
        related_name="brochures",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Document Name",
        help_text="e.g., UG Prospectus 2026",
    )
    departments = models.ManyToManyField(
        "academics.Department",
        blank=True,
        help_text="Select specific departments if applicable.",
    )
    programs = models.ManyToManyField(
        "academics.Program",
        blank=True,
        help_text="Select specific programs if applicable.",
    )
    category = models.CharField(max_length=50, choices=ADMISSION_CATEGORY_CHOICES)
    other_category_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Specify if 'Others' is selected.",
    )
    file = models.FileField(upload_to="admission/brochures/")
    upload_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-upload_date", "-id"]

    def clean(self):
        super().clean()
        if self.category == "Others" and not self.other_category_name:
            raise ValidationError(
                {
                    "other_category_name": "This field is required when category is 'Others'."
                }
            )

    def __str__(self):
        return f"{self.title} ({self.category})"


class AdmissionSchedule(SoftDeleteModel):
    session = models.ForeignKey(
        AdmissionSession,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    event_name = models.CharField(
        max_length=255, help_text="e.g., Last Date to Apply, First Merit List"
    )
    departments = models.ManyToManyField(
        "academics.Department",
        blank=True,
        help_text="Select specific departments if applicable.",
    )
    programs = models.ManyToManyField(
        "academics.Program",
        blank=True,
        help_text="Select specific programs if applicable.",
    )
    category = models.CharField(max_length=50, choices=ADMISSION_CATEGORY_CHOICES)
    event_date = models.DateTimeField(
        help_text="Date and time of the event (or deadline)"
    )
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["event_date", "id"]

    def __str__(self):
        return f"{self.event_name} - {self.event_date.strftime('%Y-%m-%d')}"


class AdmissionContact(SoftDeleteModel):
    session = models.ForeignKey(
        AdmissionSession,
        on_delete=models.CASCADE,
        related_name="contacts",
        null=True,
        blank=True,
        help_text="Leave blank if this contact is not session-specific.",
    )
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(
        max_length=50, choices=ADMISSION_CATEGORY_CHOICES, null=True, blank=True
    )
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["name"]

    def clean(self):
        super().clean()
        if not self.email and not self.phone_number:
            raise ValidationError(
                "At least one contact method (email or phone number) must be provided."
            )

    def __str__(self):
        return f"{self.name} - {self.designation or 'Contact'}"


class AdmissionLink(SoftDeleteModel):
    session = models.ForeignKey(
        AdmissionSession,
        on_delete=models.CASCADE,
        related_name="links",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Link Display Text",
        help_text="e.g., Apply Now, CUET Portal",
    )
    category = models.CharField(max_length=50, choices=ADMISSION_CATEGORY_CHOICES)
    url = models.URLField(max_length=500)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

# --- Admission Committee ---

class AdmissionCommitteeMember(SoftDeleteModel):
    name = models.CharField(max_length=255, verbose_name="Name of the Member")
    designation = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="For S.No sorting")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} - Admission Committee"

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Admission Committee Members"


class AdmissionCommitteeMinutes(SoftDeleteModel):
    meeting_title = models.CharField(max_length=255)
    date_of_meeting = models.DateField()
    file = models.FileField(upload_to="admission/committee_minutes/")
    is_private = models.BooleanField(
        default=False,
        help_text="If checked, these minutes will only be visible to authenticated, authorized personnel.",
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.meeting_title} ({self.date_of_meeting})"

    class Meta:
        ordering = ["-date_of_meeting"]
        verbose_name_plural = "Admission Committee Minutes"
