"""
Shopping list views for recipes app
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Recipe
from .serializers import RecipeSerializer
from apps.common.utils import success_response, error_response
from apps.ingredients.models import Ingredient
from supabase import create_client
from django.conf import settings
import uuid

# Initialize Supabase client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shopping_list(request):
    """Get user's shopping list"""
    try:
        # Query shopping list from Supabase
        response = supabase.table('shopping_list').select('*').eq(
            'user_id', str(request.user.id)
        ).order('created_at', desc=True).execute()
        
        # Group by purchased status
        items = response.data
        unpurchased = [item for item in items if not item.get('purchased', False)]
        purchased = [item for item in items if item.get('purchased', False)]
        
        return success_response(
            data={
                'unpurchased': unpurchased,
                'purchased': purchased,
                'total_count': len(items),
                'unpurchased_count': len(unpurchased),
                'purchased_count': len(purchased)
            }
        )
    except Exception as e:
        return error_response(
            message=f'Failed to fetch shopping list: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item(request):
    """Add item to shopping list"""
    ingredient_name = request.data.get('ingredient_name')
    
    if not ingredient_name:
        return error_response(
            message='Ingredient name is required',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create shopping list item in Supabase
        item_data = {
            'user_id': str(request.user.id),
            'ingredient_name': ingredient_name,
            'quantity': request.data.get('quantity'),
            'unit': request.data.get('unit'),
            'notes': request.data.get('notes', ''),
            'purchased': False,
            'recipe_id': request.data.get('recipe_id')
        }
        
        response = supabase.table('shopping_list').insert(item_data).execute()
        
        return success_response(
            data=response.data[0] if response.data else None,
            message='Item added to shopping list',
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return error_response(
            message=f'Failed to add item: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_purchased(request, item_id):
    """Toggle purchased status of shopping list item"""
    try:
        # First verify the item belongs to the user
        check_response = supabase.table('shopping_list').select('*').eq(
            'id', str(item_id)
        ).eq('user_id', str(request.user.id)).execute()
        
        if not check_response.data:
            return error_response(
                message='Item not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        current_item = check_response.data[0]
        new_purchased_status = not current_item.get('purchased', False)
        
        # Update the item
        response = supabase.table('shopping_list').update({
            'purchased': new_purchased_status
        }).eq('id', str(item_id)).eq('user_id', str(request.user.id)).execute()
        
        return success_response(
            data=response.data[0] if response.data else None,
            message=f'Item marked as {"purchased" if new_purchased_status else "unpurchased"}'
        )
    except Exception as e:
        return error_response(
            message=f'Failed to update item: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_item(request, item_id):
    """Delete item from shopping list"""
    try:
        # Delete the item (RLS will ensure user owns it)
        response = supabase.table('shopping_list').delete().eq(
            'id', str(item_id)
        ).eq('user_id', str(request.user.id)).execute()
        
        return success_response(
            message='Item removed from shopping list',
            status_code=status.HTTP_204_NO_CONTENT
        )
    except Exception as e:
        return error_response(
            message=f'Failed to delete item: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_from_recipe(request, recipe_id):
    """Add all ingredients from a recipe to shopping list"""
    # Get recipe
    recipe = get_object_or_404(Recipe, id=recipe_id, user=request.user)
    
    try:
        # Extract ingredients
        if isinstance(recipe.ingredients, dict) and 'items' in recipe.ingredients:
            ingredients = recipe.ingredients['items']
        elif isinstance(recipe.ingredients, list):
            ingredients = recipe.ingredients
        else:
            return error_response(
                message='Recipe has no ingredients',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        added_items = []
        
        # Add each ingredient to shopping list
        for ingredient in ingredients:
            if isinstance(ingredient, dict) and ingredient.get('name'):
                item_data = {
                    'user_id': str(request.user.id),
                    'ingredient_name': ingredient['name'],
                    'quantity': ingredient.get('quantity'),
                    'unit': ingredient.get('unit'),
                    'notes': ingredient.get('notes', ''),
                    'purchased': False,
                    'recipe_id': str(recipe_id)
                }
                
                response = supabase.table('shopping_list').insert(item_data).execute()
                if response.data:
                    added_items.append(response.data[0])
        
        return success_response(
            data={
                'added_count': len(added_items),
                'items': added_items
            },
            message=f'Added {len(added_items)} items from recipe'
        )
        
    except Exception as e:
        return error_response(
            message=f'Failed to add items from recipe: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_purchased(request):
    """Clear all purchased items from shopping list"""
    try:
        # Delete all purchased items for user
        response = supabase.table('shopping_list').delete().eq(
            'user_id', str(request.user.id)
        ).eq('purchased', True).execute()
        
        return success_response(
            message='Purchased items cleared from shopping list'
        )
    except Exception as e:
        return error_response(
            message=f'Failed to clear purchased items: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_purchased_to_ingredients(request):
    """Add purchased items to ingredients inventory"""
    try:
        # Get all purchased items
        response = supabase.table('shopping_list').select('*').eq(
            'user_id', str(request.user.id)
        ).eq('purchased', True).execute()
        
        purchased_items = response.data
        
        if not purchased_items:
            return error_response(
                message='No purchased items to add',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        added_ingredients = []
        
        with transaction.atomic():
            for item in purchased_items:
                # Create ingredient
                ingredient = Ingredient.objects.create(
                    user=request.user,
                    name=item['ingredient_name'],
                    quantity=item.get('quantity'),
                    unit=item.get('unit'),
                    notes=item.get('notes', '')
                )
                added_ingredients.append(ingredient)
                
                # Delete from shopping list
                supabase.table('shopping_list').delete().eq(
                    'id', item['id']
                ).execute()
        
        from apps.ingredients.serializers import IngredientSerializer
        return success_response(
            data={
                'added_count': len(added_ingredients),
                'ingredients': IngredientSerializer(added_ingredients, many=True).data
            },
            message=f'Added {len(added_ingredients)} ingredients to inventory'
        )
        
    except Exception as e:
        return error_response(
            message=f'Failed to add to ingredients: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
