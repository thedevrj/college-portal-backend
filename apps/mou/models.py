from django.db import models
from django.core.exceptions import ValidationError
from apps.accounts.models import SoftDeleteModel
from simple_history.models import HistoricalRecords


class MOU(SoftDeleteModel):
    partner_name = models.CharField(
        max_length=255, verbose_name="Partner/Organization Name"
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
    history = HistoricalRecords()

    class Meta:
        verbose_name = "MOU"
        verbose_name_plural = "MOUs"
        ordering = ["-date_of_signing"]
        constraints = [
            models.UniqueConstraint(
                fields=["partner_name", "date_of_signing"],
                condition=models.Q(is_deleted=False),
                name="unique_mou_partner_date",
            )
        ]

    def clean(self):
        super().clean()
        if self.description:
            word_count = len(self.description.split())
            if word_count > 250:
                raise ValidationError(
                    {
                        "description": f"Description should be around 200 words. Currently it has {word_count} words."
                    }
                )

        # Date validation
        if self.date_of_signing and self.valid_till:
            if self.valid_till < self.date_of_signing:
                raise ValidationError(
                    {"valid_till": "Expiry date cannot be before the date of signing."}
                )

        # Duplicate check logic
        qs = MOU.objects.filter(
            partner_name__iexact=self.partner_name,
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
        return self.partner_name
