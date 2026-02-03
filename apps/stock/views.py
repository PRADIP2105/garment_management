from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import StockLedger, CurrentStock
from .serializers import StockLedgerSerializer, CurrentStockSerializer
from apps.companies.models import UserProfile


class StockLedgerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StockLedgerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['material', 'transaction_type', 'reference_type']
    search_fields = ['material__material_name', 'remarks']
    ordering_fields = ['transaction_date']
    ordering = ['-transaction_date']

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
            return StockLedger.objects.filter(company=company).select_related('material')
        return StockLedger.objects.none()


class CurrentStockViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CurrentStockSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['material']
    search_fields = ['material__material_name']
    ordering_fields = ['material__material_name', 'current_quantity', 'last_updated']
    ordering = ['material__material_name']

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
            return CurrentStock.objects.filter(company=company).select_related('material')
        return CurrentStock.objects.none()

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get materials with low stock (less than 10 units)"""
        company = self.get_company()
        if company:
            queryset = CurrentStock.objects.filter(company=company, current_quantity__lt=10).select_related('material')
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response([])