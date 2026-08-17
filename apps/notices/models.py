from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from simple_history.models import HistoricalRecords
from apps.accounts.models import SoftDeleteModel


class GlobalNotice(SoftDeleteModel):
    CATEGORY_CHOICES = [
        ("Announcement", "Announcement"),
        ("Event", "Event"),
        ("Appointment", "Appointment"),
        ("Tenders", "Tenders"),
    ]

    title = models.CharField(max_length=500)
    categories = ArrayField(
        models.CharField(max_length=50, choices=CATEGORY_CHOICES),
        blank=True,
        default=list,
        help_text="Select one or more categories",
    )
    link = models.URLField(
        blank=True, null=True, help_text="Optional external link or relative URL"
    )
    attachment = models.FileField(upload_to="global_notices/", blank=True, null=True)
    date_posted = models.DateField()
    show_in_marquee = models.BooleanField(
        default=False,
        help_text="Show this notice in the scrolling marquee at the top of the homepage",
    )
    is_private = models.BooleanField(
        default=False,
        help_text="If checked, this notice will only be visible to logged-in faculty/staff.",
    )
    posted_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notices_posted",
    )

    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(
        default=False,
        help_text="Manually archive this notice immediately.",
    )
    archive_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date after which this notice automatically becomes archived.",
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ["-date_posted"]
        verbose_name_plural = "General Notices"

    def clean(self):
        super().clean()
        # Validate that every category value is a valid choice
        valid_categories = {c[0] for c in self.CATEGORY_CHOICES}
        invalid = [c for c in (self.categories or []) if c not in valid_categories]
        if invalid:
            raise ValidationError(
                {
                    "categories": f"Invalid category value(s): {', '.join(invalid)}. Must be one of: {', '.join(valid_categories)}."
                }
            )
        # Require at least a link or attachment so the notice is useful
        if not self.link and not self.attachment:
            raise ValidationError(
                "A notice must have either an external link or a file attachment to be useful."
            )

    def __str__(self):
        cats = ", ".join(self.categories) if self.categories else "Uncategorized"
        return f"[{cats}] {self.title}"
