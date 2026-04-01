from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'company', 'role', 'is_staff')
    list_filter = ('role', 'company', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Company Info', {'fields': ('company', 'role', 'language_preference')}),
    )
