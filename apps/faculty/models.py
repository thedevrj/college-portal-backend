from django.db import models
from django.utils.text import slugify


class Faculty(models.Model):

    employee_id = models.CharField(
        max_length=50,
        unique=True
    )

    staff_no = models.PositiveIntegerField(
        unique=True,
        null=True,
        blank=True
    )
    photo = models.ImageField(upload_to="faculty/",null=True,blank=True)
    photo_alt_text = models.CharField(max_length=255, blank=True, help_text="GIGW accessibility text for the image")
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)


    roles = models.JSONField(default=list, blank=True)

    slug = models.SlugField(max_length=255,unique=True,blank=True)

    school = models.ForeignKey(
        "academics.School",
        related_name="faculty",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    department = models.ForeignKey(
        "academics.Department",
        related_name="faculty",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    centre = models.ForeignKey(
        "centres.Centre",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculty"
    )
    
    insti_email = models.EmailField(blank=True)
    other_email = models.EmailField(blank=True)
    phone1 = models.CharField(max_length=20,blank=True)
    phone2 = models.CharField(max_length=20,blank=True)

    research_int = models. TextField(blank=True)   

    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        ordering = ["name"]

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        self.slug = self.slug[:255]

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"