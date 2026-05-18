from django.db import models
from apps.accounts.models import SoftDeleteModel
from simple_history.models import HistoricalRecords


# --- Board of Management (BoM) ---

class BoardOfManagementMember(SoftDeleteModel):
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
        return f"{self.name} - BoM"

    @property
    def parsed_phones(self):
        if not self.phone_fax:
            return []
        parsed = []
        parts = self.phone_fax.split(",")
        for part in parts:
            part = part.strip()
            if not part:
                continue
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
        verbose_name_plural = "Board of Management Members"


class BoardOfManagementMinutes(SoftDeleteModel):
    meeting_title = models.CharField(max_length=255)
    date_of_meeting = models.DateField()
    file = models.FileField(upload_to="board_of_management/minutes/")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.meeting_title} ({self.date_of_meeting})"

    class Meta:
        ordering = ["-date_of_meeting"]
        verbose_name_plural = "Board of Management Minutes"


# --- Academic Council ---

class AcademicCouncilMember(SoftDeleteModel):
    name = models.CharField(max_length=255, verbose_name="Name of the Member")
    designation = models.CharField(max_length=255, blank=True, null=True)
    institution = models.CharField(
        max_length=255, blank=True, null=True, help_text="University or organization details"
    )
    contact = models.CharField(
        max_length=255, blank=True, null=True, help_text="Phone numbers"
    )
    email = models.EmailField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="For S.No sorting")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} - Academic Council"

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Academic Council Members"


class AcademicCouncilMinutes(SoftDeleteModel):
    meeting_title = models.CharField(max_length=255)
    date_of_meeting = models.DateField()
    file = models.FileField(upload_to="academic_council/minutes/")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.meeting_title} ({self.date_of_meeting})"

    class Meta:
        ordering = ["-date_of_meeting"]
        verbose_name_plural = "Academic Council Minutes"


# --- Planning Board ---

class PlanningBoardMember(SoftDeleteModel):
    provision = models.CharField(
        max_length=255, blank=True, null=True, help_text="e.g., 11(1)(i)"
    )
    name = models.CharField(max_length=255, verbose_name="Name of the Member")
    date_of_appointment = models.DateField(
        blank=True, null=True, verbose_name="Date of Appointment"
    )
    date_of_expiry = models.DateField(blank=True, null=True)
    in_the_capacity_of = models.CharField(
        max_length=255, blank=True, null=True, help_text="e.g., Chairman"
    )
    order = models.PositiveIntegerField(default=0, help_text="For S.No sorting")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} - Planning Board"

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Planning Board Members"


class PlanningBoardMinutes(SoftDeleteModel):
    meeting_title = models.CharField(max_length=255)
    date_of_meeting = models.DateField()
    file = models.FileField(upload_to="planning_board/minutes/")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.meeting_title} ({self.date_of_meeting})"

    class Meta:
        ordering = ["-date_of_meeting"]
        verbose_name_plural = "Planning Board Minutes"


# --- Finance Committee ---

class FinanceCommitteeMember(SoftDeleteModel):
    name = models.CharField(max_length=255, verbose_name="Name of the Member")
    designation = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(
        max_length=255, blank=True, null=True, help_text="Phone numbers"
    )
    email = models.EmailField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="For S.No sorting")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} - Finance Committee"

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Finance Committee Members"


class FinanceCommitteeMinutes(SoftDeleteModel):
    meeting_title = models.CharField(max_length=255)
    date_of_meeting = models.DateField()
    file = models.FileField(upload_to="finance_committee/minutes/")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.meeting_title} ({self.date_of_meeting})"

    class Meta:
        ordering = ["-date_of_meeting"]
        verbose_name_plural = "Finance Committee Minutes"
