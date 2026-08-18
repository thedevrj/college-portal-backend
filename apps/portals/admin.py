from django.contrib import admin
from django import forms
from django.db import models
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.mixins import PortalSecurityMixin
from .models import (
    Grievance,
    GrievanceAttachment,
    GrievanceSignature,
    GrievanceActionLog,
    ICCComplaint,
    ICCAttachment,
    ICCSignature,
    ICCActionLog,
    DiscriminationComplaint,
    DiscriminationAttachment,
    DiscriminationSignature,
    DiscriminationActionLog,
    StudentFeedback,
    FeedbackAttachment,
    FeedbackSignature,
    FeedbackActionLog,
)


class GrievanceAttachmentInline(admin.TabularInline):
    model = GrievanceAttachment
    extra = 0
    readonly_fields = ["file", "uploaded_at"]
    exclude = ["is_deleted", "deleted_at"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class GrievanceSignatureInline(admin.TabularInline):
    model = GrievanceSignature
    extra = 0
    readonly_fields = ["image", "uploaded_at"]
    exclude = ["is_deleted", "deleted_at"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class GrievanceActionLogInline(admin.TabularInline):
    model = GrievanceActionLog
    extra = 0
    readonly_fields = [
        "action_taken_by",
        "status_changed_to",
        "timestamp",
    ]
    exclude = ["is_deleted", "deleted_at"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Grievance)
class GrievanceAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = (
        "tracking_id",
        "name_of_complainant",
        "nature_of_grievance",
        "complainant_type",
        "status",
        "submitted_at",
    )
    list_filter = (
        "status",
        "nature_of_grievance",
        "complainant_type",
        "gender",
        "submitted_at",
    )
    search_fields = (
        "tracking_id",
        "name_of_complainant",
        "email",
        "contact_number",
        "enrollment_id",
    )
    readonly_fields = ("tracking_id", "submitted_at", "updated_at")
    inlines = [
        GrievanceAttachmentInline,
        GrievanceSignatureInline,
        GrievanceActionLogInline,
    ]
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }

    fieldsets = (
        (
            "Tracking",
            {
                "fields": ("tracking_id", "status"),
            },
        ),
        (
            "Classification",
            {
                "fields": (
                    "nature_of_grievance",
                    "others_nature_of_grievance",
                    "complainant_type",
                    "others_complainant_type",
                ),
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "name_of_complainant",
                    "aadhaar_number",
                    "enrollment_id",
                    "date_of_birth",
                    "gender",
                    "fathers_name",
                    "mothers_name",
                ),
            },
        ),
        (
            "Address & Contact",
            {
                "fields": (
                    "permanent_address",
                    "state",
                    "city",
                    "pincode",
                    "contact_number",
                    "email",
                ),
            },
        ),
        (
            "Grievance",
            {
                "fields": ("complaint_text", "declaration_accepted"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("submitted_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        """
        All submitted grievance data is immutable — only status can be changed
        by the officer from the admin panel.
        """
        if obj:
            return (
                "tracking_id",
                "submitted_at",
                "updated_at",
                "nature_of_grievance",
                "others_nature_of_grievance",
                "complainant_type",
                "others_complainant_type",
                "name_of_complainant",
                "aadhaar_number",
                "enrollment_id",
                "date_of_birth",
                "gender",
                "fathers_name",
                "mothers_name",
                "permanent_address",
                "state",
                "city",
                "pincode",
                "contact_number",
                "email",
                "complaint_text",
                "declaration_accepted",
            )
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_obj = Grievance.objects.get(pk=obj.pk)
                if old_obj.status != obj.status:
                    GrievanceActionLog.objects.create(
                        grievance=obj,
                        action_taken_by=request.user,
                        action_description=(
                            f"Status updated from '{old_obj.get_status_display()}' "
                            f"to '{obj.get_status_display()}'"
                        ),
                        status_changed_to=obj.status,
                    )
            except Grievance.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)


# ─────────────────────────────────────────────────────────────────────────────
# Internal Complaints Committee (ICC) Admin
# ─────────────────────────────────────────────────────────────────────────────


class ICCAttachmentInline(admin.TabularInline):
    model = ICCAttachment
    extra = 0
    readonly_fields = ["file", "uploaded_at"]
    exclude = ("is_deleted", "deleted_at")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ICCSignatureInline(admin.TabularInline):
    model = ICCSignature
    extra = 0
    exclude = ("is_deleted", "deleted_at")
    readonly_fields = ["image", "uploaded_at"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ICCActionLogInline(admin.TabularInline):
    model = ICCActionLog
    extra = 0
    readonly_fields = [
        "action_taken_by",
        "status_changed_to",
        "timestamp",
    ]
    exclude = ("is_deleted", "deleted_at")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ICCComplaint)
class ICCComplaintAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = (
        "tracking_id",
        "name_of_complainant",
        "nature_of_grievance",
        "status",
        "submitted_at",
    )
    list_filter = (
        "status",
        "nature_of_grievance",
        "gender",
        "submitted_at",
    )
    search_fields = (
        "tracking_id",
        "name_of_complainant",
        "email",
        "contact_number",
        "enrollment_id",
    )
    readonly_fields = ("tracking_id", "submitted_at", "updated_at")
    exclude = ("is_deleted", "deleted_at")
    inlines = [
        ICCAttachmentInline,
        ICCSignatureInline,
        ICCActionLogInline,
    ]
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }

    fieldsets = (
        (
            "Tracking",
            {
                "fields": ("tracking_id", "status"),
            },
        ),
        (
            "Classification",
            {
                "fields": (
                    "nature_of_grievance",
                    "others_nature_of_grievance",
                ),
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "name_of_complainant",
                    "aadhaar_number",
                    "enrollment_id",
                    "date_of_birth",
                    "gender",
                    "fathers_name",
                    "mothers_name",
                ),
            },
        ),
        (
            "Address & Contact",
            {
                "fields": (
                    "permanent_address",
                    "state",
                    "city",
                    "pincode",
                    "contact_number",
                    "email",
                ),
            },
        ),
        (
            "Complaint Details",
            {
                "fields": ("complaint_text", "declaration_accepted"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("submitted_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (
                "tracking_id",
                "submitted_at",
                "updated_at",
                "nature_of_grievance",
                "others_nature_of_grievance",
                "name_of_complainant",
                "aadhaar_number",
                "enrollment_id",
                "date_of_birth",
                "gender",
                "fathers_name",
                "mothers_name",
                "permanent_address",
                "state",
                "city",
                "pincode",
                "contact_number",
                "email",
                "complaint_text",
                "declaration_accepted",
            )
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_obj = ICCComplaint.objects.get(pk=obj.pk)
                if old_obj.status != obj.status:
                    ICCActionLog.objects.create(
                        complaint=obj,
                        action_taken_by=request.user,
                        action_description=(
                            f"Status updated from '{old_obj.get_status_display()}' "
                            f"to '{obj.get_status_display()}'"
                        ),
                        status_changed_to=obj.status,
                    )
            except ICCComplaint.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)


# ─────────────────────────────────────────────────────────────────────────────
# SC/ST, OBC, Disable & Minority Discrimination Admin
# ─────────────────────────────────────────────────────────────────────────────


class DiscriminationAttachmentInline(admin.TabularInline):
    model = DiscriminationAttachment
    extra = 0
    readonly_fields = ["file", "uploaded_at"]
    exclude = ("is_deleted", "deleted_at")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class DiscriminationSignatureInline(admin.TabularInline):
    model = DiscriminationSignature
    extra = 0
    readonly_fields = ["image", "uploaded_at"]
    exclude = ("is_deleted", "deleted_at")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class DiscriminationActionLogInline(admin.TabularInline):
    model = DiscriminationActionLog
    extra = 0
    readonly_fields = [
        "action_taken_by",
        "status_changed_to",
        "timestamp",
    ]
    exclude = ("is_deleted", "deleted_at")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DiscriminationComplaint)
class DiscriminationComplaintAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = (
        "tracking_id",
        "full_name",
        "complaint_discrimination",
        "status",
        "submitted_at",
    )
    list_filter = (
        "status",
        "complaint_discrimination",
        "gender",
        "category_belonging",
        "submitted_at",
    )
    search_fields = (
        "tracking_id",
        "full_name",
        "email",
        "contact_number",
        "enrollment_id",
        "roll_no",
    )
    readonly_fields = ("tracking_id", "submitted_at", "updated_at")
    inlines = [
        DiscriminationAttachmentInline,
        DiscriminationSignatureInline,
        DiscriminationActionLogInline,
    ]
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }

    fieldsets = (
        (
            "Tracking",
            {
                "fields": ("tracking_id", "status"),
            },
        ),
        (
            "Complaint Details",
            {
                "fields": (
                    "complaint_discrimination",
                    "others_complaint_discrimination",
                    "complaint_text",
                    "declaration_accepted",
                ),
            },
        ),
        (
            "University Details",
            {
                "fields": (
                    "enrollment_id",
                    "roll_no",
                    "school_name",
                    "department_name",
                    "course_name",
                ),
            },
        ),
        (
            "Basic Details",
            {
                "fields": (
                    "full_name",
                    "aadhaar_number",
                    "date_of_birth",
                    "marital_status",
                    "gender",
                    "category_belonging",
                    "fathers_name",
                    "mothers_name",
                ),
            },
        ),
        (
            "Contact Details",
            {
                "fields": (
                    "contact_number",
                    "email",
                    "permanent_address",
                    "state",
                    "city",
                    "pincode",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("submitted_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (
                "tracking_id",
                "submitted_at",
                "updated_at",
                "complaint_discrimination",
                "others_complaint_discrimination",
                "complaint_text",
                "declaration_accepted",
                "enrollment_id",
                "roll_no",
                "school_name",
                "department_name",
                "course_name",
                "full_name",
                "aadhaar_number",
                "date_of_birth",
                "marital_status",
                "gender",
                "category_belonging",
                "fathers_name",
                "mothers_name",
                "contact_number",
                "email",
                "permanent_address",
                "state",
                "city",
                "pincode",
            )
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_obj = DiscriminationComplaint.objects.get(pk=obj.pk)
                if old_obj.status != obj.status:
                    DiscriminationActionLog.objects.create(
                        complaint=obj,
                        action_taken_by=request.user,
                        action_description=(
                            f"Status updated from '{old_obj.get_status_display()}' "
                            f"to '{obj.get_status_display()}'"
                        ),
                        status_changed_to=obj.status,
                    )
            except DiscriminationComplaint.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)


# ─────────────────────────────────────────────────────────────────────────────
# Student Feedback Admin
# ─────────────────────────────────────────────────────────────────────────────


class FeedbackAttachmentInline(admin.TabularInline):
    model = FeedbackAttachment
    extra = 0
    readonly_fields = ["file", "uploaded_at"]
    exclude = ("deleted_at", "is_deleted")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class FeedbackSignatureInline(admin.TabularInline):
    model = FeedbackSignature
    extra = 0
    readonly_fields = ["image", "uploaded_at"]
    exclude = ("deleted_at", "is_deleted")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class FeedbackActionLogInline(admin.TabularInline):
    model = FeedbackActionLog
    extra = 0
    readonly_fields = [
        "action_taken_by",
        "status_changed_to",
        "timestamp",
    ]
    exclude = ("deleted_at", "is_deleted")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StudentFeedback)
class StudentFeedbackAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = (
        "tracking_id",
        "name_of_student",
        "subject_of_feedback",
        "status",
        "submitted_at",
    )
    list_filter = (
        "status",
        "subject_of_feedback",
        "course_name",
        "gender",
        "submitted_at",
    )
    search_fields = (
        "tracking_id",
        "name_of_student",
        "email",
        "contact_number",
        "enrollment_no",
        "roll_no",
    )
    readonly_fields = ("tracking_id", "submitted_at", "updated_at")
    inlines = [
        FeedbackAttachmentInline,
        FeedbackSignatureInline,
        FeedbackActionLogInline,
    ]
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }

    fieldsets = (
        (
            "Tracking",
            {
                "fields": ("tracking_id", "status"),
            },
        ),
        (
            "Feedback Details",
            {
                "fields": (
                    "subject_of_feedback",
                    "feedback_text",
                ),
            },
        ),
        (
            "Student Details",
            {
                "fields": (
                    "name_of_student",
                    "aadhaar_number",
                    "fathers_name",
                    "mothers_name",
                    "date_of_birth",
                    "gender",
                ),
            },
        ),
        (
            "Academic Details",
            {
                "fields": (
                    "course_name",
                    "roll_no",
                    "enrollment_no",
                ),
            },
        ),
        (
            "Contact Details",
            {
                "fields": (
                    "permanent_address",
                    "state",
                    "city",
                    "pincode",
                    "contact_number",
                    "email",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("submitted_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (
                "tracking_id",
                "submitted_at",
                "updated_at",
                "subject_of_feedback",
                "feedback_text",
                "name_of_student",
                "aadhaar_number",
                "fathers_name",
                "mothers_name",
                "date_of_birth",
                "gender",
                "course_name",
                "roll_no",
                "enrollment_no",
                "permanent_address",
                "state",
                "city",
                "pincode",
                "contact_number",
                "email",
            )
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_obj = StudentFeedback.objects.get(pk=obj.pk)
                if old_obj.status != obj.status:
                    FeedbackActionLog.objects.create(
                        feedback=obj,
                        action_taken_by=request.user,
                        action_description=(
                            f"Status updated from '{old_obj.get_status_display()}' "
                            f"to '{obj.get_status_display()}'"
                        ),
                        status_changed_to=obj.status,
                    )
            except StudentFeedback.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)
