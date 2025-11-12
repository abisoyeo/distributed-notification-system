"""
Comprehensive test suite for User Service
Covers all CRUD operations, authentication, validation, and edge cases
"""
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from django.contrib.auth import get_user_model
import json
import uuid

User = get_user_model()


class UserRegistrationTestCase(APITestCase):
    """Test cases for POST /api/v1/users/ - User registration"""
    
    def setUp(self):
        """Set up test client and base URL"""
        self.client = APIClient()
        self.url = '/api/v1/users/'
        self.valid_payload = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'password': 'SecurePass123!',
            'push_token': 'firebase-token-xyz',
            'preferences': {
                'email': True,
                'push': False
            }
        }
    
    def test_successful_user_creation_with_all_fields(self):
        """Test 1: Successful user creation with all fields"""
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        # Assert HTTP 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Assert response uses snake_case
        data = response.json()
        self.assertIn('success', data)
        self.assertIn('data', data)
        self.assertIn('error', data)
        self.assertIn('message', data)
        self.assertIn('meta', data)
        
        # Assert success response structure
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'User registered successfully')
        self.assertIsNone(data['error'])
        
        # Assert user data in response
        user_data = data['data']
        self.assertIn('id', user_data)
        self.assertEqual(user_data['name'], 'John Doe')
        self.assertEqual(user_data['email'], 'john.doe@example.com')
        self.assertEqual(user_data['push_token'], 'firebase-token-xyz')
        self.assertIn('preferences', user_data)
        self.assertEqual(user_data['preferences']['email'], True)
        self.assertEqual(user_data['preferences']['push'], False)
        self.assertIn('created_at', user_data)
        self.assertIn('updated_at', user_data)
        
        # Assert password is NOT in response
        self.assertNotIn('password', user_data)
        
        # Assert user exists in database
        user = User.objects.get(email='john.doe@example.com')
        self.assertEqual(user.name, 'John Doe')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))  # Password is hashed
    
    def test_successful_user_creation_minimal_fields(self):
        """Test 2: Successful user creation with only required fields"""
        minimal_payload = {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'password': 'SecurePass456!'
        }
        response = self.client.post(self.url, minimal_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Assert default preferences are applied
        user_data = data['data']
        self.assertIsNone(user_data['push_token'])
        self.assertEqual(user_data['preferences']['email'], True)
        self.assertEqual(user_data['preferences']['push'], True)
    
    def test_duplicate_email_handling(self):
        """Test 3: Duplicate email returns 409 Conflict"""
        # Create first user
        self.client.post(self.url, self.valid_payload, format='json')
        
        # Try to create second user with same email
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('already exists', data['error'].lower())
        self.assertEqual(data['message'], 'User registration failed')
    
    def test_missing_required_field_name(self):
        """Test 4: Missing name field returns 400"""
        invalid_payload = {
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('name', data['error'])
    
    def test_missing_required_field_email(self):
        """Test 5: Missing email field returns 400"""
        invalid_payload = {
            'name': 'Test User',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('email', data['error'])
    
    def test_missing_required_field_password(self):
        """Test 6: Missing password field returns 400"""
        invalid_payload = {
            'name': 'Test User',
            'email': 'test@example.com'
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('password', data['error'])
    
    def test_invalid_email_format(self):
        """Test 7: Invalid email format returns 400"""
        invalid_payload = {
            'name': 'Test User',
            'email': 'not-an-email',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('email', data['error'])
    
    def test_weak_password_too_short(self):
        """Test 8: Password less than 8 characters returns 400"""
        invalid_payload = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'Pass1!'
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('password', data['error'])
    
    def test_weak_password_no_uppercase(self):
        """Test 9: Password without uppercase returns 400"""
        invalid_payload = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'securepass123!'
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_weak_password_no_lowercase(self):
        """Test 10: Password without lowercase returns 400"""
        invalid_payload = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'SECUREPASS123!'
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_weak_password_no_number(self):
        """Test 11: Password without number returns 400"""
        invalid_payload = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'SecurePass!'
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_weak_password_no_special_char(self):
        """Test 12: Password without special character returns 400"""
        invalid_payload = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'SecurePass123'
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_empty_name_field(self):
        """Test 13: Empty name field returns 400"""
        invalid_payload = {
            'name': '',
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_invalid_preferences_type(self):
        """Test 14: Invalid preferences type returns 400"""
        invalid_payload = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'preferences': 'not-a-dict'
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_response_uses_snake_case(self):
        """Test 15: Verify all response fields use snake_case"""
        response = self.client.post(self.url, self.valid_payload, format='json')
        data = response.json()
        
        # Check top-level keys
        self.assertIn('success', data)
        self.assertIn('data', data)
        self.assertIn('error', data)
        self.assertIn('message', data)
        self.assertIn('meta', data)
        
        # Check user data keys
        user_data = data['data']
        self.assertIn('created_at', user_data)  # snake_case
        self.assertIn('updated_at', user_data)  # snake_case
        self.assertIn('push_token', user_data)  # snake_case
        
        # Ensure no camelCase
        self.assertNotIn('createdAt', user_data)
        self.assertNotIn('updatedAt', user_data)
        self.assertNotIn('pushToken', user_data)


class UserAuthenticationTestCase(APITestCase):
    """Test cases for POST /api/v1/auth/login - User authentication"""
    
    def setUp(self):
        """Set up test user and client"""
        self.client = APIClient()
        self.url = '/api/v1/auth/login'
        
        # Create test user
        self.test_user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPass123!',
            name='Test User'
        )
    
    def test_login_with_valid_credentials(self):
        """Test 16: Login with valid credentials returns JWT tokens"""
        payload = {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Assert response structure
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Login successful')
        
        # Assert JWT tokens present
        self.assertIn('access', data['data'])
        self.assertIn('refresh', data['data'])
        
        # Assert user data present
        self.assertIn('user', data['data'])
        user_data = data['data']['user']
        self.assertEqual(user_data['email'], 'testuser@example.com')
        self.assertEqual(user_data['name'], 'Test User')
        self.assertNotIn('password', user_data)  # Password not exposed
    
    def test_login_with_invalid_email(self):
        """Test 17: Login with non-existent email returns 401"""
        payload = {
            'email': 'nonexistent@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('Invalid email or password', data['error'])
    
    def test_login_with_invalid_password(self):
        """Test 18: Login with wrong password returns 401"""
        payload = {
            'email': 'testuser@example.com',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('Invalid email or password', data['error'])
    
    def test_login_missing_email(self):
        """Test 19: Login without email returns 400"""
        payload = {
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_login_missing_password(self):
        """Test 20: Login without password returns 400"""
        payload = {
            'email': 'testuser@example.com'
        }
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_login_response_uses_snake_case(self):
        """Test 21: Verify login response uses snake_case"""
        payload = {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, payload, format='json')
        data = response.json()
        
        # Check user data uses snake_case
        user_data = data['data']['user']
        self.assertIn('created_at', user_data)
        self.assertIn('push_token', user_data)
        
        # Ensure no camelCase
        self.assertNotIn('createdAt', user_data)
        self.assertNotIn('pushToken', user_data)


class UserRetrievalTestCase(APITestCase):
    """Test cases for GET /api/v1/users/:user_id/ - Get user by ID"""
    
    def setUp(self):
        """Set up test users and authentication"""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='TestPass123!',
            name='User One'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='TestPass123!',
            name='User Two'
        )
        
        # Get JWT token for user1
        login_response = self.client.post('/api/v1/auth/login', {
            'email': 'user1@example.com',
            'password': 'TestPass123!'
        }, format='json')
        self.token = login_response.json()['data']['access']
    
    def test_get_user_by_valid_id_own_profile(self):
        """Test 22: Get own user profile with valid ID"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = f'/api/v1/users/{self.user1.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'User retrieved successfully')
        
        user_data = data['data']
        self.assertEqual(user_data['id'], str(self.user1.id))
        self.assertEqual(user_data['email'], 'user1@example.com')
        self.assertEqual(user_data['name'], 'User One')
        self.assertNotIn('password', user_data)
    
    def test_get_user_by_invalid_uuid(self):
        """Test 23: Get user with invalid UUID format returns 400"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = '/api/v1/users/not-a-valid-uuid/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('Invalid UUID format', data['error'])
    
    def test_get_user_by_nonexistent_id(self):
        """Test 24: Get user with valid but non-existent UUID returns 404"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        fake_uuid = uuid.uuid4()
        url = f'/api/v1/users/{fake_uuid}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('not found', data['error'].lower())
    
    def test_get_user_without_authentication(self):
        """Test 25: Get user without JWT token returns 401"""
        url = f'/api/v1/users/{self.user1.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('Authentication', data['error'])
    
    def test_get_other_user_profile(self):
        """Test 26: Get another user's profile returns 403"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = f'/api/v1/users/{self.user2.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('own profile', data['error'].lower())
    
    def test_get_user_response_uses_snake_case(self):
        """Test 27: Verify user retrieval response uses snake_case"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = f'/api/v1/users/{self.user1.id}/'
        response = self.client.get(url)
        data = response.json()
        
        user_data = data['data']
        self.assertIn('created_at', user_data)
        self.assertIn('updated_at', user_data)
        self.assertIn('push_token', user_data)
        
        self.assertNotIn('createdAt', user_data)
        self.assertNotIn('updatedAt', user_data)


class PushTokenUpdateTestCase(APITestCase):
    """Test cases for PATCH /api/v1/users/:user_id/push_token - Update push token"""
    
    def setUp(self):
        """Set up test user and authentication"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPass123!',
            name='Test User'
        )
        
        # Get JWT token
        login_response = self.client.post('/api/v1/auth/login', {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        }, format='json')
        self.token = login_response.json()['data']['access']
    
    def test_update_push_token_success(self):
        """Test 28: Successfully update push token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = f'/api/v1/users/{self.user.id}/push_token'
        payload = {'push_token': 'new-firebase-token-xyz'}
        
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Push token updated successfully')
        self.assertEqual(data['data']['push_token'], 'new-firebase-token-xyz')
        
        # Verify database was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.push_token, 'new-firebase-token-xyz')
    
    def test_update_push_token_remove(self):
        """Test 29: Remove push token by setting to null"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = f'/api/v1/users/{self.user.id}/push_token'
        payload = {'push_token': None}
        
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsNone(data['data']['push_token'])
    
    def test_update_push_token_missing_field(self):
        """Test 30: Update without push_token field returns 400"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = f'/api/v1/users/{self.user.id}/push_token'
        payload = {}
        
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_update_push_token_invalid_uuid(self):
        """Test 31: Update with invalid UUID returns 400"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = '/api/v1/users/invalid-uuid/push_token'
        payload = {'push_token': 'new-token'}
        
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_update_push_token_without_auth(self):
        """Test 32: Update without authentication returns 401"""
        url = f'/api/v1/users/{self.user.id}/push_token'
        payload = {'push_token': 'new-token'}
        
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_push_token_response_uses_snake_case(self):
        """Test 33: Verify push token update response uses snake_case"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = f'/api/v1/users/{self.user.id}/push_token'
        payload = {'push_token': 'new-token'}
        
        response = self.client.patch(url, payload, format='json')
        data = response.json()
        
        self.assertIn('push_token', data['data'])
        self.assertNotIn('pushToken', data['data'])


class PreferencesUpdateTestCase(APITestCase):
    """Test cases for GET/PATCH /api/v1/users/:user_id/preferences"""
    
    def setUp(self):
        """Set up test user and authentication"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPass123!',
            name='Test User'
        )
        
        # Get JWT token
        login_response = self.client.post('/api/v1/auth/login', {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        }, format='json')
        self.token = login_response.json()['data']['access']
    
    def test_get_preferences_success(self):
        """Test 34: Successfully get user preferences"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = f'/api/v1/users/{self.user.id}/preferences'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertIn('email', data['data'])
        self.assertIn('push', data['data'])
        self.assertIsInstance(data['data']['email'], bool)
        self.assertIsInstance(data['data']['push'], bool)
    
    def test_update_preferences_success(self):
        """Test 35: Successfully update preferences"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = f'/api/v1/users/{self.user.id}/preferences'
        payload = {
            'email': False,
            'push': True
        }
        
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Preferences updated successfully')
        self.assertEqual(data['data']['email'], False)
        self.assertEqual(data['data']['push'], True)
        
        # Verify database was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.preferences['email'], False)
        self.assertEqual(self.user.preferences['push'], True)
    
    def test_update_preferences_partial(self):
        """Test 36: Update only one preference field"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = f'/api/v1/users/{self.user.id}/preferences'
        payload = {'email': False}
        
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['email'], False)
    
    def test_update_preferences_invalid_type(self):
        """Test 37: Update with non-boolean value returns 400"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = f'/api/v1/users/{self.user.id}/preferences'
        payload = {'email': 'not-a-boolean'}
        
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_get_preferences_without_auth(self):
        """Test 38: Get preferences without authentication returns 401"""
        url = f'/api/v1/users/{self.user.id}/preferences'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_preferences_response_uses_snake_case(self):
        """Test 39: Verify preferences response uses snake_case"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = f'/api/v1/users/{self.user.id}/preferences'
        
        response = self.client.get(url)
        data = response.json()
        
        # Preferences are simple: {email: bool, push: bool}
        # Just verify top-level response structure uses snake_case
        self.assertIn('success', data)
        self.assertIn('data', data)
        self.assertIn('error', data)
        self.assertIn('message', data)


class HealthCheckTestCase(APITestCase):
    """Test cases for health check endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
    
    def test_health_check_endpoint(self):
        """Test 40: GET /health returns service status"""
        url = '/health'
        response = self.client.get(url)
        
        # Should return 200 or 503 depending on service health
        self.assertIn(response.status_code, [200, 503])
        
        data = response.json()
        
        # Assert response structure
        self.assertIn('success', data)
        self.assertIn('message', data)
        self.assertIn('data', data)
        
        # Assert health data fields
        health_data = data['data']
        self.assertIn('database', health_data)
        self.assertIn('redis', health_data)
        self.assertIn('timestamp', health_data)
        
        # Database should be connected (since we're running tests)
        self.assertEqual(health_data['database'], 'connected')
    
    def test_liveness_endpoint(self):
        """Test 41: GET /health/liveness returns alive status"""
        url = '/health/liveness'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Service is alive')
        self.assertIn('timestamp', data['data'])
    
    def test_readiness_endpoint(self):
        """Test 42: GET /health/readiness checks database"""
        url = '/health/readiness'
        response = self.client.get(url)
        
        # Should return 200 if database is ready
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Service is ready')
        self.assertIn('database', data['data'])
        self.assertEqual(data['data']['database'], 'connected')
    
    def test_health_endpoints_no_auth_required(self):
        """Test 43: Health endpoints don't require authentication"""
        # Test all health endpoints without authentication
        urls = ['/health', '/health/liveness', '/health/readiness']
        
        for url in urls:
            response = self.client.get(url)
            # Should not return 401 Unauthorized
            self.assertNotEqual(response.status_code, 401)
    
    def test_health_response_uses_snake_case(self):
        """Test 44: Verify health check response uses snake_case"""
        url = '/health'
        response = self.client.get(url)
        data = response.json()
        
        # Check top-level keys
        self.assertIn('success', data)
        self.assertIn('message', data)
        self.assertIn('data', data)
        
        # Ensure no camelCase
        self.assertNotIn('statusCode', data)
        self.assertNotIn('healthData', data)


class EdgeCaseTestCase(APITestCase):
    """Additional edge case tests"""
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
    
    def test_sql_injection_in_email(self):
        """Test 45: SQL injection attempt in email field"""
        payload = {
            'name': 'Test User',
            'email': "test@example.com' OR '1'='1",
            'password': 'SecurePass123!'
        }
        response = self.client.post('/api/v1/users/', payload, format='json')
        
        # Should be treated as invalid email
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_xss_in_name_field(self):
        """Test 46: XSS attempt in name field"""
        payload = {
            'name': '<script>alert("XSS")</script>',
            'email': 'xss@example.com',
            'password': 'SecurePass123!'
        }
        response = self.client.post('/api/v1/users/', payload, format='json')
        
        # Should create user but sanitize the name
        # Django ORM handles this by default
        if response.status_code == 201:
            data = response.json()
            # Name should be stored as-is (Django templates will escape it)
            self.assertEqual(data['data']['name'], '<script>alert("XSS")</script>')
    
    def test_very_long_name(self):
        """Test 47: Very long name field (boundary test)"""
        payload = {
            'name': 'A' * 1000,  # Very long name
            'email': 'longname@example.com',
            'password': 'SecurePass123!'
        }
        response = self.client.post('/api/v1/users/', payload, format='json')
        
        # Should either accept or reject based on model field constraints
        self.assertIn(response.status_code, [201, 400])
    
    def test_unicode_in_name(self):
        """Test 48: Unicode characters in name field"""
        payload = {
            'name': '测试用户 Tëst Ûsér 🚀',
            'email': 'unicode@example.com',
            'password': 'SecurePass123!'
        }
        response = self.client.post('/api/v1/users/', payload, format='json')
        
        # Should handle Unicode correctly
        if response.status_code == 201:
            data = response.json()
            self.assertEqual(data['data']['name'], '测试用户 Tëst Ûsér 🚀')
    
    def test_case_insensitive_email_duplicate(self):
        """Test 49: Duplicate email with different case"""
        # Create first user
        payload1 = {
            'name': 'User One',
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        self.client.post('/api/v1/users/', payload1, format='json')
        
        # Try to create second user with uppercase email
        payload2 = {
            'name': 'User Two',
            'email': 'TEST@EXAMPLE.COM',
            'password': 'SecurePass456!'
        }
        response = self.client.post('/api/v1/users/', payload2, format='json')
        
        # Should be treated as duplicate
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
    
    def test_empty_request_body(self):
        """Test 50: Empty request body"""
        response = self.client.post('/api/v1/users/', {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data['success'])

