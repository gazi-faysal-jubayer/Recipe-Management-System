"""
URL patterns for shopping list functionality
"""
from django.urls import path
from . import shopping_views

app_name = 'shopping'

urlpatterns = [
    path('', shopping_views.shopping_list, name='list'),
    path('add/', shopping_views.add_item, name='add'),
    path('<uuid:item_id>/toggle/', shopping_views.toggle_purchased, name='toggle'),
    path('<uuid:item_id>/delete/', shopping_views.delete_item, name='delete'),
    path('from-recipe/<uuid:recipe_id>/', shopping_views.add_from_recipe, name='add-from-recipe'),
    path('clear-purchased/', shopping_views.clear_purchased, name='clear-purchased'),
    path('add-to-ingredients/', shopping_views.add_purchased_to_ingredients, name='add-to-ingredients'),
]
