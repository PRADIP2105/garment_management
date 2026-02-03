from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import RawMaterial, MaterialInward
from .serializers import RawMaterialSerializer, MaterialInwardSerializer
from apps.stock.services import StockService
from apps.companies.models import UserProfile


class RawMaterialViewSet(viewsets.ModelViewSet):
    serializer_class = RawMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['unit']
    search_fields = ['material_name', 'description']
    ordering_fields = ['material_name', 'created_at']
    ordering = ['material_name']

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
            return RawMaterial.objects.filter(company=company)
        return RawMaterial.objects.none()

    def perform_create(self, serializer):
        company = self.get_company()
        if not company:
            raise ValueError("Company not found for user")
        serializer.save(company=company)


class MaterialInwardViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialInwardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['supplier', 'material', 'received_date']
    search_fields = ['supplier__name', 'material__material_name']
    ordering_fields = ['received_date', 'created_at']
    ordering = ['-received_date']

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
            return MaterialInward.objects.filter(company=company).select_related('supplier', 'material')
        return MaterialInward.objects.none()

    def perform_create(self, serializer):
        company = self.get_company()
        if not company:
            raise ValueError("Company not found for user")
        instance = serializer.save(company=company)
        # Update stock ledger
        StockService.add_inward_stock(
            company=instance.company,
            material=instance.material,
            quantity=instance.quantity,
            reference_type='inward',
            reference_id=instance.id
        )