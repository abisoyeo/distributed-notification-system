from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny
from .utils import APIResponse
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email as django_validate_email
import logging

logger = logging.getLogger(__name__)


class LoginSerializer(serializers.Serializer):
    """Serializer for login request validation"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate_email(self, value):
        """Validate email format"""
        if not value:
            raise serializers.ValidationError("Email is required")
        
        try:
            django_validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Enter a valid email address")
        
        return value.lower()
    
    def validate_password(self, value):
        """Validate password is not empty"""
        if not value:
            raise serializers.ValidationError("Password is required")
        return value


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer to add user data to token response"""
    
    def validate(self, attrs):
        # Call parent validation which checks credentials
        try:
            data = super().validate(attrs)
        except Exception as e:
            # Don't expose detailed error messages for security
            logger.warning(f"Failed login attempt for email: {attrs.get('email', 'unknown')}")
            raise serializers.ValidationError({
                'detail': 'Invalid email or password'
            })
        
        # Check if user account is active
        if not self.user.is_active:
            logger.warning(f"Inactive account login attempt: {self.user.email}")
            raise serializers.ValidationError({
                'detail': 'This account has been deactivated'
            })
        
        # Add custom user data to response (exclude sensitive fields)
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'name': self.user.name,
            'push_token': self.user.push_token,
            'preferences': self.user.preferences,
            'created_at': self.user.created_at.isoformat() if self.user.created_at else None,
        }
        
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    """POST /api/v1/auth/login - User authentication"""
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]  # Explicitly allow unauthenticated access
    
    def post(self, request, *args, **kwargs):
        # First validate the input format
        input_serializer = LoginSerializer(data=request.data)
        
        if not input_serializer.is_valid():
            return APIResponse.validation_error(
                errors=input_serializer.errors,
                message="Login failed - invalid input"
            )
        
        # Now proceed with JWT token generation
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            
            # Log successful login (don't log passwords!)
            logger.info(f"Successful login: {input_serializer.validated_data['email']}")
            
            # Return standardized response
            return APIResponse.success(
                data=serializer.validated_data,
                message="Login successful"
            )
        
        except serializers.ValidationError as e:
            # Handle validation errors (invalid credentials, inactive account, etc.)
            error_detail = e.detail
            
            if isinstance(error_detail, dict):
                error_message = error_detail.get('detail', 'Invalid credentials')
            elif isinstance(error_detail, list) and len(error_detail) > 0:
                error_message = str(error_detail[0])
            else:
                error_message = str(error_detail)
            
            return APIResponse.error(
                error=error_message,
                message="Login failed",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        except (InvalidToken, TokenError) as e:
            logger.error(f"Token error during login: {str(e)}")
            return APIResponse.error(
                error="Authentication token could not be generated",
                message="Login failed",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        except Exception as e:
            logger.error(f"Unexpected login error: {str(e)}")
            return APIResponse.error(
                error="An unexpected error occurred",
                message="Login failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
