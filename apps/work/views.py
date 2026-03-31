from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.materials.models import Material
from apps.suppliers.models import Supplier
from apps.work.models import MaterialInward, WorkDistribution, WorkReturn, WorkType
from apps.work.services import (
    create_material_inward,
    distribute_work,
    register_work_return,
)
from .serializers import (
    MaterialInwardSerializer,
    WorkDistributionDetailSerializer,
    WorkDistributionSerializer,
    WorkReturnSerializer,
    WorkTypeSerializer,
)


class CompanyScopedMixin:
    """Helper mixin to get current company."""

    @property
    def company(self):
        return self.request.user.company


class WorkTypeViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    serializer_class = WorkTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkType.objects.filter(company=self.company)

    def perform_create(self, serializer):
        serializer.save(company=self.company)


class MaterialInwardViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    serializer_class = MaterialInwardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MaterialInward.objects.filter(company=self.company)

    def perform_create(self, serializer):
        data = serializer.validated_data
        inward = create_material_inward(
            company=self.company,
            supplier=data["supplier"],
            material=data["material"],
            quantity=data["quantity"],
            received_date=data["received_date"],
            remarks=data.get("remarks", ""),
        )
        serializer.instance = inward


class WorkDistributionViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            WorkDistribution.objects.filter(company=self.company)
            .select_related("worker", "work_type")
            .prefetch_related("issued_materials__material")
        )

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return WorkDistributionDetailSerializer
        return WorkDistributionSerializer

    def create(self, request, *args, **kwargs):
        serializer = WorkDistributionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        materials_input = [
            {"material": im["material"], "issued_quantity": im["issued_quantity"]}
            for im in data["issued_materials"]
        ]

        try:
            distribution = distribute_work(
                company=self.company,
                worker=data["worker"],
                work_type=data["work_type"],
                lot_size=data["lot_size"],
                distributed_date=data["distributed_date"],
                expected_return_date=data.get("expected_return_date"),
                materials=materials_input,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        out = WorkDistributionDetailSerializer(distribution)
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_201_CREATED, headers=headers)


class WorkReturnViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    serializer_class = WorkReturnSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            WorkReturn.objects.filter(company=self.company)
            .select_related("distribution")
            .prefetch_related("returned_materials__material")
        )

    def create(self, request, *args, **kwargs):
        serializer = WorkReturnSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        returned_materials = [
            {"material": rm["material"], "returned_quantity": rm["returned_quantity"]}
            for rm in data["returned_materials"]
        ]

        try:
            work_return = register_work_return(
                company=self.company,
                distribution=data["distribution"],
                completed_quantity=data["completed_quantity"],
                pending_quantity=data["pending_quantity"],
                wastage_quantity=data.get("wastage_quantity"),
                return_date=data["return_date"],
                returned_materials=returned_materials,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        out = WorkReturnSerializer(work_return)
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_201_CREATED, headers=headers)

