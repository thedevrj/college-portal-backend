from django.contrib import admin
from apps.accounts.filters import SoftDeleteListFilter
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


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
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
            old_obj = Complaint.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                ComplaintActionLog.objects.create(
                    complaint=obj,
                    action_taken_by=request.user,
                    action_description=f"Status updated from {old_obj.get_status_display()} to {obj.get_status_display()}",
                    status_changed_to=obj.status,
                )
        super().save_model(request, obj, form, change)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order")
    search_fields = ("question",)
    list_filter = (SoftDeleteListFilter,)
    list_editable = ("order",)
    exclude = ("deleted_at", "is_deleted")


@admin.register(PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "document_type", "uploaded_at")
    list_filter = (SoftDeleteListFilter, "document_type")
    search_fields = ("title",)
    exclude = ("deleted_at", "is_deleted")
