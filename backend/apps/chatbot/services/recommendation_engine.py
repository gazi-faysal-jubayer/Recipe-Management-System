"""
Recipe recommendation engine using vector search and ingredient matching
"""
from typing import List, Dict, Optional, Tuple
from django.db import connection
from apps.recipes.models import Recipe
from apps.recipes.services import RecipeService
from apps.ingredients.services import IngredientService
import numpy as np


class RecommendationEngine:
    """Engine for recipe recommendations based on various criteria"""
    
    def __init__(self):
        self.recipe_service = RecipeService()
        self.ingredient_service = IngredientService()
    
    def recommend_by_query(
        self, 
        user, 
        query: str, 
        limit: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Recommend recipes based on semantic search query
        
        Args:
            user: User instance
            query: Search query (e.g., "sweet dessert", "quick Italian dinner")
            limit: Maximum number of recommendations
            filters: Optional filters (cuisine_type, difficulty, etc.)
            
        Returns:
            List of recipe recommendations with scores
        """
        # Generate embedding for query
        query_embedding = self.recipe_service.generate_embedding(query)
        
        # Build filter conditions
        filter_conditions = ["user_id = %s"]
        params = [str(user.id)]
        
        if filters:
            if 'cuisine_type' in filters and filters['cuisine_type']:
                filter_conditions.append("LOWER(cuisine_type) = LOWER(%s)")
                params.append(filters['cuisine_type'])
            
            if 'difficulty' in filters and filters['difficulty']:
                filter_conditions.append("difficulty = %s")
                params.append(filters['difficulty'])
            
            if 'max_time' in filters and filters['max_time']:
                filter_conditions.append("(preparation_time + cooking_time) <= %s")
                params.append(filters['max_time'])
            
            if 'taste_profile' in filters and filters['taste_profile']:
                filter_conditions.append("LOWER(taste_profile) LIKE LOWER(%s)")
                params.append(f"%{filters['taste_profile']}%")
        
        where_clause = " AND ".join(filter_conditions)
        
        # Vector similarity search using pgvector
        with connection.cursor() as cursor:
            query_sql = f"""
                SELECT 
                    id,
                    title,
                    description,
                    cuisine_type,
                    taste_profile,
                    difficulty,
                    preparation_time,
                    cooking_time,
                    1 - (embedding <=> %s::vector) as similarity_score
                FROM recipes
                WHERE {where_clause}
                    AND embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """
            
            params_with_embedding = [
                query_embedding.tolist(),  # For similarity score calculation
                *params,
                query_embedding.tolist(),  # For ordering
                limit
            ]
            
            cursor.execute(query_sql, params_with_embedding)
            
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                recipe_data = dict(zip(columns, row))
                recipe_data['id'] = str(recipe_data['id'])
                
                # Get full recipe object
                try:
                    recipe = Recipe.objects.get(id=recipe_data['id'])
                    
                    # Check ingredient availability
                    availability = self.ingredient_service.check_ingredients_availability(
                        user, 
                        recipe.ingredient_names
                    )
                    
                    results.append({
                        'recipe': recipe,
                        'similarity_score': float(recipe_data['similarity_score']),
                        'match_percentage': availability['match_percentage'],
                        'available_ingredients': availability['available'],
                        'missing_ingredients': availability['missing']
                    })
                except Recipe.DoesNotExist:
                    continue
        
        return results
    
    def recommend_by_ingredients(
        self, 
        user, 
        min_match_percentage: float = 50.0,
        limit: int = 10
    ) -> List[Dict]:
        """
        Recommend recipes based on available ingredients
        
        Args:
            user: User instance
            min_match_percentage: Minimum ingredient match percentage
            limit: Maximum number of recommendations
            
        Returns:
            List of recipe recommendations
        """
        # Get recipes with ingredient matching
        matches = self.recipe_service.search_recipes_by_available_ingredients(user, limit * 2)
        
        # Filter by minimum match percentage
        filtered_matches = [
            match for match in matches 
            if match['match_percentage'] >= min_match_percentage
        ]
        
        return filtered_matches[:limit]
    
    def recommend_by_preferences(
        self,
        user,
        preferences: Dict,
        limit: int = 5
    ) -> List[Dict]:
        """
        Recommend recipes based on user preferences
        
        Args:
            user: User instance
            preferences: Dict with taste_profile, cuisine_type, etc.
            limit: Maximum number of recommendations
            
        Returns:
            List of recipe recommendations
        """
        # Build a descriptive query from preferences
        query_parts = []
        
        if 'taste_profile' in preferences:
            query_parts.append(preferences['taste_profile'])
        
        if 'cuisine_type' in preferences:
            query_parts.append(f"{preferences['cuisine_type']} cuisine")
        
        if 'meal_type' in preferences:
            query_parts.append(preferences['meal_type'])
        
        if 'dietary_restrictions' in preferences:
            query_parts.extend(preferences['dietary_restrictions'])
        
        query = " ".join(query_parts)
        
        # Use semantic search with preferences as filters
        return self.recommend_by_query(user, query, limit, preferences)
    
    def get_similar_recipes(
        self,
        user,
        recipe_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Find recipes similar to a given recipe
        
        Args:
            user: User instance
            recipe_id: ID of the reference recipe
            limit: Maximum number of similar recipes
            
        Returns:
            List of similar recipes
        """
        try:
            # Get the reference recipe
            reference_recipe = Recipe.objects.get(id=recipe_id, user=user)
            
            if not reference_recipe.embedding:
                # Fallback to text-based search
                query = f"{reference_recipe.title} {reference_recipe.cuisine_type} {reference_recipe.taste_profile}"
                return self.recommend_by_query(user, query, limit + 1)[1:]  # Exclude self
            
            # Vector similarity search
            with connection.cursor() as cursor:
                query_sql = """
                    SELECT 
                        id,
                        title,
                        1 - (embedding <=> %s::vector) as similarity_score
                    FROM recipes
                    WHERE user_id = %s
                        AND id != %s
                        AND embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """
                
                params = [
                    reference_recipe.embedding,
                    str(user.id),
                    str(recipe_id),
                    reference_recipe.embedding,
                    limit
                ]
                
                cursor.execute(query_sql, params)
                
                results = []
                for row in cursor.fetchall():
                    recipe = Recipe.objects.get(id=row[0])
                    
                    # Check ingredients
                    availability = self.ingredient_service.check_ingredients_availability(
                        user, 
                        recipe.ingredient_names
                    )
                    
                    results.append({
                        'recipe': recipe,
                        'similarity_score': float(row[2]),
                        'match_percentage': availability['match_percentage'],
                        'available_ingredients': availability['available'],
                        'missing_ingredients': availability['missing']
                    })
                
                return results
                
        except Recipe.DoesNotExist:
            return []
    
    def generate_meal_plan(
        self,
        user,
        days: int = 7,
        meals_per_day: int = 3
    ) -> Dict[str, List[Dict]]:
        """
        Generate a meal plan for specified days
        
        Args:
            user: User instance
            days: Number of days to plan
            meals_per_day: Number of meals per day
            
        Returns:
            Dict with days as keys and recipe lists as values
        """
        meal_types = ['breakfast', 'lunch', 'dinner'][:meals_per_day]
        meal_plan = {}
        
        # Get all available recipes with good ingredient matches
        available_recipes = self.recommend_by_ingredients(user, min_match_percentage=70.0, limit=50)
        
        # Organize recipes by meal type hints
        breakfast_recipes = []
        lunch_recipes = []
        dinner_recipes = []
        any_meal_recipes = []
        
        for recipe_match in available_recipes:
            recipe = recipe_match['recipe']
            title_lower = recipe.title.lower()
            desc_lower = (recipe.description or '').lower()
            combined = title_lower + ' ' + desc_lower
            
            if any(word in combined for word in ['breakfast', 'morning', 'pancake', 'cereal', 'omelette']):
                breakfast_recipes.append(recipe_match)
            elif any(word in combined for word in ['lunch', 'sandwich', 'salad', 'soup']):
                lunch_recipes.append(recipe_match)
            elif any(word in combined for word in ['dinner', 'main course', 'pasta', 'roast']):
                dinner_recipes.append(recipe_match)
            else:
                any_meal_recipes.append(recipe_match)
        
        # Generate meal plan
        for day in range(days):
            day_key = f"day_{day + 1}"
            day_meals = []
            
            for meal_idx, meal_type in enumerate(meal_types):
                # Select from appropriate category
                if meal_type == 'breakfast' and breakfast_recipes:
                    selected = breakfast_recipes[day % len(breakfast_recipes)]
                elif meal_type == 'lunch' and lunch_recipes:
                    selected = lunch_recipes[day % len(lunch_recipes)]
                elif meal_type == 'dinner' and dinner_recipes:
                    selected = dinner_recipes[day % len(dinner_recipes)]
                elif any_meal_recipes:
                    selected = any_meal_recipes[(day * meals_per_day + meal_idx) % len(any_meal_recipes)]
                else:
                    continue
                
                day_meals.append({
                    'meal_type': meal_type,
                    'recipe': selected['recipe'],
                    'match_percentage': selected['match_percentage'],
                    'missing_ingredients': selected['missing_ingredients']
                })
            
            meal_plan[day_key] = day_meals
        
        return meal_plan
