from django.contrib import admin
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Complaint,
    ComplaintAttachment,
    FAQ,
    PolicyDocument,
    ComplaintActionLog,
)


class ComplaintAttachmentInline(admin.TabularInline):
    model = ComplaintAttachment
    extra = 0
    readonly_fields = ["uploaded_at"]
    exclude = ("deleted_at", "is_deleted")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ComplaintActionLogInline(admin.TabularInline):
    model = ComplaintActionLog
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


from django import forms
from college_backend_portal.email_service import send_status_update_email


class ComplaintAdminForm(forms.ModelForm):
    notify_user = forms.BooleanField(
        label="Send Email Notification",
        required=False,
        initial=True,
        help_text="If checked and status is changed, an automated status update email will be sent to the complainant (if not anonymous).",
    )
    officer_remarks = forms.CharField(
        label="Officer Remarks / Email Note",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="Optional remarks explaining the status update, included in the email notification.",
    )

    class Meta:
        model = Complaint
        fields = "__all__"


@admin.register(Complaint)
class ComplaintAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    form = ComplaintAdminForm
    list_display = ("tracking_id", "category", "status", "submitted_at")
    list_filter = (
        SoftDeleteListFilter,
        "status",
        "category",
        "is_anonymous",
        "submitted_at",
    )
    search_fields = ("tracking_id", "name", "email", "phone")
    readonly_fields = ("tracking_id", "submitted_at", "updated_at")
    inlines = [ComplaintAttachmentInline, ComplaintActionLogInline]
    exclude = ("deleted_at", "is_deleted")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (
                "tracking_id",
                "submitted_at",
                "updated_at",
                "name",
                "email",
                "phone",
                "is_anonymous",
                "category",
                "description",
            )
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_obj = Complaint.objects.get(pk=obj.pk)
                if old_obj.status != obj.status:
                    notify_user = form.cleaned_data.get("notify_user", True)
                    remarks = form.cleaned_data.get("officer_remarks", "").strip()
                    if remarks:
                        action_desc = f"Remarks: {remarks}"
                    else:
                        action_desc = f"Status updated from {old_obj.get_status_display()} to {obj.get_status_display()}"
                    

                    ComplaintActionLog.objects.create(
                        complaint=obj,
                        action_taken_by=request.user,
                        action_description=action_desc,
                        status_changed_to=obj.status,
                    )

                    if notify_user and not obj.is_anonymous and obj.email:
                        send_status_update_email(
                            to_email=obj.email,
                            recipient_name=obj.name or "Complainant",
                            tracking_id=obj.tracking_id,
                            portal_name="Vigilance Cell",
                            portal_slug="vigilance",
                            old_status_display=old_obj.get_status_display(),
                            new_status_display=obj.get_status_display(),
                            remarks=remarks,
                        )
            except Complaint.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)


@admin.register(FAQ)
class FAQAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("question", "order")
    search_fields = ("question",)
    list_filter = (SoftDeleteListFilter,)
    list_editable = ("order",)
    exclude = ("deleted_at", "is_deleted")


@admin.register(PolicyDocument)
class PolicyDocumentAdmin(PortalSecurityMixin, SimpleHistoryAdmin):
    list_display = ("title", "document_type", "uploaded_at")
    list_filter = (SoftDeleteListFilter, "document_type")
    search_fields = ("title",)
    exclude = ("deleted_at", "is_deleted")
