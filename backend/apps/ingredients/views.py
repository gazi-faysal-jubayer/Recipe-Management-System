"""
Views for ingredients app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count
from django.db import transaction
from .models import Ingredient, IngredientCategory
from .serializers import (
    IngredientSerializer, IngredientCategorySerializer,
    IngredientBulkUpdateSerializer, IngredientImportSerializer
)
from apps.common.utils import success_response, error_response, paginate_response
from apps.authentication.permissions import IsOwner
import csv
import io


class IngredientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ingredient CRUD operations
    """
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        queryset = Ingredient.objects.filter(user=self.request.user)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)
        
        # Filter by expiring soon
        expiring = self.request.query_params.get('expiring')
        if expiring and expiring.lower() == 'true':
            from datetime import date, timedelta
            queryset = queryset.filter(
                expiry_date__lte=date.today() + timedelta(days=7),
                expiry_date__gte=date.today()
            )
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Order by
        ordering = self.request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response(
                data=serializer.data,
                message='Ingredient added successfully',
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            message='Failed to add ingredient',
            errors=serializer.errors
        )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message='Ingredient updated successfully'
            )
        return error_response(
            message='Failed to update ingredient',
            errors=serializer.errors
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(
            message='Ingredient deleted successfully',
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk add, update, or delete ingredients
        """
        serializer = IngredientBulkUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid bulk update data',
                errors=serializer.errors
            )
        
        operation = serializer.validated_data['operation']
        ingredients_data = serializer.validated_data['ingredients']
        results = {'success': [], 'errors': []}
        
        with transaction.atomic():
            if operation == 'add':
                for data in ingredients_data:
                    ingredient_serializer = IngredientSerializer(data=data)
                    if ingredient_serializer.is_valid():
                        ingredient_serializer.save(user=request.user)
                        results['success'].append(ingredient_serializer.data)
                    else:
                        results['errors'].append({
                            'data': data,
                            'errors': ingredient_serializer.errors
                        })
            
            elif operation == 'update':
                for data in ingredients_data:
                    try:
                        ingredient = Ingredient.objects.get(
                            id=data['id'], 
                            user=request.user
                        )
                        ingredient_serializer = IngredientSerializer(
                            ingredient, 
                            data=data, 
                            partial=True
                        )
                        if ingredient_serializer.is_valid():
                            ingredient_serializer.save()
                            results['success'].append(ingredient_serializer.data)
                        else:
                            results['errors'].append({
                                'data': data,
                                'errors': ingredient_serializer.errors
                            })
                    except Ingredient.DoesNotExist:
                        results['errors'].append({
                            'data': data,
                            'errors': {'id': 'Ingredient not found'}
                        })
            
            elif operation == 'delete':
                for data in ingredients_data:
                    try:
                        ingredient = Ingredient.objects.get(
                            id=data['id'], 
                            user=request.user
                        )
                        ingredient.delete()
                        results['success'].append({'id': data['id']})
                    except Ingredient.DoesNotExist:
                        results['errors'].append({
                            'data': data,
                            'errors': {'id': 'Ingredient not found'}
                        })
        
        return success_response(
            data=results,
            message=f'Bulk {operation} completed'
        )
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Get unique categories used by user's ingredients
        """
        categories = self.get_queryset().values_list(
            'category', flat=True
        ).distinct().exclude(category__isnull=True).exclude(category='')
        
        # Also include predefined categories
        predefined_categories = IngredientCategory.objects.all()
        
        return success_response(
            data={
                'user_categories': sorted(list(categories)),
                'predefined_categories': IngredientCategorySerializer(
                    predefined_categories, many=True
                ).data
            }
        )
    
    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """
        Import ingredients from CSV file
        """
        serializer = IngredientImportSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid file',
                errors=serializer.errors
            )
        
        csv_file = serializer.validated_data['file']
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        
        results = {'success': 0, 'errors': []}
        
        try:
            reader = csv.DictReader(io_string)
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, start=2):
                    # Map CSV columns to model fields
                    ingredient_data = {
                        'name': row.get('name', '').strip(),
                        'quantity': row.get('quantity', '').strip() or None,
                        'unit': row.get('unit', '').strip() or None,
                        'category': row.get('category', '').strip() or None,
                        'expiry_date': row.get('expiry_date', '').strip() or None,
                        'notes': row.get('notes', '').strip() or None,
                    }
                    
                    # Remove None values
                    ingredient_data = {k: v for k, v in ingredient_data.items() if v is not None}
                    
                    if not ingredient_data.get('name'):
                        results['errors'].append({
                            'row': row_num,
                            'error': 'Name is required'
                        })
                        continue
                    
                    ingredient_serializer = IngredientSerializer(data=ingredient_data)
                    
                    if ingredient_serializer.is_valid():
                        ingredient_serializer.save(user=request.user)
                        results['success'] += 1
                    else:
                        results['errors'].append({
                            'row': row_num,
                            'errors': ingredient_serializer.errors
                        })
        
        except Exception as e:
            return error_response(
                message=f'Failed to parse CSV: {str(e)}'
            )
        
        return success_response(
            data=results,
            message=f'Import completed: {results["success"]} ingredients added'
        )
