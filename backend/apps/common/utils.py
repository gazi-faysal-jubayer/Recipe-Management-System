"""
Common utility functions
"""
import re
from typing import List, Dict, Any
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework import status


def normalize_ingredient_name(name: str) -> str:
    """
    Normalize ingredient names for better matching
    
    Args:
        name: Raw ingredient name
        
    Returns:
        Normalized ingredient name
    """
    # Convert to lowercase
    name = name.lower().strip()
    
    # Remove common units and quantities
    units_pattern = r'\b\d+\s*(cup|tbsp|tsp|oz|lb|g|kg|ml|l|pound|ounce|gram|kilogram|liter|milliliter)s?\b'
    name = re.sub(units_pattern, '', name)
    
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Convert to singular form (basic)
    if name.endswith('ies'):
        name = name[:-3] + 'y'
    elif name.endswith('es'):
        name = name[:-2]
    elif name.endswith('s') and not name.endswith('ss'):
        name = name[:-1]
    
    return name


def calculate_recipe_match_percentage(
    recipe_ingredients: List[str], 
    available_ingredients: List[str]
) -> float:
    """
    Calculate what percentage of recipe ingredients are available
    
    Args:
        recipe_ingredients: List of ingredients required by recipe
        available_ingredients: List of available ingredients
        
    Returns:
        Match percentage (0-100)
    """
    if not recipe_ingredients:
        return 0.0
    
    # Normalize all ingredient names
    normalized_recipe = [normalize_ingredient_name(ing) for ing in recipe_ingredients]
    normalized_available = [normalize_ingredient_name(ing) for ing in available_ingredients]
    
    # Count matches
    matches = sum(1 for ing in normalized_recipe if ing in normalized_available)
    
    return (matches / len(normalized_recipe)) * 100


def paginate_response(queryset, request, serializer_class):
    """
    Helper function to paginate queryset and return response
    
    Args:
        queryset: Django queryset
        request: DRF request object
        serializer_class: Serializer class to use
        
    Returns:
        Response object with paginated data
    """
    page_size = request.query_params.get('page_size', 20)
    page_number = request.query_params.get('page', 1)
    
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page_number)
    
    serializer = serializer_class(page_obj, many=True)
    
    return Response({
        'results': serializer.data,
        'count': paginator.count,
        'next': page_obj.has_next(),
        'previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    })


def success_response(data: Any = None, message: str = "Success", status_code: int = status.HTTP_200_OK):
    """
    Create a standardized success response
    """
    response_data = {
        'success': True,
        'message': message
    }
    if data is not None:
        response_data['data'] = data
    
    return Response(response_data, status=status_code)


def error_response(message: str = "Error", errors: Dict = None, status_code: int = status.HTTP_400_BAD_REQUEST):
    """
    Create a standardized error response
    """
    response_data = {
        'success': False,
        'message': message
    }
    if errors:
        response_data['errors'] = errors
    
    return Response(response_data, status=status_code)
