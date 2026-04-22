from django.contrib import admin
from .models import Centre


@admin.register(Centre)
class CentreAdmin(admin.ModelAdmin):

    list_display = ("name", "slug", "school", "head", "head_title")
    list_filter = ("school", "head_title")
    search_fields = ("name", "slug", "head__name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("head",)

    class Media:
        js = ("js/admin_dynamic_fields.js?v=6",)
