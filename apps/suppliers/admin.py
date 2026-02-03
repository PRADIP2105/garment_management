from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'mobile_number', 'city', 'created_at']
    list_filter = ['city', 'company']
    search_fields = ['name', 'mobile_number']
    ordering = ['name']