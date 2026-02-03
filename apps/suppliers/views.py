from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Supplier
from .serializers import SupplierSerializer
from apps.companies.models import UserProfile


class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['city']
    search_fields = ['name', 'mobile_number']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_company(self):
        """Get company from user profile"""
        company = getattr(self.request, 'company', None)
        if not company:
            try:
                profile = UserProfile.objects.select_related('company').get(user=self.request.user)
                company = profile.company
                self.request.company = company
            except UserProfile.DoesNotExist:
                return None
        return company

    def get_queryset(self):
        company = self.get_company()
        if company:
            return Supplier.objects.filter(company=company)
        return Supplier.objects.none()

    def perform_create(self, serializer):
        company = self.get_company()
        if not company:
            raise ValueError("Company not found for user")
        serializer.save(company=company)