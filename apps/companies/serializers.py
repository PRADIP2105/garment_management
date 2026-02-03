from rest_framework import serializers
from .models import Company, UserProfile


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'city', 'mobile_number', 'email', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'company', 'role', 'mobile_number', 'language_preference', 'created_at']
        read_only_fields = ['id', 'created_at']