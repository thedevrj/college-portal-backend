from django.db import models
from apps.accounts.models import SoftDeleteModel
from simple_history.models import HistoricalRecords


class PlacementNotice(SoftDeleteModel):
    title = models.CharField(max_length=255, verbose_name="Notice Title")
    date = models.DateField()
    file = models.FileField(upload_to="placement/notices/%Y/%m/")

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
        verbose_name_plural = "Placements Notifications"


