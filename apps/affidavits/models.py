import uuid
from django.db import models
from apps.accounts.models import SoftDeleteModel
from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model

User = get_user_model()


from django.core.validators import RegexValidator, EmailValidator

phone_validator = RegexValidator(
    regex=r"^[6-9]\d{9}$",
    message="Phone number must be a valid 10-digit mobile number starting with 6, 7, 8, or 9.",
)


class SubmissionStatus(models.TextChoices):
    SUBMITTED = "submitted", "Submitted"
    UNDER_VERIFICATION = "under_verification", "Under Verification"
    VERIFIED = "verified", "Verified"
    REJECTED = "rejected", "Rejected"




def student_affidavit_path(instance, filename):
    return f"affidavits/student/{instance.tracking_id}_{filename}"


def parent_affidavit_path(instance, filename):
    return f"affidavits/parent/{instance.tracking_id}_{filename}"


class Affidavit(SoftDeleteModel):
    tracking_id = models.CharField(max_length=20, unique=True, editable=False)

    student_name = models.CharField(max_length=150)
    roll_number = models.CharField(max_length=50, help_text="Student's roll no.")
    enrollment_number = models.CharField(max_length=50, help_text="Student's enrollment no.")
    program_name = models.CharField(max_length=150, blank=True)
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="affidavits",
        verbose_name="Department",
    )
    student_phone = models.CharField(max_length=10, validators=[phone_validator], verbose_name="Student Phone")
    student_email = models.EmailField(validators=[EmailValidator(message="Enter a valid email address.")], verbose_name="Student Email")

    parent_name = models.CharField(max_length=150, blank=True)
    parent_phone = models.CharField(max_length=10, validators=[phone_validator], verbose_name="Parent Phone", blank=True)

    student_affidavit = models.FileField(upload_to=student_affidavit_path)
    parent_affidavit = models.FileField(upload_to=parent_affidavit_path)

    status = models.CharField(max_length=20, choices=SubmissionStatus.choices, default=SubmissionStatus.SUBMITTED)
    remarks = models.TextField(blank=True, help_text="Verification remarks, visible to the submitter on tracking page")

    submitted_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Affidavit Submission"
        verbose_name_plural = "Affidavit Submissions"
        ordering = ["-submitted_on"]

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = f"BBAU-AFF-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_id} - {self.student_name}"


class AffidavitFAQ(SoftDeleteModel):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField()

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Affidavits FAQ"
        verbose_name_plural = "Affidavits FAQs"
        ordering = ["order"]

    def __str__(self):
        return self.question


class SampleAffidavit(SoftDeleteModel):
    affidavit_type = [
        ("STUDENT", "Student"),
        ("PARENT", "Parent"),
    ]
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="affidavits/sample/")
    affidavit_category = models.CharField(max_length=20, choices=affidavit_type)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Sample Affidavit"
        verbose_name_plural = "Sample Affidavits"

    def __str__(self):
        return self.title


class AffidavitGuidelines(SoftDeleteModel):
    title = models.CharField(max_length=255)
    content = models.TextField()

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Affidavits Guideline"
        verbose_name_plural = "Affidavits Guidelines"

    def __str__(self):
        return self.title
