from rest_framework import serializers

from apps.suppliers.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "mobile_number",
            "address",
            "city",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

