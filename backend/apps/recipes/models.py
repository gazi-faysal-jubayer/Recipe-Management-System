"""
Models for recipes app
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.validators import validate_recipe_difficulty, validate_image_url
from pgvector.django import VectorField
import uuid

User = get_user_model()


class Recipe(models.Model):
    """Recipe model matching Supabase schema"""
    
    SOURCE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('manual', 'Manual'),
    )
    
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    ingredients = models.JSONField()  # Stores list of ingredient objects
    instructions = models.TextField()
    cuisine_type = models.CharField(max_length=100, blank=True)
    taste_profile = models.CharField(max_length=100, blank=True)
    preparation_time = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Preparation time in minutes"
    )
    cooking_time = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Cooking time in minutes"
    )
    servings = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    difficulty = models.CharField(
        max_length=50,
        choices=DIFFICULTY_CHOICES,
        blank=True,
        validators=[validate_recipe_difficulty]
    )
    image_url = models.TextField(blank=True, validators=[validate_image_url])
    source_type = models.CharField(
        max_length=50,
        choices=SOURCE_TYPES,
        default='manual'
    )
    raw_text = models.TextField(blank=True, help_text="Original parsed text")
    embedding = VectorField(dimensions=384, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'recipes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'cuisine_type']),
            models.Index(fields=['user', 'difficulty']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def total_time(self):
        """Calculate total cooking time"""
        prep = self.preparation_time or 0
        cook = self.cooking_time or 0
        return prep + cook
    
    @property
    def ingredient_names(self):
        """Get list of ingredient names"""
        if isinstance(self.ingredients, list):
            return [ing.get('name', '') for ing in self.ingredients if isinstance(ing, dict)]
        elif isinstance(self.ingredients, dict) and 'items' in self.ingredients:
            return [ing.get('name', '') for ing in self.ingredients['items'] if isinstance(ing, dict)]
        return []


class RecipeFavorite(models.Model):
    """Recipe favorites model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recipe_favorites'
        unique_together = ['user', 'recipe']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.recipe.title}"
