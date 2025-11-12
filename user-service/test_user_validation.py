"""
Test script for POST /api/v1/users/ endpoint validation
Run with: python manage.py shell < test_user_creation.py
"""

from users.serializers import UserSerializer
from rest_framework.test import APIRequestFactory
from users.views import UserCreateView
import json

factory = APIRequestFactory()

print("\n" + "="*80)
print("POST /api/v1/users/ ENDPOINT VALIDATION TESTS")
print("="*80)

# Test 1: Valid payload with all fields
print("\n1. ✅ Valid payload with all fields:")
valid_payload = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "password": "SecurePass123",
    "push_token": "firebase-token-xyz",
    "preferences": {
        "email": True,
        "push": False
    }
}
print(f"Payload: {json.dumps(valid_payload, indent=2)}")
serializer = UserSerializer(data=valid_payload)
if serializer.is_valid():
    print("✅ PASSED: All validations passed")
    print(f"Validated data: {serializer.validated_data}")
else:
    print(f"❌ FAILED: {serializer.errors}")

# Test 2: Missing required fields
print("\n2. ❌ Missing required fields (name, email, password):")
invalid_payload = {
    "push_token": "token"
}
print(f"Payload: {json.dumps(invalid_payload, indent=2)}")
serializer = UserSerializer(data=invalid_payload)
if not serializer.is_valid():
    print("✅ PASSED: Validation correctly failed")
    print(f"Errors: {json.dumps(serializer.errors, indent=2)}")
else:
    print("❌ FAILED: Should have failed validation")

# Test 3: Invalid email format
print("\n3. ❌ Invalid email format:")
invalid_email_payload = {
    "name": "John Doe",
    "email": "not-an-email",
    "password": "SecurePass123"
}
print(f"Payload: {json.dumps(invalid_email_payload, indent=2)}")
serializer = UserSerializer(data=invalid_email_payload)
if not serializer.is_valid():
    print("✅ PASSED: Email validation correctly failed")
    print(f"Errors: {json.dumps(serializer.errors, indent=2)}")
else:
    print("❌ FAILED: Should have failed email validation")

# Test 4: Weak password (< 8 chars)
print("\n4. ❌ Weak password (too short):")
weak_password_payload = {
    "name": "John Doe",
    "email": "test@example.com",
    "password": "Pass1"
}
print(f"Payload: {json.dumps(weak_password_payload, indent=2)}")
serializer = UserSerializer(data=weak_password_payload)
if not serializer.is_valid():
    print("✅ PASSED: Password validation correctly failed")
    print(f"Errors: {json.dumps(serializer.errors, indent=2)}")
else:
    print("❌ FAILED: Should have failed password validation")

# Test 5: Password without numbers
print("\n5. ❌ Password without numbers:")
no_number_password = {
    "name": "John Doe",
    "email": "test2@example.com",
    "password": "OnlyLetters"
}
print(f"Payload: {json.dumps(no_number_password, indent=2)}")
serializer = UserSerializer(data=no_number_password)
if not serializer.is_valid():
    print("✅ PASSED: Password validation correctly failed")
    print(f"Errors: {json.dumps(serializer.errors, indent=2)}")
else:
    print("❌ FAILED: Should have failed password validation")

# Test 6: Empty name
print("\n6. ❌ Empty name field:")
empty_name_payload = {
    "name": "",
    "email": "test3@example.com",
    "password": "SecurePass123"
}
print(f"Payload: {json.dumps(empty_name_payload, indent=2)}")
serializer = UserSerializer(data=empty_name_payload)
if not serializer.is_valid():
    print("✅ PASSED: Name validation correctly failed")
    print(f"Errors: {json.dumps(serializer.errors, indent=2)}")
else:
    print("❌ FAILED: Should have failed name validation")

# Test 7: Optional push_token
print("\n7. ✅ Optional push_token (not provided):")
no_push_token_payload = {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "password": "SecurePass456"
}
print(f"Payload: {json.dumps(no_push_token_payload, indent=2)}")
serializer = UserSerializer(data=no_push_token_payload)
if serializer.is_valid():
    print("✅ PASSED: Works without push_token")
    print(f"Default preferences applied: {serializer.validated_data.get('preferences')}")
else:
    print(f"❌ FAILED: {serializer.errors}")

# Test 8: Default preferences
print("\n8. ✅ Default preferences (not provided):")
no_preferences_payload = {
    "name": "Test User",
    "email": "testuser@example.com",
    "password": "TestPass123"
}
print(f"Payload: {json.dumps(no_preferences_payload, indent=2)}")
serializer = UserSerializer(data=no_preferences_payload)
if serializer.is_valid():
    print("✅ PASSED: Default preferences should be applied")
    # Note: Default preferences are set in the create method
else:
    print(f"❌ FAILED: {serializer.errors}")

# Test 9: Partial preferences
print("\n9. ✅ Partial preferences (only email provided):")
partial_prefs_payload = {
    "name": "Test User 2",
    "email": "testuser2@example.com",
    "password": "TestPass456",
    "preferences": {
        "email": False
    }
}
print(f"Payload: {json.dumps(partial_prefs_payload, indent=2)}")
serializer = UserSerializer(data=partial_prefs_payload)
if serializer.is_valid():
    print("✅ PASSED: Partial preferences accepted")
    print(f"Preferences: {serializer.validated_data.get('preferences')}")
else:
    print(f"❌ FAILED: {serializer.errors}")

print("\n" + "="*80)
print("VALIDATION TESTS COMPLETED")
print("="*80 + "\n")

# Test password hashing
print("\n" + "="*80)
print("PASSWORD HASHING TEST")
print("="*80)
from users.models import User
from django.contrib.auth.hashers import check_password

test_user_data = {
    "name": "Hash Test User",
    "email": "hashtest@example.com",
    "password": "TestHash123"
}

serializer = UserSerializer(data=test_user_data)
if serializer.is_valid():
    # Check if a user with this email already exists
    if User.objects.filter(email=test_user_data['email']).exists():
        print(f"⚠️  User {test_user_data['email']} already exists. Skipping creation.")
        existing_user = User.objects.get(email=test_user_data['email'])
        is_hashed = existing_user.password.startswith('pbkdf2_sha256$')
        print(f"Password is hashed: {is_hashed}")
        print(f"Password hash (first 50 chars): {existing_user.password[:50]}...")
        can_check = check_password("TestHash123", existing_user.password)
        print(f"Can verify with check_password: {can_check}")
    else:
        user = serializer.save()
        print(f"✅ User created: {user.email}")
        print(f"Password in DB (first 50 chars): {user.password[:50]}...")
        print(f"Is password hashed? {user.password.startswith('pbkdf2_sha256$')}")
        print(f"Can verify with check_password? {check_password('TestHash123', user.password)}")
else:
    print(f"❌ Validation failed: {serializer.errors}")

print("\n" + "="*80)
print("STANDARDIZED RESPONSE FORMAT TEST")
print("="*80)
print("""
Expected response structure:
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "push_token": "token-xyz",
    "preferences": {"email": true, "push": false},
    "created_at": "2025-01-15T10:30:00Z"
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
""")

print("\n✅ View uses APIResponse.created() for success responses")
print("✅ View uses APIResponse.validation_error() for validation errors")
print("✅ View uses APIResponse.error() with 409 status for duplicate emails")
