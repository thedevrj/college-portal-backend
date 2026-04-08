from django.contrib import admin
from .models import GlobalNotice

@admin.register(GlobalNotice)
class GlobalNoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'show_in_marquee', 'is_active', 'date_posted')
    list_filter = ('category', 'show_in_marquee', 'is_active', 'date_posted')
    search_fields = ('title', 'content')
