import logging
from django.contrib.auth import authenticate, get_user_model
from rest_framework import permissions, status, views, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CreateStaffSerializer,
    RegisterOwnerSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
)

User = get_user_model()

logger = logging.getLogger(__name__)


class IsOwner(permissions.BasePermission):
    """Allow access only to company owner users."""

    def has_permission(self, request, view) -> bool:
        user: User = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == User.Role.OWNER
        )


class RegisterOwnerView(views.APIView):
    """Public endpoint to register company + first owner user."""

    permission_classes: list = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterOwnerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class StaffViewSet(viewsets.ModelViewSet):
    """Manage staff users within the same company (owner only)."""

    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return User.objects.filter(company=self.request.user.company, role=User.Role.STAFF)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CreateStaffSerializer
        return UserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain view with better error handling and logging."""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        logger.info(f"Login attempt for username: {request.data.get('username')}")
        try:
            response = super().post(request, *args, **kwargs)
            logger.info(f"Login successful for username: {request.data.get('username')}")
            return response
        except Exception as e:
            logger.error(f"Login failed for username: {request.data.get('username')} - Error: {str(e)}")
            raise

