from django.contrib import admin
from django import forms
from .models import GlobalNotice

class GlobalNoticeForm(forms.ModelForm):
    categories = forms.MultipleChoiceField(
        choices=GlobalNotice.CATEGORY_CHOICES,
        widget=forms.SelectMultiple,
        required=False,
        help_text="Hold down 'Control' to select more than one category."
    )

    class Meta:
        model = GlobalNotice
        fields = '__all__'

    def clean_categories(self):
        return self.cleaned_data['categories']

@admin.register(GlobalNotice)
class GlobalNoticeAdmin(admin.ModelAdmin):
    form = GlobalNoticeForm
    list_display = ('title', 'display_categories', 'show_in_marquee', 'is_active', 'date_posted')
    list_filter = ('show_in_marquee', 'is_active', 'date_posted')
    search_fields = ('title',)

    def display_categories(self, obj):
        return ", ".join(obj.categories) if obj.categories else "-"
    display_categories.short_description = 'Categories'
