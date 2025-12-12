"""
Quick test script to verify backend is working
"""
import requests
import sys

BACKEND_URL = "http://localhost:8000"

def test_backend():
    print("=" * 50)
    print("Testing Backend Server")
    print("=" * 50)
    print()
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if resp.status_code == 200:
            print(f"   ✅ Backend is ONLINE")
            print(f"   Response: {resp.json()}")
        else:
            print(f"   ❌ Backend returned status: {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend is OFFLINE")
        print("   → Please start the backend server first!")
        print("   → Run: uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print()
    print("=" * 50)
    print("✅ Backend is working correctly!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)

