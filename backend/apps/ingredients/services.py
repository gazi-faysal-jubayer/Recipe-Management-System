"""
Service layer for ingredients app
"""
from typing import List, Dict
from django.db.models import QuerySet
from .models import Ingredient
from apps.common.utils import normalize_ingredient_name


class IngredientService:
    """Service for ingredient-related operations"""
    
    @staticmethod
    def get_user_ingredients_normalized(user) -> List[str]:
        """
        Get normalized list of user's ingredient names
        
        Args:
            user: User instance
            
        Returns:
            List of normalized ingredient names
        """
        ingredients = Ingredient.objects.filter(user=user).values_list('name', flat=True)
        return [normalize_ingredient_name(ing) for ing in ingredients]
    
    @staticmethod
    def check_ingredients_availability(user, required_ingredients: List[str]) -> Dict:
        """
        Check which ingredients are available and which are missing
        
        Args:
            user: User instance
            required_ingredients: List of required ingredient names
            
        Returns:
            Dict with 'available' and 'missing' ingredient lists
        """
        user_ingredients = IngredientService.get_user_ingredients_normalized(user)
        
        available = []
        missing = []
        
        for ingredient in required_ingredients:
            normalized = normalize_ingredient_name(ingredient)
            if normalized in user_ingredients:
                available.append(ingredient)
            else:
                missing.append(ingredient)
        
        return {
            'available': available,
            'missing': missing,
            'match_percentage': (len(available) / len(required_ingredients)) * 100 if required_ingredients else 0
        }
    
    @staticmethod
    def update_quantities_after_cooking(user, recipe_ingredients: List[Dict]) -> List[Dict]:
        """
        Update ingredient quantities after cooking a recipe
        
        Args:
            user: User instance
            recipe_ingredients: List of dicts with 'name', 'quantity', 'unit'
            
        Returns:
            List of update results
        """
        results = []
        
        for recipe_ing in recipe_ingredients:
            normalized_name = normalize_ingredient_name(recipe_ing['name'])
            
            # Find matching user ingredient
            user_ingredients = Ingredient.objects.filter(user=user)
            
            for user_ing in user_ingredients:
                if normalize_ingredient_name(user_ing.name) == normalized_name:
                    # Update quantity if units match
                    if user_ing.unit == recipe_ing.get('unit'):
                        new_quantity = float(user_ing.quantity or 0) - float(recipe_ing.get('quantity', 0))
                        
                        if new_quantity <= 0:
                            user_ing.delete()
                            results.append({
                                'ingredient': recipe_ing['name'],
                                'action': 'deleted',
                                'reason': 'quantity depleted'
                            })
                        else:
                            user_ing.quantity = new_quantity
                            user_ing.save()
                            results.append({
                                'ingredient': recipe_ing['name'],
                                'action': 'updated',
                                'new_quantity': new_quantity
                            })
                    else:
                        results.append({
                            'ingredient': recipe_ing['name'],
                            'action': 'skipped',
                            'reason': 'unit mismatch'
                        })
                    break
            else:
                results.append({
                    'ingredient': recipe_ing['name'],
                    'action': 'not_found',
                    'reason': 'ingredient not in inventory'
                })
        
        return results
