from django.db import models
from django.contrib.postgres.fields import ArrayField


class GlobalNotice(models.Model):
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
    date_posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_posted"]
        verbose_name_plural = "General Notices"

    def __str__(self):
        cats = ", ".join(self.categories) if self.categories else "Uncategorized"
        return f"[{cats}] {self.title}"
