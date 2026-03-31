from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    company_name = serializers.CharField(write_only=True, required=True)
    company_address = serializers.CharField(write_only=True, required=False)
    company_city = serializers.CharField(write_only=True, required=False)
    company_mobile = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'company_name', 'company_address', 'company_city', 'company_mobile']
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        company_name = validated_data.pop('company_name')
        company_address = validated_data.pop('company_address', None)
        company_city = validated_data.pop('company_city', None)
        company_mobile = validated_data.pop('company_mobile', None)

        user = User.objects.create_user(**validated_data)

        # Assuming the User model has these fields or a related Company model
        user.company_name = company_name
        user.company_address = company_address
        user.company_city = company_city
        user.company_mobile = company_mobile
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
        else:
            raise serializers.ValidationError("Must include username and password")
        
        data['user'] = user
        return data
