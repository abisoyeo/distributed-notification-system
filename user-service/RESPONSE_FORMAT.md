# API Response Format Documentation

## Overview
All API endpoints use a standardized response format for consistency and predictability.

## Response Structure

```json
{
  "success": boolean,
  "data": any,
  "error": string | null,
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
```

## Usage Guide

### Import the Utility

```python
from users.utils import APIResponse
```

### Success Responses

#### 1. Simple Success (200 OK)
```python
return APIResponse.success(
    data={"user_id": "123", "email": "user@example.com"},
    message="User retrieved successfully"
)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "123",
    "email": "user@example.com"
  },
  "error": null,
  "message": "User retrieved successfully",
  "meta": {
    "total": 1,
    "limit": 20,
    "page": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

#### 2. Created Response (201 Created)
```python
return APIResponse.created(
    data={"user_id": user.id, "email": user.email},
    message="User created successfully"
)
```

#### 3. Updated Response (200 OK)
```python
return APIResponse.updated(
    data=serializer.data,
    message="User updated successfully"
)
```

#### 4. Deleted Response (204 No Content)
```python
return APIResponse.deleted(
    message="User deleted successfully"
)
```

### Error Responses

#### 1. Validation Error (400 Bad Request)
```python
if not serializer.is_valid():
    return APIResponse.validation_error(
        errors=serializer.errors,
        message="Validation failed"
    )
```

**Response:**
```json
{
  "success": false,
  "data": {
    "email": ["This field is required."],
    "password": ["This field must be at least 8 characters."]
  },
  "error": "email: This field is required.; password: This field must be at least 8 characters.",
  "message": "Validation failed",
  "meta": {
    "total": 0,
    "limit": 0,
    "page": 1,
    "total_pages": 0,
    "has_next": false,
    "has_previous": false
  }
}
```

#### 2. Not Found Error (404 Not Found)
```python
return APIResponse.not_found(
    message="User not found",
    error="The requested user does not exist"
)
```

#### 3. Unauthorized Error (401 Unauthorized)
```python
return APIResponse.unauthorized(
    message="Authentication required",
    error="You must be logged in to access this resource"
)
```

#### 4. Forbidden Error (403 Forbidden)
```python
return APIResponse.forbidden(
    message="Access denied",
    error="You do not have permission to perform this action"
)
```

#### 5. Custom Error
```python
return APIResponse.error(
    error="Database connection failed",
    message="Internal server error",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
)
```

### Paginated Responses

#### Method 1: Using paginated_response helper
```python
from users.utils import APIResponse

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        return APIResponse.paginated_response(
            queryset=queryset,
            serializer_class=self.get_serializer_class(),
            request=request,
            message="Users retrieved successfully"
        )
```

**Response (GET /api/users/?page=2&limit=10):**
```json
{
  "success": true,
  "data": [
    {"id": "uuid-1", "email": "user1@example.com", "name": "User 1"},
    {"id": "uuid-2", "email": "user2@example.com", "name": "User 2"}
  ],
  "error": null,
  "message": "Users retrieved successfully",
  "meta": {
    "total": 45,
    "limit": 10,
    "page": 2,
    "total_pages": 5,
    "has_next": true,
    "has_previous": true
  }
}
```

#### Method 2: Manual pagination control
```python
def list(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 20))
    
    # Manual pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_data = queryset[start:end]
    
    serializer = self.get_serializer(paginated_data, many=True)
    
    return APIResponse.success(
        data=serializer.data,
        message="Users retrieved successfully",
        total=queryset.count(),
        limit=limit,
        page=page
    )
```

## Complete View Examples

### Example 1: User Registration
```python
class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return APIResponse.validation_error(
                errors=serializer.errors,
                message="User registration failed"
            )
        
        self.perform_create(serializer)
        
        return APIResponse.created(
            data={
                'user_id': serializer.data['id'],
                'email': serializer.data['email'],
                'name': serializer.data['name']
            },
            message="User registered successfully"
        )
```

### Example 2: User Detail with Error Handling
```python
class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return APIResponse.success(
                data=serializer.data,
                message="User retrieved successfully"
            )
        except User.DoesNotExist:
            return APIResponse.not_found(
                message="User not found",
                error="The requested user does not exist"
            )
```

### Example 3: Update with Validation
```python
class PreferencesUpdateView(generics.UpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return APIResponse.validation_error(
                errors=serializer.errors,
                message="Failed to update preferences"
            )
        
        self.perform_update(serializer)
        
        return APIResponse.updated(
            data=serializer.data,
            message="Preferences updated successfully"
        )
```

### Example 4: Login with Custom Response
```python
class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return APIResponse.error(
                error=str(e),
                message="Login failed",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        return APIResponse.success(
            data=serializer.validated_data,
            message="Login successful"
        )
```

## API Method Reference

### Success Methods
- `APIResponse.success(data, message, status_code, total, limit, page, **kwargs)` - Generic success response
- `APIResponse.created(data, message, **kwargs)` - 201 Created
- `APIResponse.updated(data, message, **kwargs)` - 200 OK for updates
- `APIResponse.deleted(message, **kwargs)` - 204 No Content

### Error Methods
- `APIResponse.error(error, message, status_code, data, **kwargs)` - Generic error response
- `APIResponse.validation_error(errors, message, **kwargs)` - 400 Bad Request
- `APIResponse.not_found(message, error, **kwargs)` - 404 Not Found
- `APIResponse.unauthorized(message, error, **kwargs)` - 401 Unauthorized
- `APIResponse.forbidden(message, error, **kwargs)` - 403 Forbidden

### Pagination Method
- `APIResponse.paginated_response(queryset, serializer_class, request, message, **kwargs)` - Auto-paginated response

## Additional Meta Fields

You can add custom metadata to any response:

```python
return APIResponse.success(
    data=user_data,
    message="User retrieved successfully",
    timestamp=datetime.now().isoformat(),
    version="v1",
    request_id=request.headers.get('X-Request-ID')
)
```

**Response:**
```json
{
  "success": true,
  "data": {...},
  "error": null,
  "message": "User retrieved successfully",
  "meta": {
    "total": 1,
    "limit": 20,
    "page": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false,
    "timestamp": "2025-01-15T10:30:00",
    "version": "v1",
    "request_id": "abc-123"
  }
}
```

## Best Practices

1. **Always use APIResponse methods** instead of returning raw Response objects
2. **Provide meaningful messages** that describe what happened
3. **Use appropriate HTTP status codes** via the built-in methods
4. **Handle validation errors consistently** with `validation_error()`
5. **Include relevant data** in error responses when helpful for debugging
6. **Use pagination** for list endpoints to avoid large payloads
7. **Add custom meta fields** sparingly and document them
