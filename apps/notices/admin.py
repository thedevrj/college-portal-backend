from django.contrib import admin
from django import forms
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
class GlobalNoticeAdmin(admin.ModelAdmin):
    form = GlobalNoticeForm
    list_display = (
        "title",
        "show_in_marquee",
        "display_categories",
        "is_private",
        "is_active",
        "date_posted",
        "posted_by",
    )
    list_filter = ("is_private", "show_in_marquee", "is_active", "date_posted")
    search_fields = ("title",)
    readonly_fields = ("posted_by", "date_posted")

    def display_categories(self, obj):
        return ", ".join(obj.categories) if obj.categories else "-"

    display_categories.short_description = "Categories"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.posted_by = request.user
        super().save_model(request, obj, form, change)
