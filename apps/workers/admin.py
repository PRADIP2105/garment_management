from django.contrib import admin
from .models import Worker

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'mobile_number', 'skill_type', 'machine_type', 'status')
    list_filter = ('company', 'skill_type', 'machine_type', 'status')
    search_fields = ('name', 'mobile_number')
