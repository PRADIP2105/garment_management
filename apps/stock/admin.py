from django.contrib import admin
from .models import StockLedger, CurrentStock


@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display = ['material', 'transaction_type', 'quantity', 'balance_quantity', 'transaction_date']
    list_filter = ['transaction_type', 'material__company', 'transaction_date']
    search_fields = ['material__material_name', 'remarks']
    ordering = ['-transaction_date']
    readonly_fields = ['transaction_date']


@admin.register(CurrentStock)
class CurrentStockAdmin(admin.ModelAdmin):
    list_display = ['material', 'current_quantity', 'last_updated']
    list_filter = ['material__company', 'last_updated']
    search_fields = ['material__material_name']
    ordering = ['material__material_name']
    readonly_fields = ['last_updated']