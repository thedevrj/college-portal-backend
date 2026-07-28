from django.db import models
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords
from django.utils import timezone
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

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {"end_date": "End date cannot be before the start date."}
            )


class AdmissionStream(SoftDeleteModel):
    session = models.ForeignKey(
        AdmissionSession, on_delete=models.CASCADE, related_name="streams"
    )
    name = models.CharField(
        max_length=255, help_text="e.g., B.Tech via JEE, PG via CUET"
    )
    category = models.CharField(max_length=50, choices=ADMISSION_CATEGORY_CHOICES)
    order = models.PositiveIntegerField(
        default=0, help_text="Order in which tabs are displayed"
    )
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Admission Programs"
        constraints = [
            models.UniqueConstraint(
                fields=["session", "name"],
                condition=models.Q(is_deleted=False),
                name="unique_admission_stream_per_session",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.session.session_name})"


class AdmissionProspectus(SoftDeleteModel):
    session = models.ForeignKey(
        AdmissionSession, on_delete=models.CASCADE, related_name="prospectuses"
    )
    category = models.CharField(max_length=50, choices=ADMISSION_CATEGORY_CHOICES)
    title = models.CharField(
        max_length=255, help_text="e.g., CUET PG Information Bulletin"
    )
    file = models.FileField(upload_to="admission/prospectuses/")
    upload_date = models.DateField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-upload_date", "-id"]
        verbose_name_plural = "Admission Prospectus"

    def __str__(self):
        return f"{self.title} - {self.get_category_display()} ({self.session.session_name})"


class AdmissionNotice(SoftDeleteModel):
    session = models.ForeignKey(
        AdmissionSession, on_delete=models.CASCADE, related_name="notices"
    )
    category = models.CharField(max_length=50, choices=ADMISSION_CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="admission/notices/", blank=True, null=True)
    date_posted = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(
        default=False,
        help_text="Manually archive this notice.",
    )
    archive_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date after which this notice automatically becomes archived.",
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ["-date_posted", "-id"]

    def __str__(self):
        return f"{self.title} - {self.get_category_display()} ({self.session.session_name})"


class RegistrationPortal(SoftDeleteModel):
    session = models.ForeignKey(
        AdmissionSession,
        on_delete=models.CASCADE,
        related_name="registration_portals",
    )
    category = models.CharField(max_length=50, choices=ADMISSION_CATEGORY_CHOICES)
    portal_name = models.CharField(
        max_length=255, help_text="e.g., Samarth CUET-PG Portal"
    )
    url = models.URLField(max_length=500)
    registration_start = models.DateField(null=True, blank=True)
    registration_end = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.portal_name} - {self.get_category_display()}"

    def clean(self):
        super().clean()
        if (
            self.registration_start
            and self.registration_end
            and self.registration_end < self.registration_start
        ):
            raise ValidationError(
                {
                    "registration_end": "Registration end date cannot be before the start date."
                }
            )


class CounsellingPhase(SoftDeleteModel):
    stream = models.ForeignKey(
        AdmissionStream, on_delete=models.CASCADE, related_name="counselling_phases"
    )
    phase_name = models.CharField(
        max_length=100, help_text="e.g., Phase 1, Phase 2, Spot Counselling"
    )
    order = models.PositiveIntegerField(
        default=0, help_text="Chronological order of the phase"
    )
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Admission Cutoff Rounds"

    def __str__(self):
        return f"{self.phase_name} ({self.stream.name})"


class MeritList(SoftDeleteModel):
    phase = models.ForeignKey(
        CounsellingPhase, on_delete=models.CASCADE, related_name="merit_lists"
    )
    programme = models.ForeignKey(
        "academics.program",
        on_delete=models.CASCADE,
        related_name="admission_results",
    )
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.CASCADE,
        related_name="admission_results",
        blank=True,
        null=True,
    )
    pdf_file = models.FileField(upload_to="admission/merit_lists/")
    upload_date = models.DateField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["programme", "-upload_date"]

    def __str__(self):
        return f" ({self.programme}) ({self.phase.phase_name}) "


# --- Admission Committee ---


class AdmissionCommitteeMember(SoftDeleteModel):
    name = models.CharField(max_length=255, verbose_name="Name of the Member")
    designation = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="For S.No sorting")
    history = HistoricalRecords()

    def clean(self):
        super().clean()
        if self.email:
            from django.core.validators import validate_email

            val = str(self.email).strip().lower()
            try:
                validate_email(val)
            except Exception:
                raise ValidationError({"email": "Please enter a valid email address."})
            self.email = val

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
    is_archived = models.BooleanField(
        default=False,
        help_text="Manually archive these minutes.",
    )
    archive_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date after which these minutes automatically become archived.",
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.meeting_title} ({self.date_of_meeting})"

    class Meta:
        ordering = ["-date_of_meeting"]
        verbose_name_plural = "Admission Committee Minutes"
