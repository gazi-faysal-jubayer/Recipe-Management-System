"""
Views for chatbot app
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from django.db import transaction
from .models import ChatHistory
from .serializers import (
    ChatMessageSerializer, ChatHistorySerializer,
    ChatResponseSerializer, RecipeRecommendationRequestSerializer,
    MealPlanRequestSerializer
)
from .services.llm_service import LLMService
from .services.recommendation_engine import RecommendationEngine
from .prompts import (
    RECIPE_ASSISTANT_SYSTEM_PROMPT,
    RECIPE_RECOMMENDATION_PROMPT,
    format_recipe_matches,
    format_ingredients_list,
    format_meal_plan
)
from apps.common.utils import success_response, error_response
from apps.ingredients.models import Ingredient
from apps.recipes.serializers import RecipeSerializer
import json
import asyncio


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_message(request):
    """Process a chat message and return response"""
    serializer = ChatMessageSerializer(data=request.data)
    
    if not serializer.is_valid():
        return error_response(
            message='Invalid message',
            errors=serializer.errors
        )
    
    message = serializer.validated_data['message']
    context = serializer.validated_data.get('context', {})
    
    try:
        # Initialize services
        llm_service = LLMService()
        recommendation_engine = RecommendationEngine()
        
        # Get user's available ingredients
        user_ingredients = Ingredient.objects.filter(user=request.user)
        ingredients_list = format_ingredients_list(user_ingredients)
        
        # Analyze message intent
        intent = _analyze_intent(message)
        
        # Generate appropriate response based on intent
        if intent == 'recipe_recommendation':
            # Extract preferences from message
            filters = _extract_filters(message)
            
            # Get recipe recommendations
            recipe_matches = recommendation_engine.recommend_by_query(
                request.user,
                message,
                limit=5,
                filters=filters
            )
            
            # Format prompt
            prompt = RECIPE_RECOMMENDATION_PROMPT.format(
                user_message=message,
                available_ingredients=ingredients_list,
                cuisine_preferences=filters.get('cuisine_type', 'Any'),
                dietary_restrictions=context.get('dietary_restrictions', 'None'),
                time_constraints=filters.get('max_time', 'No time limit'),
                recipe_matches=format_recipe_matches(recipe_matches)
            )
            
            # Generate response
            messages = [{"role": "user", "content": prompt}]
            response = llm_service.generate_response(
                messages,
                system_prompt=RECIPE_ASSISTANT_SYSTEM_PROMPT
            )
            
            # Extract recipe IDs for storage
            recommended_recipe_ids = [str(match['recipe'].id) for match in recipe_matches[:3]]
            
            # Store in chat history
            chat = ChatHistory.objects.create(
                user=request.user,
                message=message,
                response=response,
                context=context,
                recommended_recipes=recommended_recipe_ids
            )
            
            # Prepare response data
            response_data = {
                'response': response,
                'recommended_recipes': [
                    {
                        'recipe': RecipeSerializer(match['recipe'], context={'request': request}).data,
                        'match_percentage': match['match_percentage'],
                        'missing_ingredients': match['missing_ingredients']
                    }
                    for match in recipe_matches[:3]
                ],
                'chat_id': chat.id
            }
            
        else:
            # General cooking help
            messages = [
                {"role": "user", "content": f"Available ingredients: {ingredients_list}"},
                {"role": "user", "content": message}
            ]
            
            response = llm_service.generate_response(
                messages,
                system_prompt=RECIPE_ASSISTANT_SYSTEM_PROMPT
            )
            
            # Store in chat history
            chat = ChatHistory.objects.create(
                user=request.user,
                message=message,
                response=response,
                context=context
            )
            
            response_data = {
                'response': response,
                'chat_id': chat.id
            }
        
        return success_response(
            data=response_data,
            message='Response generated successfully'
        )
        
    except Exception as e:
        return error_response(
            message=f'Failed to generate response: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history(request):
    """Get user's chat history"""
    # Get recent chat history
    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))
    
    chats = ChatHistory.objects.filter(
        user=request.user
    ).order_by('-created_at')[offset:offset + limit]
    
    total_count = ChatHistory.objects.filter(user=request.user).count()
    
    serializer = ChatHistorySerializer(chats, many=True, context={'request': request})
    
    return success_response(
        data={
            'chats': serializer.data,
            'total_count': total_count,
            'has_more': (offset + limit) < total_count
        }
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_recipes(request):
    """Get recipe recommendations based on criteria"""
    serializer = RecipeRecommendationRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return error_response(
            message='Invalid request',
            errors=serializer.errors
        )
    
    try:
        recommendation_engine = RecommendationEngine()
        
        # Get recommendations
        if serializer.validated_data.get('query'):
            # Query-based recommendations
            filters = {
                k: v for k, v in serializer.validated_data.items()
                if k in ['cuisine_type', 'difficulty', 'max_time', 'taste_profile']
            }
            
            recommendations = recommendation_engine.recommend_by_query(
                request.user,
                serializer.validated_data['query'],
                limit=serializer.validated_data['limit'],
                filters=filters
            )
        else:
            # Ingredient-based recommendations
            recommendations = recommendation_engine.recommend_by_ingredients(
                request.user,
                min_match_percentage=serializer.validated_data['min_match_percentage'],
                limit=serializer.validated_data['limit']
            )
        
        # Format response
        formatted_recommendations = []
        for rec in recommendations:
            formatted_recommendations.append({
                'recipe': RecipeSerializer(rec['recipe'], context={'request': request}).data,
                'match_percentage': rec['match_percentage'],
                'available_ingredients': rec['available_ingredients'],
                'missing_ingredients': rec['missing_ingredients'],
                'similarity_score': rec.get('similarity_score', 0)
            })
        
        return success_response(
            data={
                'recommendations': formatted_recommendations,
                'count': len(formatted_recommendations)
            }
        )
        
    except Exception as e:
        return error_response(
            message=f'Failed to get recommendations: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_meal_plan(request):
    """Generate a meal plan for the user"""
    serializer = MealPlanRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return error_response(
            message='Invalid request',
            errors=serializer.errors
        )
    
    try:
        recommendation_engine = RecommendationEngine()
        
        # Generate meal plan
        meal_plan = recommendation_engine.generate_meal_plan(
            request.user,
            days=serializer.validated_data['days'],
            meals_per_day=serializer.validated_data['meals_per_day']
        )
        
        # Format response
        formatted_plan = {}
        shopping_list = {}
        
        for day, meals in meal_plan.items():
            formatted_plan[day] = []
            
            for meal in meals:
                formatted_meal = {
                    'meal_type': meal['meal_type'],
                    'recipe': RecipeSerializer(meal['recipe'], context={'request': request}).data,
                    'match_percentage': meal['match_percentage'],
                    'missing_ingredients': meal['missing_ingredients']
                }
                formatted_plan[day].append(formatted_meal)
                
                # Aggregate missing ingredients for shopping list
                for ingredient in meal['missing_ingredients']:
                    shopping_list[ingredient] = shopping_list.get(ingredient, 0) + 1
        
        return success_response(
            data={
                'meal_plan': formatted_plan,
                'shopping_list': [
                    {'ingredient': ing, 'needed_for_meals': count}
                    for ing, count in shopping_list.items()
                ],
                'days': serializer.validated_data['days'],
                'meals_per_day': serializer.validated_data['meals_per_day']
            }
        )
        
    except Exception as e:
        return error_response(
            message=f'Failed to generate meal plan: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Helper functions
def _analyze_intent(message: str) -> str:
    """Analyze user message intent"""
    message_lower = message.lower()
    
    # Recipe recommendation keywords
    recipe_keywords = [
        'recipe', 'cook', 'make', 'prepare', 'suggest', 'recommend',
        'what can i', 'dinner', 'lunch', 'breakfast', 'meal',
        'hungry', 'eat', 'food', 'dish', 'cuisine'
    ]
    
    if any(keyword in message_lower for keyword in recipe_keywords):
        return 'recipe_recommendation'
    
    return 'general_help'


def _extract_filters(message: str) -> dict:
    """Extract filters from message"""
    filters = {}
    message_lower = message.lower()
    
    # Cuisine types
    cuisines = ['italian', 'chinese', 'indian', 'mexican', 'thai', 
                'japanese', 'french', 'greek', 'american']
    for cuisine in cuisines:
        if cuisine in message_lower:
            filters['cuisine_type'] = cuisine.title()
            break
    
    # Difficulty
    if 'easy' in message_lower or 'simple' in message_lower:
        filters['difficulty'] = 'easy'
    elif 'hard' in message_lower or 'challenging' in message_lower:
        filters['difficulty'] = 'hard'
    
    # Time constraints
    import re
    time_match = re.search(r'(\d+)\s*(minute|min|hour|hr)', message_lower)
    if time_match:
        time_value = int(time_match.group(1))
        unit = time_match.group(2)
        if 'hour' in unit or 'hr' in unit:
            time_value *= 60
        filters['max_time'] = time_value
    
    # Taste profile
    tastes = ['sweet', 'savory', 'spicy', 'tangy', 'mild']
    for taste in tastes:
        if taste in message_lower:
            filters['taste_profile'] = taste
            break
    
    return filters
