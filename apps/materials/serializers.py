from decimal import Decimal

from rest_framework import serializers

from apps.materials.models import Material
from apps.materials.services import get_material_closing_stock


class MaterialSerializer(serializers.ModelSerializer):
    closing_stock = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = [
            "id",
            "material_name",
            "unit",
            "description",
            "created_at",
            "closing_stock",
        ]
        read_only_fields = ["id", "created_at", "closing_stock"]

    def get_closing_stock(self, obj: Material) -> Decimal:
        return get_material_closing_stock(obj)

