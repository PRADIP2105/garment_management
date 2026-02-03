from django.contrib import admin
from .models import Worker


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'skill_type', 'mobile_number', 'city', 'status', 'created_at']
    list_filter = ['skill_type', 'status', 'city', 'company']
    search_fields = ['name', 'mobile_number']
    ordering = ['name']