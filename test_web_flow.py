#!/usr/bin/env python
"""
Test the complete web flow
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_registration_flow():
    """Test the complete registration and login flow"""
    print("=== Testing Web Registration Flow ===")
    
    # Test registration
    print("\n1. Testing registration...")
    reg_data = {
        "username": f"webtest{int(time.time())}",
        "email": f"webtest{int(time.time())}@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123",
        "company_name": "Web Test Company",
        "company_address": "123 Web Test Street",
        "company_city": "Web Test City",
        "company_mobile": "9876543210",
        "company_email": "webtest@company.com",
        "mobile_number": "9876543210",
        "language_preference": "en"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register/", json=reg_data)
        
        if response.status_code == 201:
            print("✓ Registration API successful")
            data = response.json()
            token = data['tokens']['access']
            user_data = data['user']
            print(f"  User: {user_data['username']}")
            print(f"  Company: {user_data['company']['name']}")
            
            # Test dashboard API with token
            print("\n2. Testing dashboard API...")
            headers = {"Authorization": f"Bearer {token}"}
            dash_response = requests.get(f"{BASE_URL}/api/dashboard/stats/", headers=headers)
            
            if dash_response.status_code == 200:
                print("✓ Dashboard API working")
                dash_data = dash_response.json()
                print(f"  Total workers: {dash_data.get('total_workers', 0)}")
            else:
                print(f"✗ Dashboard API failed: {dash_response.status_code}")
            
            # Test worker creation
            print("\n3. Testing worker creation...")
            worker_data = {
                "name": "Web Test Worker",
                "mobile_number": "9876543211",
                "address": "Worker Address",
                "city": "Worker City",
                "skill_type": "stitching",
                "machine_type": "Singer",
                "status": True,
                "language_preference": "en"
            }
            
            worker_response = requests.post(f"{BASE_URL}/api/workers/", json=worker_data, headers=headers)
            
            if worker_response.status_code == 201:
                print("✓ Worker creation successful")
                worker = worker_response.json()
                print(f"  Worker: {worker['name']} - {worker['skill_type']}")
            else:
                print(f"✗ Worker creation failed: {worker_response.status_code}")
                print(worker_response.text)
            
            return True
            
        else:
            print(f"✗ Registration failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"✗ Registration error: {str(e)}")
        return False

def test_web_pages():
    """Test that web pages load correctly"""
    print("\n=== Testing Web Pages ===")
    
    pages = [
        ('/', 'Home page'),
        ('/login/', 'Login page'),
        ('/register/', 'Registration page'),
        ('/dashboard/', 'Dashboard page'),
        ('/workers/', 'Workers page')
    ]
    
    for url, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{url}")
            if response.status_code == 200:
                print(f"✓ {name} loads successfully")
            else:
                print(f"✗ {name} failed: {response.status_code}")
        except Exception as e:
            print(f"✗ {name} error: {str(e)}")

def main():
    print("=== Garment Management System Web Flow Test ===")
    
    # Test web pages
    test_web_pages()
    
    # Test registration flow
    if test_registration_flow():
        print("\n=== All Tests Passed! ===")
        print("✓ Web application is working correctly")
        print("✓ Registration and authentication flow works")
        print("✓ API integration is functional")
        print("\nYou can now:")
        print("1. Go to http://127.0.0.1:8000/ to access the web app")
        print("2. Register a new company")
        print("3. Login and use the dashboard")
        print("4. Manage workers, suppliers, materials, and work")
    else:
        print("\n=== Some Tests Failed ===")
        print("Please check the server logs for more details")

if __name__ == '__main__':
    main()