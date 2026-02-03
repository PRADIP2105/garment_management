from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction
from .models import WorkType, WorkDistribution, WorkReturn
from .serializers import WorkTypeSerializer, WorkDistributionSerializer, WorkReturnSerializer
from apps.stock.services import StockService
from rest_framework import serializers
from apps.companies.models import UserProfile


class WorkTypeViewSet(viewsets.ModelViewSet):
    serializer_class = WorkTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
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
            return WorkType.objects.filter(company=company)
        return WorkType.objects.none()

    def perform_create(self, serializer):
        company = self.get_company()
        if not company:
            raise ValueError("Company not found for user")
        serializer.save(company=company)


class WorkDistributionViewSet(viewsets.ModelViewSet):
    serializer_class = WorkDistributionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['worker', 'work_type', 'status', 'distributed_date']
    search_fields = ['worker__name', 'work_type__name']
    ordering_fields = ['distributed_date', 'expected_return_date', 'created_at']
    ordering = ['-distributed_date']

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
            return WorkDistribution.objects.filter(company=company).select_related(
                'worker', 'work_type'
            ).prefetch_related('materials__material')
        return WorkDistribution.objects.none()

    @transaction.atomic
    def perform_create(self, serializer):
        company = self.get_company()
        if not company:
            raise ValueError("Company not found for user")
        instance = serializer.save(company=company)
        
        # Issue materials from stock
        for distributed_material in instance.materials.all():
            try:
                StockService.issue_stock(
                    company=instance.company,
                    material=distributed_material.material,
                    quantity=distributed_material.issued_quantity,
                    reference_type='distribution',
                    reference_id=instance.id,
                    remarks=f"Issued to {instance.worker.name} for {instance.work_type.name}"
                )
            except ValueError as e:
                # Rollback will happen automatically due to @transaction.atomic
                raise serializers.ValidationError(f"Stock error: {str(e)}")


class WorkReturnViewSet(viewsets.ModelViewSet):
    serializer_class = WorkReturnSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['work_distribution', 'return_date']
    search_fields = ['work_distribution__worker__name', 'work_distribution__work_type__name']
    ordering_fields = ['return_date', 'created_at']
    ordering = ['-return_date']

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
            return WorkReturn.objects.filter(company=company).select_related(
                'work_distribution__worker', 'work_distribution__work_type'
            ).prefetch_related('materials__material')
        return WorkReturn.objects.none()

    @transaction.atomic
    def perform_create(self, serializer):
        company = self.get_company()
        if not company:
            raise ValueError("Company not found for user")
        instance = serializer.save(company=company)
        
        # Update work distribution status
        work_distribution = instance.work_distribution
        total_completed = sum(wr.completed_quantity for wr in work_distribution.returns.all())
        
        if total_completed >= work_distribution.lot_size:
            work_distribution.status = 'completed'
        else:
            work_distribution.status = 'partially_returned'
        work_distribution.save()
        
        # Return materials to stock and record wastage
        for returned_material in instance.materials.all():
            if returned_material.returned_quantity > 0:
                StockService.return_stock(
                    company=instance.company,
                    material=returned_material.material,
                    quantity=returned_material.returned_quantity,
                    reference_type='return',
                    reference_id=instance.id,
                    remarks=f"Returned from {work_distribution.worker.name}"
                )
            
            if returned_material.wastage_quantity > 0:
                StockService.record_wastage(
                    company=instance.company,
                    material=returned_material.material,
                    quantity=returned_material.wastage_quantity,
                    reference_type='return',
                    reference_id=instance.id,
                    remarks=f"Wastage from {work_distribution.worker.name}"
                )