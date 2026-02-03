from rest_framework import serializers
from .models import RawMaterial, MaterialInward
from apps.suppliers.serializers import SupplierSerializer


class RawMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterial
        fields = ['id', 'material_name', 'unit', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MaterialInwardSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    material_unit = serializers.CharField(source='material.unit', read_only=True)

    class Meta:
        model = MaterialInward
        fields = [
            'id', 'supplier', 'supplier_name', 'material', 'material_name', 
            'material_unit', 'quantity', 'received_date', 'remarks', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        # Ensure supplier and material belong to the same company
        request = self.context['request']
        company = getattr(request, 'company', None)
        
        if not company:
            # Try to get company from user profile
            from apps.companies.models import UserProfile
            try:
                profile = UserProfile.objects.select_related('company').get(user=request.user)
                company = profile.company
                request.company = company
            except UserProfile.DoesNotExist:
                raise serializers.ValidationError("User profile not found")
        
        if attrs['supplier'].company != company:
            raise serializers.ValidationError("Supplier does not belong to your company")
        if attrs['material'].company != company:
            raise serializers.ValidationError("Material does not belong to your company")
        return attrs