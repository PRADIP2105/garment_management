from django.contrib import admin
from .models import RawMaterial, MaterialInward


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ['material_name', 'company', 'unit', 'created_at']
    list_filter = ['unit', 'company']
    search_fields = ['material_name', 'description']
    ordering = ['material_name']


@admin.register(MaterialInward)
class MaterialInwardAdmin(admin.ModelAdmin):
    list_display = ['material', 'supplier', 'quantity', 'received_date', 'created_at']
    list_filter = ['received_date', 'supplier', 'material__company']
    search_fields = ['material__material_name', 'supplier__name']
    ordering = ['-received_date']