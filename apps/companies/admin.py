from django.contrib import admin
from .models import Company, UserProfile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'mobile_number', 'is_active', 'created_at']
    list_filter = ['is_active', 'city', 'created_at']
    search_fields = ['name', 'mobile_number', 'email']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'role', 'language_preference', 'created_at']
    list_filter = ['role', 'language_preference', 'company']
    search_fields = ['user__username', 'user__email', 'company__name']