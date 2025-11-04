"""
Common middleware for the Recipe Management System
"""
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log information about each request"""
    
    def process_request(self, request):
        request.start_time = time.time()
        logger.info(f"Request started: {request.method} {request.path}")
        
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"Request completed: {request.method} {request.path} "
                f"Status: {response.status_code} Duration: {duration:.2f}s"
            )
        return response


class ErrorHandlingMiddleware(MiddlewareMixin):
    """Global error handling middleware"""
    
    def process_exception(self, request, exception):
        logger.error(f"Unhandled exception: {str(exception)}", exc_info=True)
        
        return JsonResponse({
            'error': 'An unexpected error occurred',
            'message': str(exception) if settings.DEBUG else 'Internal server error'
        }, status=500)
