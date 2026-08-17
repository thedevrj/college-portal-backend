from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.accounts.models import SoftDeleteModel
from simple_history.models import HistoricalRecords


class MOU(SoftDeleteModel):
    Nature_choice = [
        ("Central University", "Central University"),
        ("State University", "State University"),
        ("Centre", "Centre"),
        ("Institution/Deemed University", "Institution/Deemed University"),
        ("Research Organisation", "Research Organisation"),
        ("Govt Department", "Govt Department"),
        ("Others", "Others"),
    ]
    organization_name = models.CharField(
        max_length=255, verbose_name="Partner/Organization Name"
    )
    Nature_of_organization = models.CharField(
        max_length=50, choices=Nature_choice, null=True, blank=True
    )
    other_nature_of_organization = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Other Nature of Organization",
        help_text="Please specify if 'Others' is selected",
    )

    date_of_signing = models.DateField(
        verbose_name="Date of Signing", null=True, blank=True
    )
    valid_till = models.DateField(
        verbose_name="Valid Till / Expiry Date", null=True, blank=True
    )
    description = models.TextField(
        help_text="Brief description (approx 200 words)", null=True, blank=True
    )
    document = models.FileField(
        upload_to="mou_documents/", null=True, blank=True, verbose_name="MOU Document"
    )
    is_archived = models.BooleanField(
        default=False,
        help_text="Manually archive this MOU.",
    )
    archive_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date after which this MOU automatically becomes archived.",
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "MOU"
        verbose_name_plural = "MOUs"
        ordering = ["-date_of_signing"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization_name", "date_of_signing"],
                condition=models.Q(is_deleted=False),
                name="unique_mou_partner_date",
            )
        ]

    def clean(self):
        super().clean()
        
        if self.Nature_of_organization == "Others" and not self.other_nature_of_organization:
            raise ValidationError(
                {"other_nature_of_organization": "This field is required when Nature of Organization is 'Others'."}
            )

        if self.description:
            word_count = len(self.description.split())
            if word_count > 250:
                raise ValidationError(
                    {
                        "description": f"Description should be around 200 words. Currently it has {word_count} words."
                    }
                )

        # Date validation
        if self.date_of_signing and self.date_of_signing > timezone.now().date():
            raise ValidationError(
                {"date_of_signing": "Date of signing cannot be in the future."}
            )

        if self.date_of_signing and self.valid_till:
            if self.valid_till < self.date_of_signing:
                raise ValidationError(
                    {"valid_till": "Expiry date cannot be before the date of signing."}
                )

        # Duplicate check logic
        qs = MOU.objects.filter(
            organization_name__iexact=self.organization_name,
            date_of_signing=self.date_of_signing,
            is_deleted=False,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(
                "An MOU with the same Partner Name and Date of Signing already exists."
            )

    def __str__(self):
        return self.organization_name
