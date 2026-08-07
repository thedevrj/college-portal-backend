from django.db import models
from apps.accounts.models import SoftDeleteModel
from simple_history.models import HistoricalRecords


class COENotice(SoftDeleteModel):
    title = models.CharField(max_length=255, verbose_name="Notice Title")
    date = models.DateField()
    file = models.FileField(upload_to="coe/notices/")

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
        verbose_name_plural = "COE Notices & Circulars"


class PHDVivaVoceDate(SoftDeleteModel):
    title = models.CharField(max_length=255, verbose_name="Title")
    date = models.DateField()
    file = models.FileField(upload_to="coe/phd_viva_voce_dates/")

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
        verbose_name_plural = "PhD Viva Voce Dates"


class MPHILVivaVoceDate(SoftDeleteModel):
    title = models.CharField(max_length=255, verbose_name="Title")
    date = models.DateField()
    file = models.FileField(upload_to="coe/mphil_viva_voce_dates/")

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
        verbose_name_plural = "MPhil Viva Voce Dates"


class PHDPreSubmissionSeminar(SoftDeleteModel):
    title = models.CharField(max_length=255, verbose_name="Title")
    date = models.DateField()
    file = models.FileField(upload_to="coe/phd_pre_submission_seminars/")

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
        verbose_name_plural = "PhD Pre-Submission Seminar Dates"


class RDCUNotice(SoftDeleteModel):
    title = models.CharField(max_length=255, verbose_name="Notice Title")
    date = models.DateField()
    file = models.FileField(upload_to="coe/rdc_notices/")

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
        verbose_name_plural = "RDC Notices"
