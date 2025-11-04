"""
Serializers for ingredients app
"""
from rest_framework import serializers
from .models import Ingredient, IngredientCategory
from datetime import date


class IngredientCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategory
        fields = ['id', 'name', 'display_order']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    is_expiring_soon = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'quantity', 'unit', 'category', 
            'expiry_date', 'notes', 'is_expiring_soon', 
            'is_expired', 'days_until_expiry', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_days_until_expiry(self, obj):
        if not obj.expiry_date:
            return None
        delta = obj.expiry_date - date.today()
        return delta.days
    
    def validate_expiry_date(self, value):
        if value and value < date.today():
            raise serializers.ValidationError("Expiry date cannot be in the past")
        return value


class IngredientBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk update operations"""
    operation = serializers.ChoiceField(choices=['add', 'update', 'delete'])
    ingredients = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )
    
    def validate_ingredients(self, value):
        """Validate ingredient data based on operation"""
        operation = self.initial_data.get('operation')
        
        if operation == 'add':
            # For add, ensure name is provided
            for item in value:
                if 'name' not in item:
                    raise serializers.ValidationError("Name is required for add operation")
        
        elif operation in ['update', 'delete']:
            # For update/delete, ensure id is provided
            for item in value:
                if 'id' not in item:
                    raise serializers.ValidationError("ID is required for update/delete operation")
        
        return value


class IngredientImportSerializer(serializers.Serializer):
    """Serializer for CSV import"""
    file = serializers.FileField()
    
    def validate_file(self, value):
        """Validate uploaded file is CSV"""
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are supported")
        
        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size should not exceed 5MB")
        
        return value
