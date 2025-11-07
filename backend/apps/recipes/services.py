"""
Service layer for recipes app
"""
from typing import List, Dict, Optional, Tuple
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from sentence_transformers import SentenceTransformer
import numpy as np
from .models import Recipe
from .parsers.text_parser import RecipeTextParser, ParsedRecipe
from .parsers.image_parser import RecipeImageParser
from apps.ingredients.services import IngredientService
import re

# Lazy load sentence transformer model
_embedding_model = None

def get_embedding_model():
    """Lazy load the embedding model only when needed"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model


class RecipeService:
    """Service for recipe-related operations"""
    
    def __init__(self):
        self.text_parser = RecipeTextParser()
        self.image_parser = RecipeImageParser(self.text_parser)
        self.ingredient_service = IngredientService()
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for text
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of embeddings
        """
        # Combine relevant text for embedding
        model = get_embedding_model()
        embedding = model.encode(text)
        return embedding
    
    def create_recipe_from_parsed(self, user, parsed_recipe: ParsedRecipe, source_type: str, raw_text: str = "") -> Recipe:
        """
        Create recipe from parsed data
        
        Args:
            user: User instance
            parsed_recipe: ParsedRecipe object
            source_type: Source type (text, image, manual)
            raw_text: Original text (optional)
            
        Returns:
            Created Recipe instance
        """
        # Convert ingredients to JSON format
        ingredients_json = {
            'items': [ing.dict() for ing in parsed_recipe.ingredients]
        }
        
        # Generate embedding from title, description, and ingredients
        embedding_text = f"{parsed_recipe.title} {parsed_recipe.description or ''} {' '.join([ing.name for ing in parsed_recipe.ingredients])}"
        embedding = self.generate_embedding(embedding_text)
        
        # Create recipe
        recipe = Recipe.objects.create(
            user=user,
            title=parsed_recipe.title,
            description=parsed_recipe.description or "",
            ingredients=ingredients_json,
            instructions=parsed_recipe.instructions,
            cuisine_type=parsed_recipe.cuisine_type or "",
            taste_profile=parsed_recipe.taste_profile or "",
            preparation_time=parsed_recipe.preparation_time,
            cooking_time=parsed_recipe.cooking_time,
            servings=parsed_recipe.servings,
            difficulty=parsed_recipe.difficulty or "medium",
            source_type=source_type,
            raw_text=raw_text,
            embedding=embedding.tolist()
        )
        
        return recipe
    
    def parse_text_recipe(self, user, recipe_text: str) -> Recipe:
        """
        Parse and create recipe from text
        
        Args:
            user: User instance
            recipe_text: Recipe text
            
        Returns:
            Created Recipe instance
        """
        parsed_recipe = self.text_parser.parse(recipe_text)
        return self.create_recipe_from_parsed(user, parsed_recipe, 'text', recipe_text)
    
    def parse_image_recipe(self, user, image_file: UploadedFile) -> Tuple[Recipe, str]:
        """
        Parse and create recipe from image
        
        Args:
            user: User instance
            image_file: Uploaded image file
            
        Returns:
            Tuple of (Recipe, extracted_text)
        """
        # Read image bytes
        image_bytes = image_file.read()
        
        # Parse image
        parsed_recipe, extracted_text = self.image_parser.parse_image_bytes(image_bytes)
        
        # Create recipe
        recipe = self.create_recipe_from_parsed(user, parsed_recipe, 'image', extracted_text)
        
        return recipe, extracted_text
    
    def batch_import_recipes(self, user, combined_text: str, progress_callback=None) -> List[Recipe]:
        """
        Import multiple recipes from combined text file
        
        Args:
            user: User instance
            combined_text: Combined recipe text
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of created Recipe instances
        """
        # Split recipes by common delimiters
        recipe_chunks = self._split_recipe_text(combined_text)
        
        recipes = []
        total = len(recipe_chunks)
        
        with transaction.atomic():
            for i, chunk in enumerate(recipe_chunks):
                try:
                    # Skip empty chunks
                    if not chunk.strip():
                        continue
                    
                    # Parse and create recipe
                    parsed_recipe = self.text_parser.parse(chunk)
                    recipe = self.create_recipe_from_parsed(user, parsed_recipe, 'text', chunk)
                    recipes.append(recipe)
                    
                    # Update progress
                    if progress_callback:
                        progress_callback(i + 1, total)
                        
                except Exception as e:
                    # Log error but continue with other recipes
                    print(f"Failed to import recipe chunk {i+1}: {str(e)}")
                    continue
        
        return recipes
    
    def _split_recipe_text(self, text: str) -> List[str]:
        """
        Split combined recipe text into individual recipes
        
        Args:
            text: Combined recipe text
            
        Returns:
            List of recipe text chunks
        """
        # Common recipe separators
        separators = [
            r'\n={3,}\n',  # Three or more equals signs
            r'\n-{3,}\n',  # Three or more dashes
            r'\n\*{3,}\n', # Three or more asterisks
            r'\n#{2,}\s',  # Two or more hash marks (markdown headers)
            r'Recipe \d+:',  # "Recipe 1:", "Recipe 2:", etc.
            r'\n\n\n+',     # Three or more newlines
        ]
        
        # Try each separator pattern
        for separator in separators:
            chunks = re.split(separator, text)
            if len(chunks) > 1:
                return [chunk.strip() for chunk in chunks if chunk.strip()]
        
        # If no separator found, treat as single recipe
        return [text.strip()]
    
    def search_recipes_by_available_ingredients(self, user, limit: int = 10) -> List[Dict]:
        """
        Find recipes that can be made with available ingredients
        
        Args:
            user: User instance
            limit: Maximum number of recipes to return
            
        Returns:
            List of recipe data with match information
        """
        # Get user's available ingredients
        user_ingredients = self.ingredient_service.get_user_ingredients_normalized(user)
        
        # Get all user's recipes
        recipes = Recipe.objects.filter(user=user)
        
        recipe_matches = []
        
        for recipe in recipes:
            # Check ingredient availability
            availability = self.ingredient_service.check_ingredients_availability(
                user, 
                recipe.ingredient_names
            )
            
            # Only include recipes with >0% match
            if availability['match_percentage'] > 0:
                recipe_matches.append({
                    'recipe': recipe,
                    'match_percentage': availability['match_percentage'],
                    'available_ingredients': availability['available'],
                    'missing_ingredients': availability['missing']
                })
        
        # Sort by match percentage
        recipe_matches.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return recipe_matches[:limit]
    
    def search_recipes_by_query(self, user, query: str, filters: Dict = None) -> List[Recipe]:
        """
        Search recipes using text query and filters
        
        Args:
            user: User instance
            query: Search query
            filters: Optional filters (cuisine_type, difficulty, max_time, etc.)
            
        Returns:
            List of matching Recipe instances
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(query)
        
        # Start with user's recipes
        queryset = Recipe.objects.filter(user=user)
        
        # Apply filters
        if filters:
            if 'cuisine_type' in filters:
                queryset = queryset.filter(cuisine_type__icontains=filters['cuisine_type'])
            
            if 'difficulty' in filters:
                queryset = queryset.filter(difficulty=filters['difficulty'])
            
            if 'max_time' in filters:
                # Filter by total time (prep + cooking)
                from django.db.models import F, Q
                queryset = queryset.annotate(
                    total_time=F('preparation_time') + F('cooking_time')
                ).filter(
                    Q(total_time__lte=filters['max_time']) | 
                    Q(total_time__isnull=True)
                )
            
            if 'taste_profile' in filters:
                queryset = queryset.filter(taste_profile__icontains=filters['taste_profile'])
        
        # Vector similarity search would go here if using pgvector
        # For now, use text search
        from django.db.models import Q
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(cuisine_type__icontains=query) |
            Q(taste_profile__icontains=query)
        )
        
        return queryset
