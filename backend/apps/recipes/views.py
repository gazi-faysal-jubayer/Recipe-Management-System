"""
Views for recipes app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Recipe, RecipeFavorite
from .serializers import (
    RecipeSerializer, RecipeCreateSerializer, RecipeFavoriteSerializer,
    RecipeParseTextSerializer, RecipeParseImageSerializer,
    RecipeBatchImportSerializer, RecipeSearchSerializer
)
from .services import RecipeService
from apps.common.utils import success_response, error_response
from apps.authentication.permissions import IsOwner
from celery import shared_task
import uuid


# Background task for batch import
@shared_task
def batch_import_task(user_id, text, task_id):
    """Background task for batch recipe import"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        service = RecipeService()
        
        # Import recipes
        recipes = service.batch_import_recipes(user, text)
        
        # Store result in cache
        from django.core.cache import cache
        cache.set(f'import_task_{task_id}', {
            'status': 'completed',
            'count': len(recipes),
            'recipe_ids': [str(r.id) for r in recipes]
        }, 3600)  # Keep for 1 hour
        
    except Exception as e:
        from django.core.cache import cache
        cache.set(f'import_task_{task_id}', {
            'status': 'failed',
            'error': str(e)
        }, 3600)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for recipe CRUD operations"""
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer
    
    def get_queryset(self):
        queryset = Recipe.objects.filter(user=self.request.user)
        
        # Apply filters
        cuisine = self.request.query_params.get('cuisine_type')
        if cuisine:
            queryset = queryset.filter(cuisine_type__icontains=cuisine)
        
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Order by
        ordering = self.request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def parse_text(self, request):
        """Parse recipe from text"""
        serializer = RecipeParseTextSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid input',
                errors=serializer.errors
            )
        
        try:
            service = RecipeService()
            recipe = service.parse_text_recipe(
                request.user,
                serializer.validated_data['text']
            )
            
            return success_response(
                data=RecipeSerializer(recipe, context={'request': request}).data,
                message='Recipe parsed and saved successfully',
                status_code=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return error_response(
                message=f'Failed to parse recipe: {str(e)}',
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def parse_image(self, request):
        """Parse recipe from image"""
        serializer = RecipeParseImageSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid input',
                errors=serializer.errors
            )
        
        try:
            service = RecipeService()
            recipe, extracted_text = service.parse_image_recipe(
                request.user,
                serializer.validated_data['image']
            )
            
            return success_response(
                data={
                    'recipe': RecipeSerializer(recipe, context={'request': request}).data,
                    'extracted_text': extracted_text
                },
                message='Recipe parsed from image successfully',
                status_code=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return error_response(
                message=f'Failed to parse recipe from image: {str(e)}',
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def batch_import(self, request):
        """Import multiple recipes from text file"""
        serializer = RecipeBatchImportSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid input',
                errors=serializer.errors
            )
        
        text = serializer.validated_data['text']
        
        # For large files, use background task
        if len(text) > 100000:  # >100KB
            task_id = str(uuid.uuid4())
            batch_import_task.delay(request.user.id, text, task_id)
            
            return success_response(
                data={'task_id': task_id},
                message='Batch import started in background',
                status_code=status.HTTP_202_ACCEPTED
            )
        
        # For smaller files, process immediately
        try:
            service = RecipeService()
            recipes = service.batch_import_recipes(request.user, text)
            
            return success_response(
                data={
                    'count': len(recipes),
                    'recipes': RecipeSerializer(recipes, many=True, context={'request': request}).data
                },
                message=f'Successfully imported {len(recipes)} recipes'
            )
            
        except Exception as e:
            return error_response(
                message=f'Batch import failed: {str(e)}',
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def import_status(self, request):
        """Check status of batch import task"""
        task_id = request.query_params.get('task_id')
        
        if not task_id:
            return error_response(
                message='Task ID required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        from django.core.cache import cache
        result = cache.get(f'import_task_{task_id}')
        
        if not result:
            return success_response(
                data={'status': 'pending'},
                message='Import still in progress'
            )
        
        return success_response(data=result)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced recipe search"""
        serializer = RecipeSearchSerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return error_response(
                message='Invalid search parameters',
                errors=serializer.errors
            )
        
        service = RecipeService()
        
        # If searching for recipes with all ingredients
        if serializer.validated_data.get('has_all_ingredients'):
            results = service.search_recipes_by_available_ingredients(request.user)
            
            # Format results
            formatted_results = []
            for result in results:
                recipe_data = RecipeSerializer(result['recipe'], context={'request': request}).data
                recipe_data['match_info'] = {
                    'match_percentage': result['match_percentage'],
                    'available_ingredients': result['available_ingredients'],
                    'missing_ingredients': result['missing_ingredients']
                }
                formatted_results.append(recipe_data)
            
            return success_response(
                data={'recipes': formatted_results, 'count': len(formatted_results)}
            )
        
        # Regular search
        filters = {}
        if 'cuisine_type' in serializer.validated_data:
            filters['cuisine_type'] = serializer.validated_data['cuisine_type']
        if 'difficulty' in serializer.validated_data:
            filters['difficulty'] = serializer.validated_data['difficulty']
        if 'max_time' in serializer.validated_data:
            filters['max_time'] = serializer.validated_data['max_time']
        if 'taste_profile' in serializer.validated_data:
            filters['taste_profile'] = serializer.validated_data['taste_profile']
        
        query = serializer.validated_data.get('query', '')
        recipes = service.search_recipes_by_query(request.user, query, filters)
        
        return success_response(
            data={
                'recipes': RecipeSerializer(recipes, many=True, context={'request': request}).data,
                'count': recipes.count()
            }
        )
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """Add recipe to favorites"""
        recipe = self.get_object()
        
        favorite, created = RecipeFavorite.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        
        if created:
            return success_response(
                data=RecipeFavoriteSerializer(favorite).data,
                message='Recipe added to favorites',
                status_code=status.HTTP_201_CREATED
            )
        
        return success_response(
            message='Recipe already in favorites'
        )
    
    @action(detail=True, methods=['delete'])
    def unfavorite(self, request, pk=None):
        """Remove recipe from favorites"""
        recipe = self.get_object()
        
        try:
            favorite = RecipeFavorite.objects.get(
                user=request.user,
                recipe=recipe
            )
            favorite.delete()
            
            return success_response(
                message='Recipe removed from favorites',
                status_code=status.HTTP_204_NO_CONTENT
            )
            
        except RecipeFavorite.DoesNotExist:
            return error_response(
                message='Recipe not in favorites',
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """Get user's favorite recipes"""
        favorites = RecipeFavorite.objects.filter(
            user=request.user
        ).select_related('recipe')
        
        # Apply pagination
        from django.core.paginator import Paginator
        paginator = Paginator(favorites, 20)
        page = request.query_params.get('page', 1)
        
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
        
        return success_response(
            data={
                'results': RecipeFavoriteSerializer(page_obj, many=True).data,
                'count': paginator.count,
                'next': page_obj.has_next(),
                'previous': page_obj.has_previous(),
                'total_pages': paginator.num_pages
            }
        )
