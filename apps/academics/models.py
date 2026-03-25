from django.db import models
from django.utils.text import slugify

class School(models.Model):

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to="schools/",blank=True,null=True)
    about_school = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # enforce DB length safety
        self.slug = self.slug[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Department(models.Model):

    school = models.ForeignKey(
        School,
        related_name="departments",
        on_delete=models.CASCADE
    )
      
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True,null = True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # enforce DB length safety
        self.slug = self.slug[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name