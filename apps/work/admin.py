from django.contrib import admin
from .models import WorkType, MaterialInward, WorkDistribution, WorkReceived, WorkReturn

@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    list_filter = ('company',)

@admin.register(MaterialInward)
class MaterialInwardAdmin(admin.ModelAdmin):
    list_display = ('material', 'company', 'supplier', 'quantity', 'received_date')
    list_filter = ('company', 'received_date')
    search_fields = ('material__material_name', 'supplier__name')

@admin.register(WorkDistribution)
class WorkDistributionAdmin(admin.ModelAdmin):
    list_display = ('worker', 'company', 'work_type', 'lot_size', 'distributed_date')
    list_filter = ('company', 'distributed_date', 'work_type')
    search_fields = ('worker__name',)

@admin.register(WorkReceived)
class WorkReceivedAdmin(admin.ModelAdmin):
    list_display = ('distribution', 'company', 'received_quantity', 'received_date', 'status')
    list_filter = ('company', 'status', 'received_date')

@admin.register(WorkReturn)
class WorkReturnAdmin(admin.ModelAdmin):
    list_display = ('distribution', 'company', 'completed_quantity', 'pending_quantity', 'return_date')
    list_filter = ('company', 'return_date')
