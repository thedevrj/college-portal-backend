from django.db import models
from django.core.exceptions import ValidationError
from apps.accounts.models import SoftDeleteModel
from simple_history.models import HistoricalRecords
from ckeditor.fields import RichTextField


class CourseLevel(models.TextChoices):
    UG = "UG", "Undergraduate"
    PG = "PG", "Postgraduate"


class FoundationCourse(SoftDeleteModel):
    level = models.CharField(
        max_length=10, choices=CourseLevel.choices, verbose_name="Course Level"
    )
    semester = models.PositiveIntegerField(
        help_text="e.g., 1, 2, 3, 4...", verbose_name="Semester"
    )
    course_code = models.CharField(max_length=100, verbose_name="Course/Paper Code")
    course_title = models.CharField(max_length=255, verbose_name="Course Title")
    credits = models.PositiveIntegerField(default=0, verbose_name="Credits")
    syllabus_file = models.FileField(
        upload_to="foundation_courses/syllabus/",
        blank=True,
        null=True,
        verbose_name="Syllabus File",
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ["level", "semester", "course_code"]
        verbose_name = "Foundation Course"
        verbose_name_plural = "Foundation Courses"
        constraints = [
            models.UniqueConstraint(
                fields=["course_code"],
                condition=models.Q(is_deleted=False),
                name="unique_foundation_course_code",
            )
        ]

    def clean(self):
        super().clean()
        if self.semester < 1:
            raise ValidationError(
                {"semester": "Semester must be a positive integer starting from 1."}
            )

        # Check uniqueness manually in clean for admin form validation
        qs = FoundationCourse.objects.filter(
            course_code__iexact=self.course_code,
            is_deleted=False,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(
                {
                    "course_code": f"A Foundation Course with Course Code '{self.course_code}' already exists."
                }
            )

    def __str__(self):
        return f"[{self.level} - Sem {self.semester}] {self.course_code} - {self.course_title}"


class FoundationCourseMaterial(SoftDeleteModel):
    MATERIAL_TYPE_CHOICES = [
        ("Document", "Document/PDF"),
        ("Video", "Video Lecture"),
        ("Link", "External Link/Reference"),
        ("Others", "Others"),
    ]
    course = models.ForeignKey(
        FoundationCourse,
        on_delete=models.CASCADE,
        related_name="materials",
        verbose_name="Course",
    )
    title = models.CharField(max_length=255, verbose_name="Material Title")
    material_type = models.CharField(
        max_length=50,
        choices=MATERIAL_TYPE_CHOICES,
        default="Document",
        verbose_name="Material Type",
    )
    file = models.FileField(
        upload_to="foundation_courses/materials/",
        blank=True,
        null=True,
        verbose_name="File Attachment",
    )
    link = models.URLField(blank=True, null=True, verbose_name="External Link")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded At")
    history = HistoricalRecords()

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Foundation Course Material"
        verbose_name_plural = "Foundation Course Materials"

    def clean(self):
        super().clean()
        if not self.file and not self.link:
            raise ValidationError(
                "Either a file attachment or an external link must be provided."
            )

    def __str__(self):
        return f"{self.title} ({self.course.course_title})"
