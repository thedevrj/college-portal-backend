from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    BoardOfManagementMember,
    BoardOfManagementMinutes,
    AcademicCouncilMember,
    AcademicCouncilMinutes,
    PlanningBoardMember,
    PlanningBoardMinutes,
    FinanceCommitteeMember,
    FinanceCommitteeMinutes,
)

import re
from datetime import datetime


# --- Robust Date Parser ---

def clean_and_parse_date(val):
    if val is None:
        return None

    # If it's already a date/datetime object from Excel
    if hasattr(val, "date"):
        return val.date()
    if isinstance(val, datetime):
        return val.date()

    val_str = str(val).strip()
    if val_str in ["", "-", "--", "n/a", "N/A", "none", "None", "None None"]:
        return None

    # Extract date pattern: DD.MM.YYYY or YYYY.MM.DD
    match = re.search(r"(\d{1,2}|\d{4})[./-](\d{1,2})[./-](\d{1,2}|\d{4})", val_str)
    if match:
        part1 = match.group(1)
        part2 = match.group(2)
        part3 = match.group(3)

        # Determine if it's YYYY-MM-DD or DD-MM-YYYY
        if len(part1) == 4:
            date_str = f"{part1}-{part2}-{part3}"
            fmt = "%Y-%m-%d"
        else:
            date_str = f"{part1}-{part2}-{part3}"
            fmt = "%d-%m-%Y"

        try:
            return datetime.strptime(date_str, fmt).date()
        except Exception:
            pass

    # Direct fallback parsing
    for fmt in ["%d.%m.%Y", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]:
        try:
            return datetime.strptime(val_str, fmt).date()
        except (ValueError, TypeError):
            continue

    return None


def clean_row_none_strings(row):
    for key in list(row.keys()):
        val = row[key]
        if val is not None and str(val).lower().strip() == "none":
            row[key] = None


# --- Resources for Import/Export ---

class BoardOfManagementMemberResource(resources.ModelResource):
    class Meta:
        model = BoardOfManagementMember
        fields = (
            "id",
            "provision",
            "name",
            "designation",
            "email",
            "phone_fax",
            "date_of_nomination",
            "date_of_expiry",
            "order",
        )
        export_order = fields

    def before_import_row(self, row, **kwargs):
        clean_row_none_strings(row)
        for date_field in ["date_of_nomination", "date_of_expiry"]:
            if date_field in row:
                row[date_field] = clean_and_parse_date(row[date_field])
        return super().before_import_row(row, **kwargs)


class BoardOfManagementMinutesResource(resources.ModelResource):
    class Meta:
        model = BoardOfManagementMinutes
        fields = ("id", "meeting_title", "date_of_meeting", "file")
        export_order = fields

    def before_import_row(self, row, **kwargs):
        clean_row_none_strings(row)
        if "date_of_meeting" in row:
            row["date_of_meeting"] = clean_and_parse_date(row["date_of_meeting"])
        return super().before_import_row(row, **kwargs)


class AcademicCouncilMemberResource(resources.ModelResource):
    class Meta:
        model = AcademicCouncilMember
        fields = ("id", "name", "designation", "institution", "contact", "email", "order")
        export_order = fields

    def before_import_row(self, row, **kwargs):
        clean_row_none_strings(row)
        return super().before_import_row(row, **kwargs)


class AcademicCouncilMinutesResource(resources.ModelResource):
    class Meta:
        model = AcademicCouncilMinutes
        fields = ("id", "meeting_title", "date_of_meeting", "file")
        export_order = fields

    def before_import_row(self, row, **kwargs):
        clean_row_none_strings(row)
        if "date_of_meeting" in row:
            row["date_of_meeting"] = clean_and_parse_date(row["date_of_meeting"])
        return super().before_import_row(row, **kwargs)


