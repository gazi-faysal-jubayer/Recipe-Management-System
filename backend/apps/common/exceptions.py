"""
Custom exceptions for the Recipe Management System
"""

class RecipeManagementException(Exception):
    """Base exception for all custom exceptions"""
    pass


class ValidationError(RecipeManagementException):
    """Raised when validation fails"""
    pass


class NotFoundError(RecipeManagementException):
    """Raised when a resource is not found"""
    pass


class PermissionDeniedError(RecipeManagementException):
    """Raised when user lacks permission"""
    pass


class ExternalServiceError(RecipeManagementException):
    """Raised when external service fails"""
    pass


class RateLimitError(RecipeManagementException):
    """Raised when rate limit is exceeded"""
    pass
