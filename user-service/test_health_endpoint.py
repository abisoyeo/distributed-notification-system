"""
Test script for health check endpoint
"""
import requests
import json

def test_health_endpoint():
    """Test the /health endpoint"""
    url = "http://localhost:8000/health"
    
    print("="*80)
    print("Testing GET /health endpoint")
    print("="*80)
    
    try:
        response = requests.get(url, timeout=5)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'content-length', 'date']:
                print(f"  {key}: {value}")
        
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
        # Validate response structure
        data = response.json()
        print("\n" + "="*80)
        print("Response Validation:")
        print("="*80)
        
        assert 'success' in data, "Missing 'success' field"
        print("✅ Has 'success' field:", data['success'])
        
        assert 'message' in data, "Missing 'message' field"
        print("✅ Has 'message' field:", data['message'])
        
        assert 'data' in data, "Missing 'data' field"
        print("✅ Has 'data' field")
        
        assert 'database' in data['data'], "Missing 'database' status"
        print("✅ Has 'database' status:", data['data']['database'])
        
        assert 'redis' in data['data'], "Missing 'redis' status"
        print("✅ Has 'redis' status:", data['data']['redis'])
        
        assert 'timestamp' in data['data'], "Missing 'timestamp'"
        print("✅ Has 'timestamp':", data['data']['timestamp'])
        
        print("\n✅ All validations passed!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("Make sure the server is running: python manage.py runserver 8000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_liveness_endpoint():
    """Test the /health/liveness endpoint"""
    url = "http://localhost:8000/health/liveness"
    
    print("\n" + "="*80)
    print("Testing GET /health/liveness endpoint")
    print("="*80)
    
    try:
        response = requests.get(url, timeout=5)
        print(f"\nStatus Code: {response.status_code}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_readiness_endpoint():
    """Test the /health/readiness endpoint"""
    url = "http://localhost:8000/health/readiness"
    
    print("\n" + "="*80)
    print("Testing GET /health/readiness endpoint")
    print("="*80)
    
    try:
        response = requests.get(url, timeout=5)
        print(f"\nStatus Code: {response.status_code}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    test_health_endpoint()
    test_liveness_endpoint()
    test_readiness_endpoint()