class PlanningBoardMemberResource(resources.ModelResource):
    class Meta:
        model = PlanningBoardMember
        fields = (
            "id",
            "provision",
            "name",
            "date_of_appointment",
            "date_of_expiry",
            "in_the_capacity_of",
            "order",
        )
        export_order = fields

    def before_import_row(self, row, **kwargs):
        clean_row_none_strings(row)
        for date_field in ["date_of_appointment", "date_of_expiry"]:
            if date_field in row:
                row[date_field] = clean_and_parse_date(row[date_field])
        return super().before_import_row(row, **kwargs)


class PlanningBoardMinutesResource(resources.ModelResource):
    class Meta:
        model = PlanningBoardMinutes
        fields = ("id", "meeting_title", "date_of_meeting", "file")
        export_order = fields

    def before_import_row(self, row, **kwargs):
        clean_row_none_strings(row)
        if "date_of_meeting" in row:
            row["date_of_meeting"] = clean_and_parse_date(row["date_of_meeting"])
        return super().before_import_row(row, **kwargs)


class FinanceCommitteeMemberResource(resources.ModelResource):
    class Meta:
        model = FinanceCommitteeMember
        fields = ("id", "name", "designation", "contact", "email", "order")
        export_order = fields

    def before_import_row(self, row, **kwargs):
        clean_row_none_strings(row)
        return super().before_import_row(row, **kwargs)


class FinanceCommitteeMinutesResource(resources.ModelResource):
    class Meta:
        model = FinanceCommitteeMinutes
        fields = ("id", "meeting_title", "date_of_meeting", "file")
        export_order = fields

    def before_import_row(self, row, **kwargs):
        clean_row_none_strings(row)
        if "date_of_meeting" in row:
            row["date_of_meeting"] = clean_and_parse_date(row["date_of_meeting"])
        return super().before_import_row(row, **kwargs)


# --- Admin Registrations ---

@admin.register(BoardOfManagementMember)
class BoardOfManagementMemberAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = BoardOfManagementMemberResource
    list_display = ("name", "designation", "provision", "email", "order")
    search_fields = ("name", "designation", "email")
    list_filter = ("provision",)


@admin.register(BoardOfManagementMinutes)
class BoardOfManagementMinutesAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = BoardOfManagementMinutesResource
    list_display = ("meeting_title", "date_of_meeting")
    search_fields = ("meeting_title",)
    list_filter = ("date_of_meeting",)


@admin.register(AcademicCouncilMember)
class AcademicCouncilMemberAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = AcademicCouncilMemberResource
    list_display = ("name", "designation", "institution", "contact", "email", "order")
    search_fields = ("name", "designation", "institution", "email")
    list_filter = ("institution",)


@admin.register(AcademicCouncilMinutes)
class AcademicCouncilMinutesAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = AcademicCouncilMinutesResource
    list_display = ("meeting_title", "date_of_meeting")
    search_fields = ("meeting_title",)
    list_filter = ("date_of_meeting",)


@admin.register(PlanningBoardMember)
class PlanningBoardMemberAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = PlanningBoardMemberResource
    list_display = ("name", "in_the_capacity_of", "provision", "date_of_appointment", "order")
    search_fields = ("name", "in_the_capacity_of")
    list_filter = ("provision",)


@admin.register(PlanningBoardMinutes)
class PlanningBoardMinutesAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = PlanningBoardMinutesResource
    list_display = ("meeting_title", "date_of_meeting")
    search_fields = ("meeting_title",)
    list_filter = ("date_of_meeting",)


@admin.register(FinanceCommitteeMember)
class FinanceCommitteeMemberAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = FinanceCommitteeMemberResource
    list_display = ("name", "designation", "contact", "email", "order")
    search_fields = ("name", "designation", "email")


@admin.register(FinanceCommitteeMinutes)
class FinanceCommitteeMinutesAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = FinanceCommitteeMinutesResource
    list_display = ("meeting_title", "date_of_meeting")
    search_fields = ("meeting_title",)
    list_filter = ("date_of_meeting",)
