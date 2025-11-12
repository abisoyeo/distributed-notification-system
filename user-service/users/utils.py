"""
Utility functions for API responses and common operations.
"""
from rest_framework.response import Response
from rest_framework import status
from typing import Any, Optional, Dict
from math import ceil


class APIResponse:
    """
    Standard API response formatter for consistent response structure.
    
    Response format:
    {
        "success": boolean,
        "data": any,
        "error": string or null,
        "message": string,
        "meta": {
            "total": number,
            "limit": number,
            "page": number,
            "total_pages": number,
            "has_next": boolean,
            "has_previous": boolean
        }
    }
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Request successful",
        status_code: int = status.HTTP_200_OK,
        total: Optional[int] = None,
        limit: int = 20,
        page: int = 1,
        **kwargs
    ) -> Response:
        """
        Create a successful API response.
        
        Args:
            data: The response data
            message: Success message
            status_code: HTTP status code
            total: Total number of items (for pagination)
            limit: Items per page
            page: Current page number
            **kwargs: Additional meta fields
            
        Returns:
            Response: DRF Response object with standardized format
        """
        # Calculate pagination meta
        if total is None:
            if isinstance(data, list):
                total = len(data)
            else:
                total = 1 if data else 0
        
        total_pages = ceil(total / limit) if limit > 0 else 1
        has_next = page < total_pages
        has_previous = page > 1
        
        response_data = {
            "success": True,
            "data": data,
            "error": None,
            "message": message,
            "meta": {
                "total": total,
                "limit": limit,
                "page": page,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous,
                **kwargs
            }
        }
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(
        error: str = "An error occurred",
        message: str = "Request failed",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        data: Any = None,
        **kwargs
    ) -> Response:
        """
        Create an error API response.
        
        Args:
            error: Error message or details
            message: General error message
            status_code: HTTP status code
            data: Optional error data
            **kwargs: Additional meta fields
            
        Returns:
            Response: DRF Response object with standardized error format
        """
        response_data = {
            "success": False,
            "data": data,
            "error": error,
            "message": message,
            "meta": {
                "total": 0,
                "limit": 0,
                "page": 1,
                "total_pages": 0,
                "has_next": False,
                "has_previous": False,
                **kwargs
            }
        }
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "Resource created successfully",
        **kwargs
    ) -> Response:
        """Create a 201 Created response."""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED,
            **kwargs
        )
    
    @staticmethod
    def updated(
        data: Any = None,
        message: str = "Resource updated successfully",
        **kwargs
    ) -> Response:
        """Create a 200 OK response for updates."""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_200_OK,
            **kwargs
        )
    
    @staticmethod
    def deleted(
        message: str = "Resource deleted successfully",
        **kwargs
    ) -> Response:
        """Create a 204 No Content response for deletions."""
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_204_NO_CONTENT,
            **kwargs
        )
    
    @staticmethod
    def not_found(
        message: str = "Resource not found",
        error: str = "The requested resource does not exist",
        **kwargs
    ) -> Response:
        """Create a 404 Not Found response."""
        return APIResponse.error(
            error=error,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            **kwargs
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Authentication required",
        error: str = "You must be authenticated to access this resource",
        **kwargs
    ) -> Response:
        """Create a 401 Unauthorized response."""
        return APIResponse.error(
            error=error,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            **kwargs
        )
    
    @staticmethod
    def forbidden(
        message: str = "Access forbidden",
        error: str = "You do not have permission to access this resource",
        **kwargs
    ) -> Response:
        """Create a 403 Forbidden response."""
        return APIResponse.error(
            error=error,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            **kwargs
        )
    
    @staticmethod
    def validation_error(
        errors: Dict[str, Any],
        message: str = "Validation failed",
        **kwargs
    ) -> Response:
        """
        Create a 400 Bad Request response for validation errors.
        
        Args:
            errors: Dictionary of field errors from serializer
            message: Error message
            **kwargs: Additional meta fields
        """
        # Format validation errors
        error_messages = []
        for field, error_list in errors.items():
            if isinstance(error_list, list):
                error_messages.append(f"{field}: {', '.join(str(e) for e in error_list)}")
            else:
                error_messages.append(f"{field}: {str(error_list)}")
        
        return APIResponse.error(
            error="; ".join(error_messages),
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            data=errors,
            **kwargs
        )
    
    @staticmethod
    def paginated_response(
        queryset,
        serializer_class,
        request,
        message: str = "Data retrieved successfully",
        **kwargs
    ) -> Response:
        """
        Create a paginated response from a queryset.
        
        Args:
            queryset: Django queryset
            serializer_class: Serializer class to use
            request: Request object for pagination params
            message: Success message
            **kwargs: Additional meta fields
        """
        # Get pagination params
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        
        # Calculate pagination
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        
        # Get paginated data
        paginated_queryset = queryset[start:end]
        serializer = serializer_class(paginated_queryset, many=True)
        
        return APIResponse.success(
            data=serializer.data,
            message=message,
            total=total,
            limit=limit,
            page=page,
            **kwargs
        )


def format_serializer_errors(serializer_errors: Dict[str, Any]) -> str:
    """
    Format DRF serializer errors into a readable string.
    
    Args:
        serializer_errors: Dictionary of errors from serializer.errors
        
    Returns:
        str: Formatted error message
    """
    error_messages = []
    for field, errors in serializer_errors.items():
        if isinstance(errors, list):
            for error in errors:
                if isinstance(error, dict):
                    error_messages.append(f"{field}: {error}")
                else:
                    error_messages.append(f"{field}: {error}")
        else:
            error_messages.append(f"{field}: {errors}")
    
    return "; ".join(error_messages)
