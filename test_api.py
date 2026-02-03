#!/usr/bin/env python
"""
Simple API test script for Garment Management System
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_registration():
    """Test user registration"""
    print("Testing user registration...")
    
    data = {
        "username": "testuser",
        "email": "test@example.com",
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
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=data)
    
    if response.status_code == 201:
        print("✓ Registration successful")
        return response.json()
    else:
        print(f"✗ Registration failed: {response.status_code}")
        print(response.text)
        return None

def test_login(username="testuser", password="testpass123"):
    """Test user login"""
    print("Testing user login...")
    
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=data)
    
    if response.status_code == 200:
        print("✓ Login successful")
        return response.json()
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_dashboard(token):
    """Test dashboard API"""
    print("Testing dashboard API...")
    
    headers = {"Authorization": f"Bearer {token}"}
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

def test_worker_creation(token):
    """Test worker creation"""
    print("Testing worker creation...")
    
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
    
    response = requests.post(f"{BASE_URL}/workers/", json=data, headers=headers)
    
    if response.status_code == 201:
        print("✓ Worker creation successful")
        return response.json()
    else:
        print(f"✗ Worker creation failed: {response.status_code}")
        print(response.text)
        return None

def main():
    print("=== Garment Management System API Test ===")
    
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

if __name__ == '__main__':
    main()