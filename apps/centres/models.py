from django.db import models
from django.utils.text import slugify


class Centre(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    school = models.ForeignKey(
        "academics.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='centres'
    )
    class Meta:
        ordering = ["name"]

    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # enforce DB length safety
        self.slug = self.slug[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
