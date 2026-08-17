from django.db import models
from django.contrib.auth import get_user_model
from apps.accounts.models import SoftDeleteModel
from django.core.exceptions import ValidationError
import uuid

User = get_user_model()


class Complaint(SoftDeleteModel):
    CATEGORY_CHOICES = [
        ("corruption", "Corruption"),
        ("malpractice", "Malpractice"),
        ("procedural_lapse", "Procedural Lapse"),
        ("Others", "Others"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("under_investigation", "Under Investigation"),
        ("resolved", "Resolved"),
        ("forwarded", "Forwarded to Higher Authorities"),
        ("dismissed", "Dismissed"),
        ("Others", "Others"),
    ]

    tracking_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="other"
    )
    description = models.TextField()

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    others_status = models.CharField(max_length=30, blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            (
                "manage_complaints",
                "Can view and update vigilance complaint case statuses through the API",
            ),
        ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.tracking_id:
            # Generate a sequential, trackable ID
            month_str = self.submitted_at.strftime("%Y%m")
            self.tracking_id = f"VIG-{month_str}-{self.id:04d}"
            self.save(update_fields=["tracking_id"])

        if self.status == "Others" and not self.others_status:
            raise ValidationError(
                {"others_status": "This field is required when category is 'Others'."}
            )

    def __str__(self):
        return f"{self.tracking_id} - {self.get_status_display()}"


class ComplaintAttachment(SoftDeleteModel):
    complaint = models.ForeignKey(
        Complaint, related_name="attachments", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="vigilance_attachments/%Y/%m/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.complaint.tracking_id}"


class FAQ(SoftDeleteModel):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.IntegerField(
        default=0, help_text="Order in which FAQ should be displayed"
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.question


class PolicyDocument(SoftDeleteModel):
    DOC_TYPES = [
        ("policy", "Policy"),
        ("sop", "SOP"),
        ("report", "Annual / Periodic Report"),
    ]
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOC_TYPES)
    file = models.FileField(upload_to="vigilance_documents/%Y/%m/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ComplaintActionLog(SoftDeleteModel):
    complaint = models.ForeignKey(
        Complaint, related_name="action_logs", on_delete=models.CASCADE
    )
    action_taken_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    action_description = models.CharField()
    status_changed_to = models.CharField(
        max_length=30, choices=Complaint.STATUS_CHOICES, blank=True, null=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.complaint.tracking_id} at {self.timestamp}"
