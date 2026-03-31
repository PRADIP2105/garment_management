from decimal import Decimal

from rest_framework import serializers

from apps.materials.models import Material
from apps.suppliers.models import Supplier
from apps.work.models import (
    MaterialInward,
    WorkDistribution,
    WorkDistributionMaterial,
    WorkReturn,
    WorkReturnMaterial,
    WorkType,
)
from apps.workers.models import Worker


class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = ["id", "name"]


class MaterialInwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialInward
        fields = [
            "id",
            "supplier",
            "material",
            "quantity",
            "received_date",
            "remarks",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        request = self.context["request"]
        supplier: Supplier = attrs["supplier"]
        material: Material = attrs["material"]
        if supplier.company != request.user.company or material.company != request.user.company:
            raise serializers.ValidationError("Supplier and material must belong to your company")
        return attrs


class WorkDistributionMaterialInputSerializer(serializers.Serializer):
    material = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all())
    issued_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)


class WorkDistributionSerializer(serializers.ModelSerializer):
    issued_materials = WorkDistributionMaterialInputSerializer(many=True)

    class Meta:
        model = WorkDistribution
        fields = [
            "id",
            "worker",
            "work_type",
            "lot_size",
            "distributed_date",
            "expected_return_date",
            "created_at",
            "issued_materials",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        request = self.context["request"]
        worker: Worker = attrs["worker"]
        work_type: WorkType = attrs["work_type"]
        if worker.company != request.user.company or work_type.company != request.user.company:
            raise serializers.ValidationError("Worker and work type must belong to your company")
        for im in attrs.get("issued_materials", []):
            if im["material"].company != request.user.company:
                raise serializers.ValidationError(
                    f"Material {im['material'].id} does not belong to your company"
                )
        return attrs


class WorkDistributionListMaterialSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source="material.material_name", read_only=True)

    class Meta:
        model = WorkDistributionMaterial
        fields = ["id", "material", "material_name", "issued_quantity"]


class WorkDistributionDetailSerializer(serializers.ModelSerializer):
    issued_materials = WorkDistributionListMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = WorkDistribution
        fields = [
            "id",
            "worker",
            "work_type",
            "lot_size",
            "distributed_date",
            "expected_return_date",
            "created_at",
            "issued_materials",
        ]


class WorkReturnMaterialInputSerializer(serializers.Serializer):
    material = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all())
    returned_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)


class WorkReturnSerializer(serializers.ModelSerializer):
    returned_materials = WorkReturnMaterialInputSerializer(many=True)

    class Meta:
        model = WorkReturn
        fields = [
            "id",
            "distribution",
            "completed_quantity",
            "pending_quantity",
            "wastage_quantity",
            "return_date",
            "created_at",
            "returned_materials",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        request = self.context["request"]
        distribution: WorkDistribution = attrs["distribution"]
        if distribution.company != request.user.company:
            raise serializers.ValidationError("Distribution must belong to your company")
        return attrs

