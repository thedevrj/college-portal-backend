from django.db import models
from apps.accounts.models import SoftDeleteModel
from simple_history.models import HistoricalRecords


class ProctorialBoardMember(SoftDeleteModel):
    choice = (
        ("Proctor", "Proctor"),
        ("Additional Proctor", "Additional Proctor"),
        ("Dy. Proctor", "Depty Proctor"),
        ("Asst. Proctor", "Assistant Proctor"),
        ("Asst. Proctor & Convener", "Assistant Proctor & Convener"),
        ("Others", "Others"),
    )
    name = models.CharField(max_length=255, verbose_name="Name of the Member")
    designation = models.CharField(max_length=255, blank=True, null=True)
    in_the_capacity_of = models.CharField(
        max_length=255, choices=choice, null=True, blank=True
    )
    others_in_the_capacity_of = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(
        max_length=255, blank=True, null=True, help_text="Phone numbers"
    )
    email_id = models.EmailField(blank=True, null=True)
    notification = models.FileField(
        upload_to="proctorial_board/notifications/", null=True, blank=True
    )
    order = models.PositiveIntegerField(default=0, help_text="For S.No sorting")
    history = HistoricalRecords()

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        from django.core.validators import validate_email

        if self.email_id:
            val = str(self.email_id).strip().lower()
            try:
                validate_email(val)
            except ValidationError:
                raise ValidationError(
                    {"email_id": "Please enter a valid email address."}
                )
            self.email_id = val

        if self.in_the_capacity_of == "Others" and not self.others_in_the_capacity_of:
            raise ValidationError(
                {
                    "others_in_the_capacity_of": "This field is required when 'Others' is selected."
                }
            )

    def __str__(self):
        return f"{self.name} - Proctorial Board"

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Proctorial Board Members"


class ProctorialBoardMinutes(SoftDeleteModel):
    meeting_title = models.CharField(max_length=255)
    date_of_meeting = models.DateField()
    file = models.FileField(upload_to="proctorial_board/minutes/")

    is_archived = models.BooleanField(
        default=False,
        help_text="Tick if want to add into archive.",
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
        verbose_name_plural = "Proctorial Board Minutes"


class ProctorialBoardNotice(SoftDeleteModel):
    title = models.CharField(max_length=255)
    date = models.DateField()
    file = models.FileField(upload_to="proctorial_board/notices/")

    is_archived = models.BooleanField(
        default=False,
        help_text="Tick if want to add into archive.",
    )
    archive_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date after which this automatically becomes archived.",
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.title} ({self.date})"

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Proctorial Board Notices & Circulars"
