"""
Health check views for monitoring service status
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    GET /health - Health check endpoint
    
    Returns service health status including:
    - PostgreSQL/Database connection status
    - Redis connection status (if enabled)
    - Service timestamp
    
    Response format:
    {
        "success": true,
        "message": "User Service is healthy",
        "data": {
            "database": "connected",
            "redis": "connected",
            "timestamp": "2025-11-12T10:30:00.000Z"
        }
    }
    """
    health_data = {
        "database": "disconnected",
        "redis": "not_configured",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    is_healthy = True
    status_code = 200
    
    # Check PostgreSQL/Database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_data["database"] = "connected"
        logger.debug("Database health check: connected")
    except Exception as e:
        health_data["database"] = "disconnected"
        is_healthy = False
        status_code = 503  # Service Unavailable
        logger.error(f"Database health check failed: {str(e)}")
    
    # Check Redis connection (if configured)
    use_redis = getattr(settings, 'USE_REDIS', False)
    
    if use_redis:
        try:
            # Try to set and get a test value
            cache.set('health_check', 'ok', 10)
            test_value = cache.get('health_check')
            
            if test_value == 'ok':
                health_data["redis"] = "connected"
                logger.debug("Redis health check: connected")
            else:
                health_data["redis"] = "disconnected"
                is_healthy = False
                status_code = 503
                logger.warning("Redis health check failed: test value mismatch")
        except Exception as e:
            health_data["redis"] = "disconnected"
            is_healthy = False
            status_code = 503
            logger.error(f"Redis health check failed: {str(e)}")
    else:
        health_data["redis"] = "not_configured"
    
    # Prepare response
    response_data = {
        "success": is_healthy,
        "message": "User Service is healthy" if is_healthy else "User Service is unhealthy",
        "data": health_data
    }
    
    return JsonResponse(response_data, status=status_code)


def liveness_check(request):
    """
    GET /health/liveness - Kubernetes liveness probe
    
    Simple endpoint that returns 200 if the service is running.
    Does not check dependencies.
    """
    return JsonResponse({
        "success": True,
        "message": "Service is alive",
        "data": {
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }, status=200)


def readiness_check(request):
    """
    GET /health/readiness - Kubernetes readiness probe
    
    Checks if service is ready to accept traffic.
    Verifies database connection is available.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return JsonResponse({
            "success": True,
            "message": "Service is ready",
            "data": {
                "database": "connected",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }, status=200)
    
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JsonResponse({
            "success": False,
            "message": "Service is not ready",
            "data": {
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }, status=503)
