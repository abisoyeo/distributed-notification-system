from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import User, PushToken, NotificationPreferences
from .serializers import UserSerializer, PushTokenSerializer, NotificationPreferenceSerializer
from .services import UserService, PushTokenService
from .utils import APIResponse
from .cache import UserCache, CacheKeys
from .validators import Validators, ValidationError as CustomValidationError
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ValidationError as DjangoValidationError
import logging

logger = logging.getLogger(__name__)


class UserCreateView(generics.CreateAPIView):
    """POST /api/v1/users/ - Create user"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            # Extract and validate fields BEFORE serializer
            email = request.data.get('email')
            password = request.data.get('password')
            name = request.data.get('name')
            push_token = request.data.get('push_token')
            
            # Validate email
            try:
                email = Validators.validate_email(email)
            except CustomValidationError as e:
                return APIResponse.validation_error(
                    errors=e.errors,
                    message=e.message
                )
            
            # Validate password
            try:
                Validators.validate_password(password)
            except CustomValidationError as e:
                return APIResponse.validation_error(
                    errors=e.errors,
                    message=e.message
                )
            
            # Validate name
            try:
                name = Validators.validate_name(name, required=True)
            except CustomValidationError as e:
                return APIResponse.validation_error(
                    errors=e.errors,
                    message=e.message
                )
            
            # Validate push_token (optional)
            if push_token:
                try:
                    push_token = Validators.validate_push_token(push_token, required=False)
                except CustomValidationError as e:
                    return APIResponse.validation_error(
                        errors=e.errors,
                        message=e.message
                    )
            
            # Prepare validated data
            validated_data = {
                'email': email,
                'password': password,
                'name': name,
                'push_token': push_token
            }
            
            # Use serializer for additional validation
            serializer = self.get_serializer(data=validated_data)
            
            if not serializer.is_valid():
                return APIResponse.validation_error(
                    errors=serializer.errors,
                    message="User registration failed"
                )
            
            # Create user
            user = serializer.save()
            
            # Prepare response data (exclude sensitive fields)
            response_data = {
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'push_token': user.push_token,
                'preferences': user.preferences,
                'created_at': user.created_at.isoformat() if user.created_at else None,
            }
            
            # Cache the new user data
            UserCache.set_user_data(str(user.id), response_data)
            UserCache.set_user_preferences(str(user.id), user.preferences)
            if user.push_token:
                UserCache.set_push_token(str(user.id), user.push_token)
            
            logger.info(f"User created successfully: {user.email}")
            return APIResponse.created(
                data=response_data,
                message="User registered successfully"
            )
        
        except IntegrityError as e:
            # Handle duplicate email error
            logger.warning(f"Duplicate email registration attempt: {request.data.get('email')}")
            return APIResponse.error(
                error="A user with this email already exists",
                message="User registration failed",
                status_code=status.HTTP_409_CONFLICT
            )
        
        except DatabaseError as e:
            logger.error(f"Database error during user creation: {str(e)}")
            return APIResponse.error(
                error="Database error occurred",
                message="User registration failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except Exception as e:
            logger.error(f"Unexpected error during user creation: {str(e)}", exc_info=True)
            return APIResponse.error(
                error="An unexpected error occurred",
                message="User registration failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserRetrieveView(generics.RetrieveAPIView):
    """GET /api/v1/users/:user_id/ - Get user by ID with caching"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        try:
            user_id_raw = self.kwargs.get('pk')
            
            # Validate UUID format
            try:
                Validators.validate_uuid(user_id_raw, field_name="user_id")
                user_id = str(user_id_raw)
            except CustomValidationError as e:
                logger.warning(f"Invalid UUID format: {user_id_raw}")
                return APIResponse.validation_error(
                    errors=e.errors,
                    message=e.message
                )
            
            # Try to get from cache first
            cached_data = UserCache.get_user_data(user_id)
            if cached_data:
                # Permission check
                if str(request.user.id) != user_id:
                    logger.warning(f"Unauthorized access attempt by {request.user.email} to view user {user_id}")
                    return APIResponse.error(
                        error="You can only view your own profile",
                        message="User retrieval failed",
                        status_code=status.HTTP_403_FORBIDDEN
                    )
                
                logger.info(f"User retrieved from cache: {user_id}")
                return APIResponse.success(
                    data=cached_data,
                    message="User retrieved successfully"
                )
            
            # Cache miss - fetch from database
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.warning(f"User not found: {user_id}")
                return APIResponse.not_found(
                    error=f"User with id {user_id} not found",
                    message="User retrieval failed"
                )
            except DatabaseError as e:
                logger.error(f"Database error retrieving user {user_id}: {str(e)}")
                return APIResponse.error(
                    error="Database error occurred",
                    message="User retrieval failed",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Permission check
            if request.user.id != user.id:
                logger.warning(f"Unauthorized access attempt by {request.user.email} to view user {user_id}")
                return APIResponse.error(
                    error="You can only view your own profile",
                    message="User retrieval failed",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Build response with explicit snake_case
            response_data = {
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'push_token': user.push_token,
                'preferences': {
                    'email': user.preferences.get('email', True),
                    'push': user.preferences.get('push', True)
                },
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            }
            
            # Cache the user data (10 minutes TTL)
            UserCache.set_user_data(user_id, response_data)
            
            logger.info(f"User retrieved from database and cached: {user.email}")
            return APIResponse.success(
                data=response_data,
                message="User retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during user retrieval: {str(e)}", exc_info=True)
            return APIResponse.error(
                error="An unexpected error occurred",
                message="User retrieval failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PreferencesRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """GET & PATCH /api/v1/users/:user_id/preferences - Get/Update preferences with caching"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user_id_raw = self.kwargs.get('user_id')
        
        # Validate UUID format
        try:
            Validators.validate_uuid(user_id_raw, field_name="user_id")
            user_id = str(user_id_raw)
        except CustomValidationError as e:
            raise NotFound(f"Invalid user_id format: {user_id_raw}")
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound(f"User with id {user_id} not found")
        except DatabaseError as e:
            logger.error(f"Database error retrieving user {user_id}: {str(e)}")
            raise Exception("Database error occurred")
        
        # Ensure user can only access their own preferences
        if self.request.user.id != user.id:
            raise PermissionDenied("You can only access your own preferences")
        
        return user
    
    def retrieve(self, request, *args, **kwargs):
        """GET - Return only preferences with email and push booleans"""
        user_id_raw = self.kwargs.get('user_id')
        
        try:
            # Validate UUID format
            try:
                Validators.validate_uuid(user_id_raw, field_name="user_id")
                user_id = str(user_id_raw)
            except CustomValidationError as e:
                logger.warning(f"Invalid UUID format: {user_id_raw}")
                return APIResponse.validation_error(
                    errors=e.errors,
                    message=e.message
                )
            
            # Try to get from cache first
            cached_preferences = UserCache.get_user_preferences(user_id)
            if cached_preferences:
                logger.info(f"Preferences retrieved from cache for user: {user_id}")
                return APIResponse.success(
                    data=cached_preferences,
                    message="Preferences retrieved successfully"
                )
            
            # Cache miss - fetch from database
            user = self.get_object()
            
            # Extract ONLY email and push preferences
            preferences = user.preferences or {}
            response_data = {
                'email': preferences.get('email', True),
                'push': preferences.get('push', True)
            }
            
            # Cache the preferences (10 minutes TTL)
            UserCache.set_user_preferences(user_id, response_data)
            
            logger.info(f"Preferences retrieved from database and cached: {user.email}")
            return APIResponse.success(
                data=response_data,
                message="Preferences retrieved successfully"
            )
            
        except NotFound as e:
            logger.warning(f"User not found: {user_id_raw}")
            return APIResponse.not_found(
                error=str(e),
                message="Preferences retrieval failed"
            )
        
        except PermissionDenied as e:
            logger.warning(f"Unauthorized preferences access by {request.user.email}")
            return APIResponse.error(
                error=str(e),
                message="Preferences retrieval failed",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        except DatabaseError as e:
            logger.error(f"Database error retrieving preferences: {str(e)}")
            return APIResponse.error(
                error="Database error occurred",
                message="Preferences retrieval failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except Exception as e:
            logger.error(f"Unexpected error during preferences retrieval: {str(e)}", exc_info=True)
            return APIResponse.error(
                error="An unexpected error occurred",
                message="Preferences retrieval failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def partial_update(self, request, *args, **kwargs):
        """PATCH - Update preferences and invalidate cache"""
        user_id_raw = self.kwargs.get('user_id')
        
        try:
            # Validate UUID format
            try:
                Validators.validate_uuid(user_id_raw, field_name="user_id")
            except CustomValidationError as e:
                logger.warning(f"Invalid UUID format: {user_id_raw}")
                return APIResponse.validation_error(
                    errors=e.errors,
                    message=e.message
                )
            
            user = self.get_object()
            user_id = str(user.id)
            
            # Get preferences from request body (direct, not nested)
            email_pref = request.data.get('email')
            push_pref = request.data.get('push')
            
            # Check for unknown fields
            allowed_fields = {'email', 'push'}
            provided_fields = set(request.data.keys())
            unknown_fields = provided_fields - allowed_fields
            
            if unknown_fields:
                return APIResponse.validation_error(
                    errors={'unknown_fields': f"Unknown fields: {', '.join(unknown_fields)}. Only 'email' and 'push' are allowed."},
                    message="Preferences update failed"
                )
            
            # Validate preferences
            try:
                Validators.validate_preferences(email_pref, push_pref)
            except CustomValidationError as e:
                return APIResponse.validation_error(
                    errors=e.errors,
                    message=e.message
                )
            
            # Update preferences
            updated_user = UserService.update_preferences(
                user=user,
                email_pref=email_pref,
                push_pref=push_pref
            )
            
            # Return updated preferences
            response_data = {
                'email': updated_user.preferences.get('email', True),
                'push': updated_user.preferences.get('push', True)
            }
            
            # Invalidate all user cache (preferences, user data)
            UserCache.delete_user_preferences(user_id)
            UserCache.delete_user_data(user_id)
            
            # Cache the new preferences
            UserCache.set_user_preferences(user_id, response_data)
            
            logger.info(f"Preferences updated and cache invalidated for user: {user.email}")
            return APIResponse.success(
                data=response_data,
                message="Preferences updated successfully"
            )
            
        except NotFound as e:
            logger.warning(f"User not found: {user_id_raw}")
            return APIResponse.not_found(
                error=str(e),
                message="Preferences update failed"
            )
        
        except PermissionDenied as e:
            logger.warning(f"Unauthorized preferences update by {request.user.email}")
            return APIResponse.error(
                error=str(e),
                message="Preferences update failed",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        except DatabaseError as e:
            logger.error(f"Database error updating preferences: {str(e)}")
            return APIResponse.error(
                error="Database error occurred",
                message="Preferences update failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except Exception as e:
            logger.error(f"Unexpected error during preferences update: {str(e)}", exc_info=True)
            return APIResponse.error(
                error="An unexpected error occurred",
                message="Preferences update failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PushTokenUpdateView(generics.UpdateAPIView):
    """PATCH /api/v1/users/:user_id/push_token - Update push token and invalidate cache"""
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user_id_raw = self.kwargs.get('user_id')
        
        # Validate UUID format
        try:
            Validators.validate_uuid(user_id_raw, field_name="user_id")
            user_id = str(user_id_raw)
        except CustomValidationError as e:
            raise NotFound(f"Invalid user_id format: {user_id_raw}")
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound(f"User with id {user_id} not found")
        except DatabaseError as e:
            logger.error(f"Database error retrieving user {user_id}: {str(e)}")
            raise Exception("Database error occurred")
        
        # Ensure user can only update their own push token
        if self.request.user.id != user.id:
            raise PermissionDenied("You can only update your own push token")
        
        return user
    
    def partial_update(self, request, *args, **kwargs):
        """PATCH - Update push token only and invalidate cache"""
        user_id_raw = self.kwargs.get('user_id')
        
        try:
            # Validate UUID format
            try:
                Validators.validate_uuid(user_id_raw, field_name="user_id")
            except CustomValidationError as e:
                logger.warning(f"Invalid UUID format: {user_id_raw}")
                return APIResponse.validation_error(
                    errors=e.errors,
                    message=e.message
                )
            
            user = self.get_object()
            user_id = str(user.id)
            push_token = request.data.get('push_token')
            
            # Validate push token
            try:
                push_token = Validators.validate_push_token(push_token, required=True)
            except CustomValidationError as e:
                return APIResponse.validation_error(
                    errors=e.errors,
                    message=e.message
                )
            
            # Update user's push_token field
            user.push_token = push_token
            user.save()
            
            # Optionally register as PushToken object if device_id provided
            device_id = request.data.get('device_id')
            device_type = request.data.get('device_type', 'other')
            
            if device_id:
                PushTokenService.register_token(
                    user=user,
                    device_id=device_id,
                    token=push_token,
                    device_type=device_type
                )
            
            response_data = {
                'id': str(user.id),
                'push_token': user.push_token
            }
            
            # Invalidate user cache and update push token cache
            UserCache.delete_user_data(user_id)
            UserCache.set_push_token(user_id, push_token)
            
            logger.info(f"Push token updated and cache invalidated for user: {user.email}")
            return APIResponse.success(
                data=response_data,
                message="Push token updated successfully"
            )
            
        except NotFound as e:
            logger.warning(f"User not found: {user_id_raw}")
            return APIResponse.not_found(
                error=str(e),
                message="Push token update failed"
            )
        
        except PermissionDenied as e:
            logger.warning(f"Unauthorized push token update by {request.user.email}")
            return APIResponse.error(
                error=str(e),
                message="Push token update failed",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        except DatabaseError as e:
            logger.error(f"Database error updating push token: {str(e)}")
            return APIResponse.error(
                error="Database error occurred",
                message="Push token update failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except Exception as e:
            logger.error(f"Unexpected error during push token update: {str(e)}", exc_info=True)
            return APIResponse.error(
                error="An unexpected error occurred",
                message="Push token update failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Keep this for backwards compatibility if needed
class PushTokenCreateView(generics.CreateAPIView):
    """Legacy: POST push tokens (use PushTokenUpdateView instead)"""
    queryset = PushToken.objects.all()
    serializer_class = PushTokenSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        if self.request.user.id != user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only create push tokens for yourself")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        push_token, created = PushTokenService.register_token(
            user=user,
            device_id=serializer.validated_data.get('device_id', ''),
            token=serializer.validated_data['token'],
            device_type=serializer.validated_data['device_type']
        )
        
        output_serializer = PushTokenSerializer(push_token)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(output_serializer.data, status=status_code)
