"""
URL patterns for storage app
"""
from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    path('upload/recipe-image/', views.upload_recipe_image, name='upload-recipe-image'),
]
