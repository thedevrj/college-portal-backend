from re import VERBOSE
from django.db import models
from apps.accounts.models import SoftDeleteModel
from simple_history.models import HistoricalRecords


class AuthorityType(models.TextChoices):
    ACADEMIC_COUNCIL = "ACADEMIC_COUNCIL", "Academic Council"
    BOARD_OF_MANAGEMENT = "BOARD_OF_MANAGEMENT", "Board of Management"
    PLANNING_BOARD = "PLANNING_BOARD", "Planning Board"
    FINANCE_COMMITTEE = "FINANCE_COMMITTEE", "Finance Committee"


class Authority(SoftDeleteModel):
    name = models.CharField(max_length=100, choices=AuthorityType.choices, unique=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name_plural = "Authorities"


class AuthorityMember(SoftDeleteModel):
    authority = models.ForeignKey(
        Authority, on_delete=models.CASCADE, related_name="members"
    )
    provision = models.CharField(
        max_length=255, blank=True, null=True, help_text="e.g., 11(1)(i)"
    )
    name = models.CharField(max_length=255, verbose_name="Name of the Member")
    designation = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_fax = models.TextField(
        blank=True, null=True, help_text="Multiple numbers allowed"
    )
    date_of_nomination = models.DateField(
        blank=True, null=True, verbose_name="Date of Nomination/Appointment"
    )
    date_of_expiry = models.DateField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="For S.No sorting")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} - {self.authority.get_name_display()}"

    @property
    def parsed_phones(self):
        if not self.phone_fax:
            return []
        parsed = []
        # Split by comma
        parts = self.phone_fax.split(",")
        for part in parts:
            part = part.strip()
            if not part:
                continue
            # Find parenthesis for labels like (O) or (Fax)
            if "(" in part and ")" in part:
                try:
                    num, rest = part.split("(", 1)
                    label = rest.split(")", 1)[0]
                    parsed.append({
                        "number": num.strip(),
                        "label": f"({label.strip()})"
                    })
                except Exception:
                    parsed.append({
                        "number": part,
                        "label": ""
                    })
            else:
                # Check if there is space
                subparts = part.split(None, 1)
                if len(subparts) == 2:
                    parsed.append({
                        "number": subparts[0].strip(),
                        "label": subparts[1].strip()
                    })
                else:
                    parsed.append({
                        "number": part,
                        "label": ""
                    })
        return parsed

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Authority Members"


class AuthorityMinutes(SoftDeleteModel):
    authority = models.ForeignKey(
        Authority, on_delete=models.CASCADE, related_name="minutes"
    )
    meeting_title = models.CharField(max_length=255)
    date_of_meeting = models.DateField()
    file = models.FileField(upload_to="authorities/minutes/")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.meeting_title} ({self.date_of_meeting})"

    class Meta:
        ordering = ["-date_of_meeting"]
        verbose_name_plural = "Authority Minutes"
