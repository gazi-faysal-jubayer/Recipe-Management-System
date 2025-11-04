"""
URL patterns for chatbot app
"""
from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('chat/', views.chat_message, name='chat'),
    path('history/', views.chat_history, name='history'),
    path('recommend/', views.recommend_recipes, name='recommend'),
    path('meal-plan/', views.generate_meal_plan, name='meal-plan'),
]
