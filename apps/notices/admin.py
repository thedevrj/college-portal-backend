from django.contrib import admin
from django.db import models
from django import forms
from simple_history.admin import SimpleHistoryAdmin
from apps.accounts.filters import SoftDeleteListFilter
from apps.accounts.mixins import PortalSecurityMixin
from .models import GlobalNotice


class GlobalNoticeForm(forms.ModelForm):
    categories = forms.MultipleChoiceField(
        choices=GlobalNotice.CATEGORY_CHOICES,
        widget=forms.SelectMultiple,
        required=False,
        help_text="Hold down 'Control' to select more than one category.",
    )

    class Meta:
        model = GlobalNotice
        fields = "__all__"

    def clean_categories(self):
        return self.cleaned_data["categories"]


@admin.register(GlobalNotice)
class GlobalNoticeAdmin(PortalSecurityMixin, SimpleHistoryAdmin, admin.ModelAdmin):
    form = GlobalNoticeForm
    list_display = (
        "title",
        "show_in_marquee",
        "display_categories",
        "is_private",
        "is_archived",
        "archive_date",
        "posted_by",
    )
    list_filter = (
        SoftDeleteListFilter,
        "is_private",
        "show_in_marquee",
        "is_active",
        "date_posted",
        "is_archived",
        "archive_date",
    )
    search_fields = ("title",)
    readonly_fields = ("posted_by",)
    formfield_overrides = {
        models.DateField: {"widget": forms.DateInput(attrs={"type": "date"})},
    }

    def display_categories(self, obj):
        return ", ".join(obj.categories) if obj.categories else "-"

    display_categories.short_description = "Categories"

    # def get_queryset(self, request):
    #     from django.utils import timezone
    #     from django.db.models import Q

    #     qs = super().get_queryset(request)
    #     today = timezone.now().date()
    #     return qs.exclude(Q(is_archived=True) | Q(archive_date__lt=today))

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.posted_by = request.user
        super().save_model(request, obj, form, change)
