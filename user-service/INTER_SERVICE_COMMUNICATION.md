# User Service - Inter-Service Communication Guide

## 📞 Which Service Calls Which Endpoint?

### **Notification Service** 🔔

When sending notifications, the Notification Service needs to check user preferences and get contact information.

| Endpoint | Purpose | Example Use Case |
|----------|---------|------------------|
| `GET /api/v1/users/{user_id}/preferences` | Check if user wants email/push notifications | Before sending any notification, check preferences |
| `GET /api/v1/users/{user_id}/` | Get user's email address and push_token | Get contact info to actually send the notification |

**Example Flow:**
```
1. Notification Service receives: "Send notification to user 123"
2. Calls: GET /api/v1/users/123/preferences
   → Response: {"email": true, "push": false}
3. User wants email, so call: GET /api/v1/users/123/
   → Response: {email: "user@example.com", ...}
4. Send email to user@example.com
```

---

### **Analytics Service** 📊

When tracking user behavior and generating reports.

| Endpoint | Purpose | Example Use Case |
|----------|---------|------------------|
| `GET /api/v1/users/{user_id}/` | Get user profile data | Track user demographics, activity patterns |

**Example Flow:**
```
1. Analytics receives event: "User 123 clicked button"
2. Calls: GET /api/v1/users/123/
   → Response: {name: "John Doe", email: "john@example.com", created_at: "..."}
3. Store analytics with user context
```

---

### **Admin Dashboard** 👥

When admins need to view/manage user accounts.

| Endpoint | Purpose | Example Use Case |
|----------|---------|------------------|
| `POST /api/v1/users/login` | Admin authentication | Admin logs into dashboard |
| `GET /api/v1/users/{user_id}/` | View user profile | Admin views user account details |
| `GET /api/v1/users/{user_id}/preferences` | View notification settings | Admin checks user's preferences |
| `PATCH /api/v1/users/{user_id}/preferences` | Update settings for user | Admin adjusts preferences for support ticket |

**Example Flow:**
```
1. Admin logs in: POST /api/v1/users/login
   → Response: {access_token, refresh_token}
2. Admin searches for user and clicks profile
3. Dashboard calls: GET /api/v1/users/456/
   → Shows user info
4. Admin clicks "Notification Settings"
5. Dashboard calls: GET /api/v1/users/456/preferences
   → Shows current preferences
```

---

### **Mobile/Web App** 📱💻

Client applications for end users.

| Endpoint | Purpose | Example Use Case |
|----------|---------|------------------|
| `POST /api/v1/users/` | User registration | New user signs up |
| `POST /api/v1/users/login` | User login | User signs in to app |
| `POST /api/v1/users/refresh` | Refresh expired token | Access token expired, get new one |
| `GET /api/v1/users/{user_id}/` | Get own profile | User views their profile |
| `GET /api/v1/users/{user_id}/preferences` | View notification settings | User opens settings page |
| `PATCH /api/v1/users/{user_id}/preferences` | Update preferences | User toggles "Email notifications" |
| `PATCH /api/v1/users/{user_id}/push_token` | Register push token | App gets FCM token and registers it |

**Example Flow - User Updates Preferences:**
```
1. User opens app settings
2. App calls: GET /api/v1/users/123/preferences
   → Shows: Email ✓, Push ✓
3. User toggles Email OFF
4. App calls: PATCH /api/v1/users/123/preferences
   Body: {"email": false}
   → Updated preferences saved
5. Future notifications respect new preference
```

---

## 🔐 How Authentication Works

### **Step 1: Get Token (Login)**
```
Client → POST /api/v1/users/login
Body: {"email": "user@example.com", "password": "SecurePass123"}

Response: {
  "access": "eyJhbGc...",  ← Use for API requests (expires in 15 min)
  "refresh": "eyJhbGc...", ← Use to get new access token (expires in 1 day)
  "user": {...}
}
```

### **Step 2: Use Token in Requests**
```
Any Service → GET /api/v1/users/123/preferences
Headers: {
  "Authorization": "Bearer eyJhbGc...",  ← Add access token here
  "Content-Type": "application/json"
}
```

### **Step 3: Refresh When Expired**
```
If you get 401 Unauthorized (token expired):

Client → POST /api/v1/users/refresh
Body: {"refresh": "eyJhbGc..."}

Response: {
  "access": "NEW_TOKEN...",
  "refresh": "NEW_REFRESH_TOKEN..."
}
```

---

## 🌐 Service Communication Setup

### **Docker Compose Example**

When services run in Docker, they communicate using service names:

```yaml
# docker-compose.yml
services:
  user-service:
    ports:
      - "8000:8000"
    
  notification-service:
    environment:
      - USER_SERVICE_URL=http://user-service:8000  ← Use service name
    depends_on:
      - user-service
```

### **Environment Variables**

Each service needs to know where User Service is:

```bash
# Notification Service .env
USER_SERVICE_URL=http://user-service:8000

# Analytics Service .env  
USER_SERVICE_URL=http://user-service:8000

# Local development
USER_SERVICE_URL=http://localhost:8000
```

---

## 📋 Quick Reference: Service → Endpoint Mapping

### Before Sending Notification
```
Notification Service → GET /api/v1/users/{id}/preferences  (Check if user wants notifications)
Notification Service → GET /api/v1/users/{id}/            (Get email/push_token to send to)
```

### User Analytics
```
Analytics Service → GET /api/v1/users/{id}/  (Get user profile data)
```

### Admin Operations
```
Admin Dashboard → POST /api/v1/users/login              (Admin login)
Admin Dashboard → GET /api/v1/users/{id}/               (View user profile)
Admin Dashboard → PATCH /api/v1/users/{id}/preferences  (Update settings)
```

### User Actions
```
Mobile/Web App → POST /api/v1/users/                    (Register)
Mobile/Web App → POST /api/v1/users/login               (Login)
Mobile/Web App → PATCH /api/v1/users/{id}/preferences   (Update settings)
Mobile/Web App → PATCH /api/v1/users/{id}/push_token    (Register device)
```

---

## 🎯 Summary

**Your User Service provides:**
- ✅ User authentication (login, token refresh)
- ✅ User profiles (read user data)
- ✅ Notification preferences (read/update)
- ✅ Push token management (register devices)

**Other services simply:**
1. Set the User Service URL in their config
2. Make standard HTTP requests with authentication
3. Parse the standardized JSON responses

**That's it! No complex setup needed.** 🚀

Your User Service is a standard REST API that any service can consume using HTTP requests.
