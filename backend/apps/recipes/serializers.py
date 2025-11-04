"""
Serializers for recipes app
"""
from rest_framework import serializers
from .models import Recipe, RecipeFavorite


class RecipeIngredientSerializer(serializers.Serializer):
    """Serializer for recipe ingredients"""
    name = serializers.CharField()
    quantity = serializers.FloatField(required=False, allow_null=True)
    unit = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model"""
    ingredient_names = serializers.ReadOnlyField()
    total_time = serializers.ReadOnlyField()
    is_favorite = serializers.SerializerMethodField()
    ingredients_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'ingredients', 'ingredients_formatted',
            'instructions', 'cuisine_type', 'taste_profile', 
            'preparation_time', 'cooking_time', 'total_time',
            'servings', 'difficulty', 'image_url', 'source_type',
            'ingredient_names', 'is_favorite', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'embedding']
    
    def get_is_favorite(self, obj):
        """Check if recipe is favorited by current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return RecipeFavorite.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False
    
    def get_ingredients_formatted(self, obj):
        """Format ingredients for display"""
        if isinstance(obj.ingredients, dict) and 'items' in obj.ingredients:
            items = obj.ingredients['items']
        elif isinstance(obj.ingredients, list):
            items = obj.ingredients
        else:
            return []
        
        formatted = []
        for item in items:
            if isinstance(item, dict):
                # Format: "2 cups flour (sifted)"
                parts = []
                if item.get('quantity'):
                    parts.append(str(item['quantity']))
                if item.get('unit'):
                    parts.append(item['unit'])
                parts.append(item.get('name', ''))
                
                formatted_str = ' '.join(parts)
                if item.get('notes'):
                    formatted_str += f" ({item['notes']})"
                
                formatted.append(formatted_str)
        
        return formatted


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating recipes manually"""
    ingredients = serializers.ListField(
        child=RecipeIngredientSerializer(),
        allow_empty=False
    )
    
    class Meta:
        model = Recipe
        fields = [
            'title', 'description', 'ingredients', 'instructions',
            'cuisine_type', 'taste_profile', 'preparation_time',
            'cooking_time', 'servings', 'difficulty', 'image_url'
        ]
    
    def create(self, validated_data):
        # Convert ingredients to stored format
        ingredients_data = validated_data.pop('ingredients')
        validated_data['ingredients'] = {
            'items': [dict(ing) for ing in ingredients_data]
        }
        
        # Generate embedding
        from .services import RecipeService
        service = RecipeService()
        
        embedding_text = f"{validated_data['title']} {validated_data.get('description', '')} {' '.join([ing['name'] for ing in ingredients_data])}"
        embedding = service.generate_embedding(embedding_text)
        validated_data['embedding'] = embedding.tolist()
        
        # Set source type
        validated_data['source_type'] = 'manual'
        
        return super().create(validated_data)


class RecipeParseTextSerializer(serializers.Serializer):
    """Serializer for parsing recipe from text"""
    text = serializers.CharField(required=True)


class RecipeParseImageSerializer(serializers.Serializer):
    """Serializer for parsing recipe from image"""
    image = serializers.ImageField(required=True)
    
    def validate_image(self, value):
        # Validate file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image size should not exceed 10MB")
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(f"Invalid image type. Allowed types: {', '.join(allowed_types)}")
        
        return value


class RecipeBatchImportSerializer(serializers.Serializer):
    """Serializer for batch importing recipes"""
    file = serializers.FileField(required=False)
    text = serializers.CharField(required=False)
    
    def validate(self, data):
        if not data.get('file') and not data.get('text'):
            raise serializers.ValidationError("Either file or text must be provided")
        
        if data.get('file'):
            # Validate file size (max 50MB for batch import)
            if data['file'].size > 50 * 1024 * 1024:
                raise serializers.ValidationError("File size should not exceed 50MB")
            
            # Read file content
            try:
                content = data['file'].read().decode('utf-8')
                data['text'] = content
            except Exception:
                raise serializers.ValidationError("Failed to read file. Ensure it's a valid text file.")
        
        return data


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for recipe favorites"""
    recipe = RecipeSerializer(read_only=True)
    
    class Meta:
        model = RecipeFavorite
        fields = ['id', 'recipe', 'created_at']
        read_only_fields = ['id', 'created_at']


class RecipeSearchSerializer(serializers.Serializer):
    """Serializer for recipe search"""
    query = serializers.CharField(required=False, allow_blank=True)
    cuisine_type = serializers.CharField(required=False)
    difficulty = serializers.ChoiceField(choices=['easy', 'medium', 'hard'], required=False)
    max_time = serializers.IntegerField(required=False, min_value=0)
    taste_profile = serializers.CharField(required=False)
    has_all_ingredients = serializers.BooleanField(required=False, default=False)
