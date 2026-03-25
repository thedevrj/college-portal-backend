from django.contrib import admin
from .models import Centre


@admin.register(Centre)
class CentreAdmin(admin.ModelAdmin):

    list_display = ("name", "slug", "school")
    list_filter = ("school",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
