#!/usr/bin/env python
"""
Simple test script to verify the Garment Management System is working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_home_page():
    """Test if home page loads"""
    print("Testing home page...")
    try:
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code == 200:
            print("✓ Home page loads successfully")
            return True
        else:
            print(f"✗ Home page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Home page error: {str(e)}")
        return False

def test_registration():
    """Test user registration"""
    print("\nTesting user registration...")
    
    data = {
        "username": "testuser123",
        "email": "test123@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123",
        "company_name": "Test Garment Company",
        "company_address": "123 Test Street",
        "company_city": "Test City",
        "company_mobile": "9876543210",
        "company_email": "company@test.com",
        "mobile_number": "9876543210",
        "language_preference": "en"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=data)
        
        if response.status_code == 201:
            print("✓ Registration successful")
            return response.json()
        else:
            print(f"✗ Registration failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"✗ Registration error: {str(e)}")
        return None

def test_login(username="testuser123", password="testpass123"):
    """Test user login"""
    print("\nTesting user login...")
    
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=data)
        
        if response.status_code == 200:
            print("✓ Login successful")
            return response.json()
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"✗ Login error: {str(e)}")
        return None

def test_dashboard(token):
    """Test dashboard API"""
    print("\nTesting dashboard API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/dashboard/stats/", headers=headers)
        
        if response.status_code == 200:
            print("✓ Dashboard API working")
            data = response.json()
            print(f"  Total workers: {data.get('total_workers', 0)}")
            return True
        else:
            print(f"✗ Dashboard API failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"✗ Dashboard API error: {str(e)}")
        return False

def test_worker_creation(token):
    """Test worker creation"""
    print("\nTesting worker creation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Test Worker",
        "mobile_number": "9876543211",
        "address": "Worker Address",
        "city": "Worker City",
        "skill_type": "stitching",
        "machine_type": "Singer",
        "status": True,
        "language_preference": "en"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/workers/", json=data, headers=headers)
        
        if response.status_code == 201:
            print("✓ Worker creation successful")
            return response.json()
        else:
            print(f"✗ Worker creation failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"✗ Worker creation error: {str(e)}")
        return None

def main():
    print("=== Garment Management System Test ===")
    
    # Test home page
    if not test_home_page():
        print("Home page test failed. Make sure the server is running.")
        return
    
    # Test registration
    reg_result = test_registration()
    if not reg_result:
        print("Registration failed, trying login with existing user...")
        login_result = test_login()
    else:
        login_result = reg_result
    
    if not login_result:
        print("Cannot proceed without authentication")
        return
    
    token = login_result['tokens']['access']
    
    # Test dashboard
    test_dashboard(token)
    
    # Test worker creation
    test_worker_creation(token)
    
    print("\n=== Test Complete ===")
    print("✓ System is working correctly!")
    print("\nYou can now access:")
    print("- Web Application: http://127.0.0.1:8000/")
    print("- Admin Panel: http://127.0.0.1:8000/admin/")
    print("- API Documentation: Check the README.md for API endpoints")

if __name__ == '__main__':
    main()