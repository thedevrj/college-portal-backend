from django.db import models
from django.utils.text import slugify
from simple_history.models import HistoricalRecords
from apps.accounts.models import SoftDeleteModel
from ckeditor.fields import RichTextField


class Centre(SoftDeleteModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    school = models.ForeignKey(
        "academics.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="centres",
    )

    HEAD_TITLE_CHOICES = [
        ("Director", "Director"),
        ("In-Charge", "In-Charge"),
        ("Coordinator", "Coordinator"),
        ("Others", "Others"),
    ]
    head = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_centres",
        verbose_name="Leadership",
    )
    head_title = models.CharField(
        max_length=50,
        choices=HEAD_TITLE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Leadership Title",
    )
    head_title_other = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Provide the title if 'Others' is selected",
        verbose_name="Other Leadership Title",
    )

    class Meta:
        ordering = ["name"]

    description = models.TextField(blank=True, null=True)
    about = RichTextField(blank=True, null=True)
    thrust_areas = RichTextField(
        blank=True,
        null=True,
        help_text="Major research and academic focus areas of the centre",
    )
    history = HistoricalRecords()

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError

        if self.head_title == "Others" and not self.head_title_other:
            raise ValidationError(
                {
                    "head_title_other": "This field is required when Leadership Title is 'Others'."
                }
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        # enforce DB length safety
        self.slug = self.slug[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
