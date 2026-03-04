"""
Blood Stock app serializers.
"""

from rest_framework import serializers
from .models import BloodStock, StockTransaction


class BloodStockSerializer(serializers.ModelSerializer):
    """Serializer for blood stock details."""
    
    stock_status = serializers.CharField(read_only=True)
    actual_available = serializers.IntegerField(read_only=True)
    total_units = serializers.IntegerField(read_only=True)
    is_low = serializers.BooleanField(read_only=True)
    is_critical = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = BloodStock
        fields = [
            'id', 'blood_group', 'units_available', 'units_reserved',
            'units_expired', 'actual_available', 'total_units',
            'hospital_name', 'hospital_address', 'hospital_city',
            'contact_number', 'minimum_threshold', 'critical_threshold',
            'stock_status', 'is_low', 'is_critical',
            'last_updated', 'created_at'
        ]
        read_only_fields = [
            'id', 'units_expired', 'last_updated', 'created_at'
        ]


class BloodStockCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating blood stock."""
    
    class Meta:
        model = BloodStock
        fields = [
            'blood_group', 'units_available', 'hospital_name',
            'hospital_address', 'hospital_city', 'contact_number',
            'minimum_threshold', 'critical_threshold'
        ]
    
    def validate(self, attrs):
        """Validate unique combination of blood group and hospital."""
        blood_group = attrs.get('blood_group')
        hospital_name = attrs.get('hospital_name')
        
        if BloodStock.objects.filter(
            blood_group=blood_group,
            hospital_name=hospital_name
        ).exists():
            raise serializers.ValidationError(
                f"Stock entry for {blood_group} at {hospital_name} already exists."
            )
        
        return attrs


class BloodStockUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating blood stock."""
    
    class Meta:
        model = BloodStock
        fields = [
            'units_available', 'hospital_name', 'hospital_city',
            'hospital_address', 'contact_number',
            'minimum_threshold', 'critical_threshold'
        ]


class BloodStockListSerializer(serializers.ModelSerializer):
    """Serializer for listing blood stock (compact view)."""
    
    stock_status = serializers.CharField(read_only=True)
    
    class Meta:
        model = BloodStock
        fields = [
            'id', 'blood_group', 'units_available', 'units_reserved',
            'hospital_name', 'hospital_city', 'stock_status', 'last_updated'
        ]


class StockTransactionSerializer(serializers.ModelSerializer):
    """Serializer for stock transactions."""
    
    blood_group = serializers.CharField(source='blood_stock.blood_group', read_only=True)
    hospital_name = serializers.CharField(source='blood_stock.hospital_name', read_only=True)
    performed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StockTransaction
        fields = [
            'id', 'blood_stock', 'blood_group', 'hospital_name',
            'transaction_type', 'units', 'units_before', 'units_after',
            'blood_request', 'performed_by', 'performed_by_name',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return obj.performed_by.get_full_name()
        return None


class StockStatisticsSerializer(serializers.Serializer):
    """Serializer for stock statistics."""
    
    total_units = serializers.IntegerField()
    total_available = serializers.IntegerField()
    total_reserved = serializers.IntegerField()
    total_expired = serializers.IntegerField()
    by_blood_group = serializers.ListField()
    by_hospital = serializers.ListField()
    critical_stocks = serializers.ListField()
    low_stocks = serializers.ListField()


class StockImportSerializer(serializers.Serializer):
    """Serializer for importing stock from CSV."""
    
    file = serializers.FileField()
    
    def validate_file(self, value):
        """Validate file is CSV."""
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are supported.")
        return value
