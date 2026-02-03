from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from apps.companies.models import Company, UserProfile


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    # Company details
    company_name = serializers.CharField(max_length=200)
    company_address = serializers.CharField()
    company_city = serializers.CharField(max_length=100)
    company_mobile = serializers.CharField(max_length=15)
    company_email = serializers.EmailField(required=False)
    
    # User details
    mobile_number = serializers.CharField(max_length=15, required=False)
    language_preference = serializers.ChoiceField(choices=[('en', 'English'), ('gu', 'Gujarati')], default='en')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("Username already exists")
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Email already exists")
        
        return attrs

    def create(self, validated_data):
        # Create company
        company = Company.objects.create(
            name=validated_data['company_name'],
            address=validated_data['company_address'],
            city=validated_data['company_city'],
            mobile_number=validated_data['company_mobile'],
            email=validated_data.get('company_email', '')
        )
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Create user profile as owner
        UserProfile.objects.create(
            user=user,
            company=company,
            role='owner',
            mobile_number=validated_data.get('mobile_number', ''),
            language_preference=validated_data['language_preference']
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')

        return attrs