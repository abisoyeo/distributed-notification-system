# Testing API Responses

## Example API Responses with New Format

### 1. User Registration (POST /api/v1/users/)

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123",
    "name": "John Doe"
  }'
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "newuser@example.com",
    "name": "John Doe"
  },
  "error": null,
  "message": "User registered successfully",
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

**Validation Error Response (400 Bad Request):**
```json
{
  "success": false,
  "data": {
    "email": ["This field is required."],
    "password": ["This field must be at least 8 characters."]
  },
  "error": "email: This field is required.; password: This field must be at least 8 characters.",
  "message": "User registration failed",
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

---

### 2. User Login (POST /api/v1/users/login)

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "name": "John Doe"
    }
  },
  "error": null,
  "message": "Login successful",
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

**Error Response (401 Unauthorized):**
```json
{
  "success": false,
  "data": null,
  "error": "No active account found with the given credentials",
  "message": "Login failed",
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

---

### 3. Get User Details (GET /api/v1/users/{user_id}/)

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "push_token": "device-token-xyz",
    "preferences": {
      "email": true,
      "push": true
    },
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
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

**Not Found Response (404 Not Found):**
```json
{
  "success": false,
  "data": null,
  "error": "The requested user does not exist",
  "message": "User not found",
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

---

### 4. Get Notification Preferences (GET /api/v1/users/{user_id}/preferences)

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/preferences \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "email": true,
    "push": true
  },
  "error": null,
  "message": "Notification preferences retrieved successfully",
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

---

### 5. Update Notification Preferences (PUT/PATCH /api/v1/users/{user_id}/preferences)

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/preferences \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "push": false,
    "email": true
  }'
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "email": true,
    "push": false
  },
  "error": null,
  "message": "Notification preferences updated successfully",
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

**Validation Error Response (400 Bad Request):**
```json
{
  "success": false,
  "data": {
    "unknown_fields": "Unknown fields: email_notifications, push_notifications. Only 'email' and 'push' are allowed."
  },
  "error": "unknown_fields: Unknown fields: email_notifications, push_notifications. Only 'email' and 'push' are allowed.",
  "message": "Preferences update failed",
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

**Note:** The API accepts only `email` and `push` fields (short names), not `email_notifications` or `push_notifications`.

---

### 6. Update Push Token (PATCH /api/v1/users/{user_id}/push_token)

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/push_token \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "fcm_token": "firebase-device-token-xyz123",
    "platform": "android"
  }'
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "user": "550e8400-e29b-41d4-a716-446655440000",
    "fcm_token": "firebase-device-token-xyz123",
    "platform": "android",
    "is_active": true,
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  },
  "error": null,
  "message": "Push token updated successfully",
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

**Validation Error Response (400 Bad Request):**
```json
{
  "success": false,
  "data": {
    "fcm_token": ["This field is required."],
    "platform": ["This field is required."]
  },
  "error": "fcm_token: This field is required.; platform: This field is required.",
  "message": "Failed to register push token",
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

---

### 7. Token Refresh (POST /api/v1/users/refresh)

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/users/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "error": null,
  "message": "Request successful",
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

---

### 8. Common Authentication Errors

#### Invalid/Expired Token Error (401 Unauthorized)

When using an invalid, expired, or malformed access token:

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer invalid_or_expired_token"
```

**Error Response:**
```json
{
  "success": false,
  "data": null,
  "error": "{'detail': ErrorDetail(string='Given token not valid for any token type', code='token_not_valid'), 'code': ErrorDetail(string='token_not_valid', code='token_not_valid'), 'messages': [{'token_class': ErrorDetail(string='AccessToken', code='token_not_valid'), 'token_type': ErrorDetail(string='access', code='token_not_valid'), 'message': ErrorDetail(string='Token is invalid', code='token_not_valid')}]}",
  "message": "Authentication failed",
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

**How to Fix:**
1. **Get a new access token** by logging in again:
   ```bash
   curl -X POST http://localhost:8000/api/v1/users/login \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "SecurePass123"}'
   ```

2. **Use the refresh token** to get a new access token (if access token expired but refresh token still valid):
   ```bash
   curl -X POST http://localhost:8000/api/v1/users/refresh \
     -H "Content-Type: application/json" \
     -d '{"refresh": "your_refresh_token_here"}'
   ```

3. **Check token format**: Ensure you're using `Bearer <token>` format in the Authorization header

**Note:** Access tokens expire after 15 minutes. Refresh tokens expire after 1 day.

---

## Postman Collection

Import this JSON into Postman for quick testing:

```json
{
  "info": {
    "name": "User Service API",
    "description": "Standardized response format",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Register User",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"SecurePass123\",\n  \"name\": \"Test User\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/api/v1/users/",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "users", ""]
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"SecurePass123\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/api/v1/users/login",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "users", "login"]
        }
      }
    },
    {
      "name": "Get User",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ],
        "url": {
          "raw": "http://localhost:8000/api/v1/users/{{user_id}}/",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "users", "{{user_id}}", ""]
        }
      }
    }
  ]
}
```

---

## Testing Checklist

- [ ] Test successful registration with all required fields
- [ ] Test registration with missing/invalid fields (validation errors)
- [ ] Test successful login with valid credentials
- [ ] Test login with invalid credentials (401 error)
- [ ] Test getting user details with valid token
- [ ] Test getting user details without token (401 error)
- [ ] Test getting user details with expired token (401 error)
- [ ] Test getting non-existent user (404 error)
- [ ] Test updating preferences with valid data
- [ ] Test updating preferences with invalid data
- [ ] Test updating push token with valid data
- [ ] Test token refresh with valid refresh token
- [ ] Test token refresh with expired/invalid token
- [ ] Test authentication with malformed Bearer token

## Important Notes

### Token Lifecycle
- **Access Token**: Expires after **15 minutes** - use for API requests
- **Refresh Token**: Expires after **1 day** - use to get new access tokens
- **Token Rotation**: Enabled - each refresh generates a new refresh token

### Common Issues
1. **"Token is invalid" error**: Your access token has expired. Use the refresh endpoint.
2. **404 on endpoints with trailing slash**: Remove the trailing slash (e.g., use `/preferences` not `/preferences/`)
3. **Method Not Allowed**: Check you're using the correct HTTP method (POST, GET, PATCH)
4. **Bad Request on registration**: Ensure you're sending to `/api/v1/users/` not `/api/v1/users/register/`
5. **Unknown fields error on preferences**: Use `email` and `push` field names, not `email_notifications` or `push_notifications`

### Database Connection Issues

**Error:** `remaining connection slots are reserved for roles with the SUPERUSER attribute`

**Cause:** PostgreSQL database has reached its maximum connection limit.

**Solutions:**
1. **Restart Django server** to release connections
2. **Check CONN_MAX_AGE setting** - Set to `0` in development mode to close connections after each request
3. **Check for connection leaks** - Ensure you're not opening connections without closing them
4. **Upgrade database plan** on Aiven if you need more concurrent connections

**Prevention:**
- Use `CONN_MAX_AGE = 0` during development (automatically configured in settings)
- Use connection pooling (like pgBouncer) in production
- Monitor active connections in Aiven dashboard

All responses should follow the standardized format with `success`, `data`, `error`, `message`, and `meta` fields.
