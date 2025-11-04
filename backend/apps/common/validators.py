"""
Common validators for the Recipe Management System
"""
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
import re


def validate_positive_number(value):
    """Validate that a number is positive"""
    if value <= 0:
        raise ValidationError(f'{value} is not a positive number')


def validate_recipe_difficulty(value):
    """Validate recipe difficulty level"""
    valid_difficulties = ['easy', 'medium', 'hard']
    if value not in valid_difficulties:
        raise ValidationError(f'{value} is not a valid difficulty. Choose from: {", ".join(valid_difficulties)}')


def validate_image_url(value):
    """Validate that a URL points to an image"""
    url_validator = URLValidator()
    
    try:
        url_validator(value)
    except ValidationError:
        raise ValidationError('Enter a valid URL')
    
    # Check if URL ends with common image extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    if not any(value.lower().endswith(ext) for ext in image_extensions):
        # Allow Supabase storage URLs
        if 'supabase' not in value:
            raise ValidationError('URL must point to an image file')


def validate_unit(value):
    """Validate measurement units"""
    valid_units = [
        'cup', 'cups', 'tbsp', 'tablespoon', 'tsp', 'teaspoon',
        'oz', 'ounce', 'ounces', 'lb', 'pound', 'pounds',
        'g', 'gram', 'grams', 'kg', 'kilogram', 'kilograms',
        'ml', 'milliliter', 'milliliters', 'l', 'liter', 'liters',
        'piece', 'pieces', 'item', 'items', 'pinch', 'dash',
        'handful', 'bunch', 'package', 'can', 'jar', 'bottle'
    ]
    
    if value and value.lower() not in valid_units:
        raise ValidationError(f'{value} is not a valid unit')
