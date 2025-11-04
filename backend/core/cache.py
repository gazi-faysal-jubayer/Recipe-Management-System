"""
Caching utilities for Recipe Management System
"""
from django.core.cache import cache
from functools import wraps
import hashlib
import json


def cache_key(*args, **kwargs):
    """Generate cache key from arguments"""
    key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(timeout=3600, key_prefix=''):
    """
    Decorator to cache function results
    
    Args:
        timeout: Cache timeout in seconds (default: 1 hour)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = cache.get(key)
            
            if result is None:
                # Cache miss - call function
                result = func(*args, **kwargs)
                # Store in cache
                cache.set(key, result, timeout)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_pattern):
    """
    Invalidate cache keys matching pattern
    
    Args:
        key_pattern: Pattern to match cache keys
    """
    try:
        cache.delete_pattern(f"*{key_pattern}*")
    except AttributeError:
        # If delete_pattern not available, clear all
        cache.clear()


class CacheManager:
    """Manager for specific cache operations"""
    
    @staticmethod
    def cache_recipe_embedding(recipe_id, embedding, timeout=7200):
        """Cache recipe embedding"""
        key = f"recipe_embedding:{recipe_id}"
        cache.set(key, embedding, timeout)
    
    @staticmethod
    def get_recipe_embedding(recipe_id):
        """Get cached recipe embedding"""
        key = f"recipe_embedding:{recipe_id}"
        return cache.get(key)
    
    @staticmethod
    def cache_user_ingredients(user_id, ingredients, timeout=900):
        """Cache user's ingredient list"""
        key = f"user_ingredients:{user_id}"
        cache.set(key, ingredients, timeout)
    
    @staticmethod
    def get_user_ingredients(user_id):
        """Get cached user ingredients"""
        key = f"user_ingredients:{user_id}"
        return cache.get(key)
    
    @staticmethod
    def invalidate_user_ingredients(user_id):
        """Invalidate user's ingredient cache"""
        key = f"user_ingredients:{user_id}"
        cache.delete(key)
