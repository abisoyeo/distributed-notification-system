"""
Custom exception handler for standardizing DRF authentication errors
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from .utils import APIResponse
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that standardizes all DRF exceptions
    to use our APIResponse format.
    
    This ensures 401/403 errors from JWT authentication failures
    use the same format as our other API responses.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Get request info for logging
        request = context.get('request')
        view = context.get('view')
        
        view_name = view.__class__.__name__ if view else 'Unknown'
        method = request.method if request else 'Unknown'
        path = request.path if request else 'Unknown'
        
        # Handle authentication errors (401)
        if isinstance(exc, NotAuthenticated):
            logger.warning(
                f"Authentication required: {method} {path} - {view_name}"
            )
            return APIResponse.unauthorized(
                error="Authentication credentials were not provided",
                message="Authentication required"
            )
        
        # Handle invalid token errors (401)
        if isinstance(exc, AuthenticationFailed):
            logger.warning(
                f"Authentication failed: {method} {path} - {view_name} - {str(exc)}"
            )
            return APIResponse.unauthorized(
                error=str(exc) if str(exc) else "Invalid or expired token",
                message="Authentication failed"
            )
        
        # For other exceptions, you can add more custom handling here
        # For now, return the default DRF response for non-auth errors
    
    return response
