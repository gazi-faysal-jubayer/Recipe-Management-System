"""
Serializers for chatbot app
"""
from rest_framework import serializers
from .models import ChatHistory
from apps.recipes.serializers import RecipeSerializer


class ChatMessageSerializer(serializers.Serializer):
    """Serializer for incoming chat messages"""
    message = serializers.CharField(required=True, max_length=2000)
    context = serializers.JSONField(required=False, default=dict)


class ChatHistorySerializer(serializers.ModelSerializer):
    """Serializer for chat history"""
    recommended_recipes_details = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatHistory
        fields = [
            'id', 'message', 'response', 'context', 
            'recommended_recipes', 'recommended_recipes_details',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_recommended_recipes_details(self, obj):
        """Get full recipe details for recommended recipes"""
        if not obj.recommended_recipes:
            return []
        
        from apps.recipes.models import Recipe
        recipes = Recipe.objects.filter(
            id__in=obj.recommended_recipes,
            user=obj.user
        )
        
        return RecipeSerializer(recipes, many=True, context=self.context).data


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat responses"""
    response = serializers.CharField()
    recommended_recipes = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    context = serializers.JSONField(required=False, default=dict)
    chat_id = serializers.UUIDField(required=False)


class RecipeRecommendationRequestSerializer(serializers.Serializer):
    """Serializer for recipe recommendation requests"""
    query = serializers.CharField(required=False, allow_blank=True)
    cuisine_type = serializers.CharField(required=False)
    difficulty = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard'], 
        required=False
    )
    max_time = serializers.IntegerField(required=False, min_value=0)
    taste_profile = serializers.CharField(required=False)
    min_match_percentage = serializers.FloatField(
        required=False, 
        default=50.0,
        min_value=0,
        max_value=100
    )
    limit = serializers.IntegerField(
        required=False,
        default=5,
        min_value=1,
        max_value=20
    )


class MealPlanRequestSerializer(serializers.Serializer):
    """Serializer for meal plan requests"""
    days = serializers.IntegerField(
        required=False,
        default=7,
        min_value=1,
        max_value=30
    )
    meals_per_day = serializers.IntegerField(
        required=False,
        default=3,
        min_value=1,
        max_value=5
    )
