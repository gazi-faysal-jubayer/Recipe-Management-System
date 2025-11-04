"""
URL patterns for ingredients app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'ingredients'

router = DefaultRouter()
router.register('', views.IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
]
