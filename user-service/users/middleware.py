import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """Log all requests with timing"""
    
    def process_request(self, request):
        request.start_time = time.time()
        
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"{request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.2f}s"
            )
        return response

class CacheMiddleware(MiddlewareMixin):
    """Add cache headers for GET requests"""
    
    def process_response(self, request, response):
        if request.method == 'GET' and response.status_code == 200:
            response['Cache-Control'] = 'max-age=300'  # 5 minutes
        return response