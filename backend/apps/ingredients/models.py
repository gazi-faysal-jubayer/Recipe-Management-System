"""
Models for ingredients app
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from apps.common.validators import validate_unit
import uuid

User = get_user_model()


class IngredientCategory(models.Model):
    """Ingredient category model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ingredient_categories'
        ordering = ['display_order', 'name']
        verbose_name_plural = 'Ingredient categories'
    
    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient model matching Supabase schema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=255)
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    unit = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        validators=[validate_unit]
    )
    category = models.CharField(max_length=100, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ingredients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'expiry_date']),
            models.Index(fields=['user', 'name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})" if self.quantity else self.name
    
    @property
    def is_expiring_soon(self):
        """Check if ingredient is expiring within 7 days"""
        if not self.expiry_date:
            return False
        
        from datetime import date, timedelta
        return self.expiry_date <= date.today() + timedelta(days=7)
    
    @property
    def is_expired(self):
        """Check if ingredient is expired"""
        if not self.expiry_date:
            return False
        
        from datetime import date
        return self.expiry_date < date.today()
