from django.contrib import admin
from django import forms
from django.db import models
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.mixins import PortalSecurityMixin
from apps.accounts.filters import SoftDeleteListFilter
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
from college_backend_portal.email_service import send_status_update_email


class PortalStatusNotificationFormMixin(forms.ModelForm):
    notify_user = forms.BooleanField(
        label="Send Email Notification",
        required=False,
        initial=True,
        help_text="If checked and status is changed, an automated status update email will be sent to the applicant.",
    )
    officer_remarks = forms.CharField(
        label="Officer Remarks / Email Note",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="Optional remarks explaining the status change or next steps, included in the email notification.",
    )


class GrievanceAdminForm(PortalStatusNotificationFormMixin):
    class Meta:
        model = Grievance
        fields = "__all__"


class ICCComplaintAdminForm(PortalStatusNotificationFormMixin):
    class Meta:
        model = ICCComplaint
        fields = "__all__"


class DiscriminationComplaintAdminForm(PortalStatusNotificationFormMixin):
    class Meta:
        model = DiscriminationComplaint
        fields = "__all__"


class StudentFeedbackAdminForm(PortalStatusNotificationFormMixin):
    class Meta:
        model = StudentFeedback
        fields = "__all__"


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
    form = GrievanceAdminForm
    list_display = (
        "tracking_id",
        "name_of_complainant",
        "nature_of_grievance",
        "complainant_type",
        "status",
        "submitted_at",
    )
    list_filter = (
        SoftDeleteListFilter,
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
            "Status & Notification",
            {
                "fields": ("tracking_id", "status", "notify_user", "officer_remarks"),
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
                    notify_user = form.cleaned_data.get("notify_user", True)
                    remarks = form.cleaned_data.get("officer_remarks", "").strip()
                    if remarks:
                        action_desc = f"Remarks: {remarks}"
                    else:
                        action_desc = (
                            f"Status updated from '{old_obj.get_status_display()}' "
                            f"to '{obj.get_status_display()}'"
                        )

                    GrievanceActionLog.objects.create(
                        grievance=obj,
                        action_taken_by=request.user,
                        action_description=action_desc,
                        status_changed_to=obj.status,
                    )

                    if notify_user and obj.email:
                        send_status_update_email(
                            to_email=obj.email,
                            recipient_name=obj.name_of_complainant,
                            tracking_id=obj.tracking_id,
                            portal_name="Grievance Redressal Portal",
                            portal_slug="grievance",
                            old_status_display=old_obj.get_status_display(),
                            new_status_display=obj.get_status_display(),
                            remarks=remarks,
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
    form = ICCComplaintAdminForm
    list_display = (
        "tracking_id",
        "name_of_complainant",
        "nature_of_grievance",
        "status",
        "submitted_at",
    )
    list_filter = (
        SoftDeleteListFilter,
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
            "Status & Notification",
            {
                "fields": ("tracking_id", "status", "notify_user", "officer_remarks"),
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
                    notify_user = form.cleaned_data.get("notify_user", True)
                    remarks = form.cleaned_data.get("officer_remarks", "").strip()

                    if remarks:
                        action_desc = f"Remarks: {remarks}"
                    else:
                        action_desc = (
                            f"Status updated from '{old_obj.get_status_display()}' "
                            f"to '{obj.get_status_display()}'"
                        )
                    
                    ICCActionLog.objects.create(
                        complaint=obj,
                        action_taken_by=request.user,
                        action_description=action_desc,
                        status_changed_to=obj.status,
                    )

                    if notify_user and obj.email:
                        send_status_update_email(
                            to_email=obj.email,
                            recipient_name=obj.name_of_complainant,
                            tracking_id=obj.tracking_id,
                            portal_name="Internal Complaints Committee (ICC)",
                            portal_slug="icc",
                            old_status_display=old_obj.get_status_display(),
                            new_status_display=obj.get_status_display(),
                            remarks=remarks,
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
    form = DiscriminationComplaintAdminForm
    list_display = (
        "tracking_id",
        "full_name",
        "complaint_discrimination",
        "status",
        "submitted_at",
    )
    list_filter = (
        SoftDeleteListFilter,
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
            "Status & Notification",
            {
                "fields": ("tracking_id", "status", "notify_user", "officer_remarks"),
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
                    notify_user = form.cleaned_data.get("notify_user", True)
                    remarks = form.cleaned_data.get("officer_remarks", "").strip()

                    if remarks:
                        action_desc = f"Remarks: {remarks}"
                    else:
                        action_desc = (
                            f"Status updated from '{old_obj.get_status_display()}' "
                            f"to '{obj.get_status_display()}'"
                        )
                    DiscriminationActionLog.objects.create(
                        complaint=obj,
                        action_taken_by=request.user,
                        action_description=action_desc,
                        status_changed_to=obj.status,
                    )

                    if notify_user and obj.email:
                        send_status_update_email(
                            to_email=obj.email,
                            recipient_name=obj.full_name,
                            tracking_id=obj.tracking_id,
                            portal_name="Equal Opportunity / Discrimination Cell",
                            portal_slug="discrimination",
                            old_status_display=old_obj.get_status_display(),
                            new_status_display=obj.get_status_display(),
                            remarks=remarks,
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
    form = StudentFeedbackAdminForm
    list_display = (
        "tracking_id",
        "name_of_student",
        "subject_of_feedback",
        "status",
        "submitted_at",
    )
    list_filter = (
        SoftDeleteListFilter,
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
            "Status & Notification",
            {
                "fields": ("tracking_id", "status", "notify_user", "officer_remarks"),
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
                    notify_user = form.cleaned_data.get("notify_user", True)
                    remarks = form.cleaned_data.get("officer_remarks", "").strip()

                    if remarks:
                        action_desc = f"Remarks: {remarks}"
                    else:
                        action_desc = (
                            f"Status updated from '{old_obj.get_status_display()}' "
                            f"to '{obj.get_status_display()}'"
                        )
                    FeedbackActionLog.objects.create(
                        feedback=obj,
                        action_taken_by=request.user,
                        action_description=action_desc,
                        status_changed_to=obj.status,
                    )

                    if notify_user and obj.email:
                        send_status_update_email(
                            to_email=obj.email,
                            recipient_name=obj.name_of_student,
                            tracking_id=obj.tracking_id,
                            portal_name="Student Feedback Portal",
                            portal_slug="feedback",
                            old_status_display=old_obj.get_status_display(),
                            new_status_display=obj.get_status_display(),
                            remarks=remarks,
                        )
            except StudentFeedback.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)
