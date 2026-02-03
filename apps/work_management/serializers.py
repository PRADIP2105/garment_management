from rest_framework import serializers
from .models import WorkType, WorkDistribution, DistributedMaterial, WorkReturn, ReturnedMaterial


class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class DistributedMaterialSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    material_unit = serializers.CharField(source='material.unit', read_only=True)

    class Meta:
        model = DistributedMaterial
        fields = ['id', 'material', 'material_name', 'material_unit', 'issued_quantity']
        read_only_fields = ['id']


class WorkDistributionSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    work_type_name = serializers.CharField(source='work_type.name', read_only=True)
    materials = DistributedMaterialSerializer(many=True)

    class Meta:
        model = WorkDistribution
        fields = [
            'id', 'worker', 'worker_name', 'work_type', 'work_type_name',
            'lot_size', 'distributed_date', 'expected_return_date', 'status',
            'materials', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        materials_data = validated_data.pop('materials')
        # Company will be set in the view's perform_create method
        
        work_distribution = WorkDistribution.objects.create(**validated_data)
        
        for material_data in materials_data:
            DistributedMaterial.objects.create(
                work_distribution=work_distribution,
                **material_data
            )
        
        return work_distribution

    def validate(self, attrs):
        from apps.companies.models import UserProfile
        request = self.context['request']
        
        # Get company from request or user profile
        company = getattr(request, 'company', None)
        if not company:
            try:
                profile = UserProfile.objects.select_related('company').get(user=request.user)
                company = profile.company
                request.company = company
            except UserProfile.DoesNotExist:
                raise serializers.ValidationError("User profile not found")
        
        # Validate worker belongs to company
        if attrs['worker'].company != company:
            raise serializers.ValidationError("Worker does not belong to your company")
        
        # Validate work type belongs to company
        if attrs['work_type'].company != company:
            raise serializers.ValidationError("Work type does not belong to your company")
        
        # Validate materials belong to company
        for material_data in attrs.get('materials', []):
            if material_data['material'].company != company:
                raise serializers.ValidationError("Material does not belong to your company")
        
        return attrs


class ReturnedMaterialSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    material_unit = serializers.CharField(source='material.unit', read_only=True)

    class Meta:
        model = ReturnedMaterial
        fields = ['id', 'material', 'material_name', 'material_unit', 'returned_quantity', 'wastage_quantity']
        read_only_fields = ['id']


class WorkReturnSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source='work_distribution.worker.name', read_only=True)
    work_type_name = serializers.CharField(source='work_distribution.work_type.name', read_only=True)
    materials = ReturnedMaterialSerializer(many=True, required=False)

    class Meta:
        model = WorkReturn
        fields = [
            'id', 'work_distribution', 'worker_name', 'work_type_name',
            'completed_quantity', 'pending_quantity', 'return_date',
            'remarks', 'materials', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        materials_data = validated_data.pop('materials', [])
        # Company will be set in the view's perform_create method
        
        work_return = WorkReturn.objects.create(**validated_data)
        
        for material_data in materials_data:
            ReturnedMaterial.objects.create(
                work_return=work_return,
                **material_data
            )
        
        return work_return

    def validate(self, attrs):
        from apps.companies.models import UserProfile
        request = self.context['request']
        work_distribution = attrs['work_distribution']
        
        # Get company from request or user profile
        company = getattr(request, 'company', None)
        if not company:
            try:
                profile = UserProfile.objects.select_related('company').get(user=request.user)
                company = profile.company
                request.company = company
            except UserProfile.DoesNotExist:
                raise serializers.ValidationError("User profile not found")
        
        # Validate work distribution belongs to company
        if work_distribution.company != company:
            raise serializers.ValidationError("Work distribution does not belong to your company")
        
        # Validate quantities
        total_returned = sum(wr.completed_quantity for wr in work_distribution.returns.all())
        if total_returned + attrs['completed_quantity'] > work_distribution.lot_size:
            raise serializers.ValidationError("Total returned quantity cannot exceed lot size")
        
        return attrs