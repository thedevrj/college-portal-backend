from django import forms
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin
from college_backend_portal.email_service import send_status_update_email

from .models import Affidavit, AffidavitFAQ, AffidavitGuidelines, SampleAffidavit


class AffidavitAdminForm(forms.ModelForm):
    notify_user = forms.BooleanField(
        label="Send Email Notification",
        required=False,
        initial=True,
        help_text="If checked and status is changed, an automated status update email will be sent to the student.",
    )

    class Meta:
        model = Affidavit
        fields = "__all__"


@admin.register(SampleAffidavit)
class SampleAffidavitAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "affidavit_category")
    list_filter = (SoftDeleteListFilter, "affidavit_category")
    search_fields = ("title", "affidavit_category")
    exclude = ("is_deleted", "deleted_at")

@admin.register(Affidavit)
class AffidavitAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    form = AffidavitAdminForm
    list_display = (
        "tracking_id",
        "student_name",
        "roll_number",
        "enrollment_number",
        "department",
        "status",
        "submitted_on",
    )
    list_filter = (SoftDeleteListFilter, "status", "department", "submitted_on")
    search_fields = (   
        "tracking_id",
        "student_name",
        "roll_number",
        "enrollment_number",
        "department__name",
        "student_email",
        "student_phone",
        "parent_name",
    )
    readonly_fields = ("tracking_id", "submitted_on", "updated_on",  "student_name",
                    "roll_number",
                    "enrollment_number",
                    "department",
                    "program_name",
                    "student_email",
                    "student_phone",
                    "student_affidavit",
                    "parent_name",
                    "parent_phone",
                    "parent_affidavit",
                )
    fieldsets = (
        (
            "Tracking Details",
            {
                "fields": (
                    "tracking_id",
                    "status",
                    "remarks",
                    "notify_user",
                    "submitted_on",
                    "updated_on",
                )
            },
        ),
        (
            "Student Details",
            {
                "fields": (
                    "student_name",
                    "roll_number",
                    "enrollment_number",
                    "department",
                    "program_name",
                    "student_email",
                    "student_phone",
                    "student_affidavit",
                )
            },
        ),
        (
            "Parent/Guardian Details",
            {
                "fields": (
                    "parent_name",
                    "parent_phone",
                    "parent_affidavit",
                )
            },
        ),
    )
    
    list_editable = ("status",)
    date_hierarchy = "submitted_on"
    exclude = ("is_deleted", "deleted_at")

    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_obj = Affidavit.objects.get(pk=obj.pk)
                if old_obj.status != obj.status:
                    notify_user = form.cleaned_data.get("notify_user", True)
                    remarks = obj.remarks or ""
                    if notify_user and obj.student_email:
                        send_status_update_email(
                            to_email=obj.student_email,
                            recipient_name=obj.student_name,
                            tracking_id=obj.tracking_id,
                            portal_name="Anti-Ragging Affidavit Portal",
                            portal_slug="affidavit",
                            old_status_display=old_obj.get_status_display(),
                            new_status_display=obj.get_status_display(),
                            remarks=remarks,
                        )
            except Affidavit.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)


@admin.register(AffidavitFAQ)
class AffidavitFAQAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("question", "order")
    list_filter = (SoftDeleteListFilter,)
    search_fields = ("question", "answer")
    list_editable = ("order",)
    ordering = ("order", "id")
    exclude = ("is_deleted", "deleted_at")


@admin.register(AffidavitGuidelines)
class AffidavitGuidelinesAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title",)
    list_filter = (SoftDeleteListFilter,)
    search_fields = ("title", "content")
    exclude = ("is_deleted", "deleted_at")
