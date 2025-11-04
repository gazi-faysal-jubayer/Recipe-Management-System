"""
Tests for ingredients app
"""
import pytest
from django.contrib.auth import get_user_model
from apps.ingredients.models import Ingredient
from apps.ingredients.services import IngredientService
from apps.common.utils import normalize_ingredient_name

User = get_user_model()


@pytest.mark.django_db
class TestIngredientModel:
    """Test Ingredient model"""
    
    def test_create_ingredient(self):
        """Test creating an ingredient"""
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        
        ingredient = Ingredient.objects.create(
            user=user,
            name='Tomatoes',
            quantity=5,
            unit='pieces',
            category='Vegetables'
        )
        
        assert ingredient.name == 'Tomatoes'
        assert ingredient.quantity == 5
        assert ingredient.user == user
    
    def test_ingredient_str(self):
        """Test ingredient string representation"""
        user = User.objects.create_user(
            username='test2@example.com',
            email='test2@example.com'
        )
        
        ingredient = Ingredient.objects.create(
            user=user,
            name='Flour',
            quantity=2,
            unit='kg'
        )
        
        assert str(ingredient) == 'Flour (2 kg)'


@pytest.mark.django_db
class TestIngredientService:
    """Test IngredientService"""
    
    def test_normalize_ingredient_name(self):
        """Test ingredient name normalization"""
        assert normalize_ingredient_name('Tomatoes') == 'tomato'
        assert normalize_ingredient_name('ONIONS') == 'onion'
        assert normalize_ingredient_name('Berries') == 'berry'
    
    def test_check_ingredients_availability(self):
        """Test checking ingredient availability"""
        user = User.objects.create_user(
            username='test3@example.com',
            email='test3@example.com'
        )
        
        # Create user ingredients
        Ingredient.objects.create(user=user, name='Pasta')
        Ingredient.objects.create(user=user, name='Tomatoes')
        
        service = IngredientService()
        result = service.check_ingredients_availability(
            user,
            ['Pasta', 'Tomatoes', 'Garlic']
        )
        
        assert len(result['available']) == 2
        assert len(result['missing']) == 1
        assert 'Garlic' in result['missing']
        assert result['match_percentage'] > 0
