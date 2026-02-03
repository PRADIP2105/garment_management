#!/usr/bin/env python
"""
Test work types API
"""
import requests

BASE_URL = "http://127.0.0.1:8000/api"

def test_work_types():
    """Test work types API"""
    print("=== Testing Work Types API ===")
    
    # Login first
    login_data = {
        "username": "logintest",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code != 200:
        print("❌ Login failed")
        return False
    
    token = response.json()['tokens']['access']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test work types API
    print("\n1. Testing work types API...")
    response = requests.get(f"{BASE_URL}/work/types/", headers=headers)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        work_types = data.get('results', [])
        print(f"✅ Work types API working - Found {len(work_types)} work types")
        
        for wt in work_types:
            print(f"  - {wt['name']}: {wt['description']}")
        
        return True
    else:
        print("❌ Work types API failed")
        print(f"Error: {response.text}")
        return False

if __name__ == '__main__':
    test_work_types()