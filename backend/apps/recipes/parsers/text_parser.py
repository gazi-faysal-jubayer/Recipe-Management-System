"""
Text parser for extracting recipe information using LLM
"""
import json
from typing import Dict, Any, Optional
from groq import Groq
from django.conf import settings
from pydantic import BaseModel, Field
from typing import List

# Initialize Groq client
groq_client = Groq(api_key=settings.GROQ_API_KEY)


class RecipeIngredient(BaseModel):
    """Model for recipe ingredient"""
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None


class ParsedRecipe(BaseModel):
    """Model for parsed recipe data"""
    title: str
    description: Optional[str] = None
    ingredients: List[RecipeIngredient]
    instructions: str
    cuisine_type: Optional[str] = None
    taste_profile: Optional[str] = None
    preparation_time: Optional[int] = Field(None, description="Prep time in minutes")
    cooking_time: Optional[int] = Field(None, description="Cooking time in minutes")
    servings: Optional[int] = None
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")


class RecipeTextParser:
    """Parse recipe text using Groq LLM"""
    
    SYSTEM_PROMPT = """You are a recipe parsing assistant. Your task is to extract structured recipe information from unstructured text.
    
    Extract the following information:
    1. Title: The name of the recipe
    2. Description: A brief description (if available)
    3. Ingredients: List with name, quantity, unit, and any notes
    4. Instructions: Step-by-step cooking instructions
    5. Cuisine type: (e.g., Italian, Chinese, Indian, American, etc.)
    6. Taste profile: (e.g., sweet, savory, spicy, tangy, etc.)
    7. Preparation time: In minutes
    8. Cooking time: In minutes
    9. Servings: Number of servings
    10. Difficulty: easy, medium, or hard
    
    Important guidelines:
    - If information is not available, use null
    - For ingredients, try to extract exact quantities and units
    - Combine multiple instruction steps into a single text with numbered steps
    - Ensure difficulty is only one of: easy, medium, hard
    - Times should be in minutes (convert hours if needed)
    
    Return the data as a valid JSON object matching this structure:
    {
        "title": "Recipe Name",
        "description": "Brief description",
        "ingredients": [
            {"name": "ingredient 1", "quantity": 2, "unit": "cups", "notes": "optional notes"},
            {"name": "ingredient 2", "quantity": 1, "unit": "tbsp", "notes": null}
        ],
        "instructions": "1. First step\\n2. Second step\\n3. Third step",
        "cuisine_type": "Italian",
        "taste_profile": "savory",
        "preparation_time": 15,
        "cooking_time": 30,
        "servings": 4,
        "difficulty": "medium"
    }"""
    
    def __init__(self, model: str = "llama-3.1-70b-versatile"):
        self.model = model
    
    def parse(self, recipe_text: str) -> ParsedRecipe:
        """
        Parse recipe text and return structured data
        
        Args:
            recipe_text: Unstructured recipe text
            
        Returns:
            ParsedRecipe object with extracted information
            
        Raises:
            Exception: If parsing fails
        """
        try:
            # Call Groq API
            response = groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"Please parse this recipe:\n\n{recipe_text}"}
                ],
                temperature=0.1,  # Low temperature for consistent parsing
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Extract JSON from response
            content = response.choices[0].message.content
            parsed_data = json.loads(content)
            
            # Convert to Pydantic model for validation
            return ParsedRecipe(**parsed_data)
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Recipe parsing failed: {str(e)}")
    
    def parse_batch(self, recipes: List[str]) -> List[ParsedRecipe]:
        """
        Parse multiple recipes
        
        Args:
            recipes: List of recipe texts
            
        Returns:
            List of ParsedRecipe objects
        """
        results = []
        
        for recipe_text in recipes:
            try:
                parsed = self.parse(recipe_text)
                results.append(parsed)
            except Exception as e:
                # Log error but continue with other recipes
                print(f"Failed to parse recipe: {str(e)}")
                continue
        
        return results
    
    def extract_ingredients_list(self, recipe_text: str) -> List[str]:
        """
        Quick extraction of just ingredient names
        
        Args:
            recipe_text: Recipe text
            
        Returns:
            List of ingredient names
        """
        try:
            response = groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Extract only the ingredient names from the recipe. Return as a JSON array of strings."
                    },
                    {"role": "user", "content": recipe_text}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Handle different response formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'ingredients' in data:
                return data['ingredients']
            else:
                return []
                
        except Exception:
            return []
