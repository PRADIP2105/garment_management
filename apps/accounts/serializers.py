from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.companies.models import Company

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "city", "created_at"]
        read_only_fields = ["id", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "language_preference",
        ]
        read_only_fields = ["id", "role"]


class RegisterOwnerSerializer(serializers.Serializer):
    """Register first user and company (tenant)."""

    company_name = serializers.CharField(max_length=255)
    company_city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    language_preference = serializers.ChoiceField(
        choices=(("gu", "Gujarati"), ("en", "English")), default="gu"
    )

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(_("Username already exists"))
        return value

    def create(self, validated_data):
        company = Company.objects.create(
            name=validated_data["company_name"],
            city=validated_data.get("company_city", ""),
        )
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            company=company,
            role=User.Role.OWNER,
            language_preference=validated_data["language_preference"],
        )
        return user


class CreateStaffSerializer(serializers.ModelSerializer):
    """Create staff under same company (owner only)."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "language_preference",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        request = self.context["request"]
        owner: User = request.user
        user = User.objects.create_user(
            company=owner.company,
            role=User.Role.STAFF,
            **validated_data,
        )
        return user


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """Custom serializer for obtaining JWT token pairs with better error messages."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            # Try to authenticate the user
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password
            )

            if not user:
                raise serializers.ValidationError(
                    _("Invalid username or password."),
                    code="authentication_failed"
                )

            # Check if user is active
            if not user.is_active:
                raise serializers.ValidationError(
                    _("User account is disabled."),
                    code="account_disabled"
                )

            attrs["user"] = user
            return attrs
        else:
            raise serializers.ValidationError(
                _("Must include 'username' and 'password'."),
                code="missing_credentials"
            )
