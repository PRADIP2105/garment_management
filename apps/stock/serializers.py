from rest_framework import serializers
from .models import StockLedger, CurrentStock


class StockLedgerSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    material_unit = serializers.CharField(source='material.unit', read_only=True)

    class Meta:
        model = StockLedger
        fields = [
            'id', 'material', 'material_name', 'material_unit', 'transaction_type',
            'quantity', 'balance_quantity', 'reference_type', 'reference_id',
            'transaction_date', 'remarks'
        ]
        read_only_fields = ['id', 'transaction_date']


class CurrentStockSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    material_unit = serializers.CharField(source='material.unit', read_only=True)
    material_description = serializers.CharField(source='material.description', read_only=True)

    class Meta:
        model = CurrentStock
        fields = [
            'id', 'material', 'material_name', 'material_unit', 'material_description',
            'current_quantity', 'last_updated'
        ]
        read_only_fields = ['id', 'current_quantity', 'last_updated']