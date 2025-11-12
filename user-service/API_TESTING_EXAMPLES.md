# Testing API Responses

## Example API Responses with New Format

### 1. User Registration (POST /api/users/register/)

**Request:**
```bash
curl -X POST http://localhost:8000/api/users/register/ \
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

### 2. User Login (POST /api/users/login/)

**Request:**
```bash
curl -X POST http://localhost:8000/api/users/login/ \
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

### 3. Get User Details (GET /api/users/{user_id}/)

**Request:**
```bash
curl -X GET http://localhost:8000/api/users/550e8400-e29b-41d4-a716-446655440000/ \
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
      "email_notifications": true,
      "push_notifications": true,
      "sms_notifications": false
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

### 4. Get Notification Preferences (GET /api/users/{user_id}/preferences/)

**Request:**
```bash
curl -X GET http://localhost:8000/api/users/550e8400-e29b-41d4-a716-446655440000/preferences/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user": "550e8400-e29b-41d4-a716-446655440000",
    "email_notifications": true,
    "push_notifications": true,
    "sms_notifications": false,
    "notification_frequency": "immediate",
    "quiet_hours_start": "22:00:00",
    "quiet_hours_end": "08:00:00"
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

### 5. Update Notification Preferences (PUT/PATCH /api/users/{user_id}/preferences/)

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/users/550e8400-e29b-41d4-a716-446655440000/preferences/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "push_notifications": false,
    "email_notifications": true
  }'
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user": "550e8400-e29b-41d4-a716-446655440000",
    "email_notifications": true,
    "push_notifications": false,
    "sms_notifications": false,
    "notification_frequency": "immediate",
    "quiet_hours_start": "22:00:00",
    "quiet_hours_end": "08:00:00"
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

---

### 6. Register Push Token (POST /api/users/{user_id}/push-tokens/)

**Request:**
```bash
curl -X POST http://localhost:8000/api/users/550e8400-e29b-41d4-a716-446655440000/push-tokens/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "fcm_token": "firebase-device-token-xyz123",
    "platform": "android"
  }'
```

**Success Response (201 Created):**
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
  "message": "Push token registered successfully",
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

### 7. Token Refresh (POST /api/users/token/refresh/)

**Request:**
```bash
curl -X POST http://localhost:8000/api/users/token/refresh/ \
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
          "raw": "http://localhost:8000/api/users/register/",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "users", "register", ""]
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
          "raw": "http://localhost:8000/api/users/login/",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "users", "login", ""]
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
          "raw": "http://localhost:8000/api/users/{{user_id}}/",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "users", "{{user_id}}", ""]
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
- [ ] Test getting non-existent user (404 error)
- [ ] Test updating preferences with valid data
- [ ] Test updating preferences with invalid data
- [ ] Test registering push token with valid data
- [ ] Test token refresh with valid refresh token
- [ ] Test token refresh with expired/invalid token

All responses should follow the standardized format with `success`, `data`, `error`, `message`, and `meta` fields.
