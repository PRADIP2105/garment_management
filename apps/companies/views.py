from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company, UserProfile
from .serializers import CompanySerializer, UserProfileSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request, 'company') and self.request.company:
            return Company.objects.filter(id=self.request.company.id)
        return Company.objects.none()

    def perform_create(self, serializer):
        # Only allow company creation during registration
        pass

    def perform_update(self, serializer):
        # Only owners can update company details
        if self.request.user_role != 'owner':
            raise permissions.PermissionDenied("Only owners can update company details")
        serializer.save()

    def perform_destroy(self, instance):
        # Only owners can delete company
        if self.request.user_role != 'owner':
            raise permissions.PermissionDenied("Only owners can delete company")
        instance.delete()

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user's profile"""
        try:
            profile = UserProfile.objects.select_related('company', 'user').get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)