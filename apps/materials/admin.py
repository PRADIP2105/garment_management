from django.contrib import admin
from .models import Material

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('material_name', 'company', 'unit', 'description')
    list_filter = ('company', 'unit')
    search_fields = ('material_name',)
