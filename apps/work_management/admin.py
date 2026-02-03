from django.contrib import admin
from .models import WorkType, WorkDistribution, DistributedMaterial, WorkReturn, ReturnedMaterial


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'created_at']
    list_filter = ['company']
    search_fields = ['name', 'description']


class DistributedMaterialInline(admin.TabularInline):
    model = DistributedMaterial
    extra = 1


@admin.register(WorkDistribution)
class WorkDistributionAdmin(admin.ModelAdmin):
    list_display = ['worker', 'work_type', 'lot_size', 'distributed_date', 'status']
    list_filter = ['status', 'work_type', 'distributed_date']
    search_fields = ['worker__name', 'work_type__name']
    inlines = [DistributedMaterialInline]


class ReturnedMaterialInline(admin.TabularInline):
    model = ReturnedMaterial
    extra = 1


@admin.register(WorkReturn)
class WorkReturnAdmin(admin.ModelAdmin):
    list_display = ['work_distribution', 'completed_quantity', 'pending_quantity', 'return_date']
    list_filter = ['return_date']
    search_fields = ['work_distribution__worker__name']
    inlines = [ReturnedMaterialInline]