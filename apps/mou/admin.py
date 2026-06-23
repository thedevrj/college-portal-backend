from django.contrib import admin
from .models import MOU

@admin.register(MOU)
class MOUAdmin(admin.ModelAdmin):
    list_display = ('partner_name', 'date_of_signing', 'valid_till', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('partner_name', 'description')
    date_hierarchy = 'date_of_signing'
    exclude = ('is_deleted', 'deleted_at')
