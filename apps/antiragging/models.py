from django.db import models
from apps.accounts.models import SoftDeleteModel
from simple_history.models import HistoricalRecords


class ResourceCategory(models.TextChoices):
    UGC_REGULATIONS = "ugc_regulations", "UGC Regulations"
    UNIVERSITY_POLICY = "university_policy", "University Policy"
    AWARENESS_MATERIAL = "awareness_material", "Awareness Material"
    ANNUAL_REPORT = "annual_report", "Annual Compliance Report"
    HOSTEL_SAFETY = "hostel_safety", "Hostel Safety"


class Resource(SoftDeleteModel):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=32, choices=ResourceCategory.choices)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="antiragging/resources/")
    published_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-published_on"]

    def __str__(self):
        return self.title


class CommitteeType(models.TextChoices):
    ANTI_RAGGING_COMMITTEE = "committee", "Anti-Ragging Committee"
    ANTI_RAGGING_SQUAD = "squad", "Anti-Ragging Squad"


class CommitteeMember(SoftDeleteModel):
    designation_choices = [
        ("", "Select Designation"),
        ("CHAIRPERSON", "Chairperson"),
        ("MEMBER","Member"),
        ("MEMBER_CONVENER","Member & Convener")
    ]
    faculty = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="antiragging_committee_members",
        verbose_name="Committee Member",
    )
    designation = models.CharField(max_length=150, choices=designation_choices)
    committee_type = models.CharField(max_length=16, choices=CommitteeType.choices)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    history = HistoricalRecords()

    class Meta:
        ordering = ["committee_type", "display_order"]

    def __str__(self):
        faculty_name = self.faculty.name if self.faculty else "Unknown Faculty"
        return f"{faculty_name} ({self.get_committee_type_display()})"


class FAQ(SoftDeleteModel):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "Anti-Ragging FAQ"
        verbose_name_plural = "Anti-Ragging FAQs"

    def __str__(self):
        return self.question


class EmergencyContact(SoftDeleteModel):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    available_hours = models.CharField(max_length=100, blank=True, help_text="e.g. 24x7 or 9:00 AM - 5:00 PM")
    display_order = models.PositiveIntegerField(default=0)
    history = HistoricalRecords()

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return f"{self.name} - {self.role}"
