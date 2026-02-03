#!/usr/bin/env python
"""
Test login issue specifically
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_registration_and_login():
    """Test registration and then login"""
    print("=== Testing Registration and Login Flow ===")
    
    # Create unique username
    timestamp = int(time.time())
    username = f"logintest{timestamp}"
    email = f"logintest{timestamp}@example.com"
    
    # Test registration
    print(f"\n1. Registering user: {username}")
    reg_data = {
        "username": username,
        "email": email,
        "password": "testpass123",
        "confirm_password": "testpass123",
        "company_name": "Login Test Company",
        "company_address": "123 Login Street",
        "company_city": "Login City",
        "company_mobile": "9876543210",
        "company_email": "login@test.com",
        "mobile_number": "9876543210",
        "language_preference": "en"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=reg_data)
        print(f"Registration response: {response.status_code}")
        
        if response.status_code == 201:
            print("✓ Registration successful")
            data = response.json()
            print(f"  User: {data['user']['username']}")
            print(f"  Company: {data['user']['company']['name']}")
            
            # Now test login with the same credentials
            print(f"\n2. Testing login with: {username}")
            login_data = {
                "username": username,
                "password": "testpass123"
            }
            
            login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
            print(f"Login response: {login_response.status_code}")
            
            if login_response.status_code == 200:
                print("✓ Login successful")
                login_result = login_response.json()
                print(f"  Access token received: {login_result['tokens']['access'][:20]}...")
                return True
            else:
                print("✗ Login failed")
                print(f"  Error: {login_response.text}")
                return False
        else:
            print("✗ Registration failed")
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_existing_user_login():
    """Test login with existing user"""
    print("\n=== Testing Login with Existing User ===")
    
    # Try with one of the existing users
    existing_users = [
        ("testuser123", "testpass123"),
        ("pradip", "testpass123"),
    ]
    
    for username, password in existing_users:
        print(f"\nTrying login with: {username}")
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
            print(f"Response: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✓ Login successful with {username}")
                data = response.json()
                print(f"  User: {data['user']['username']}")
                print(f"  Company: {data['user']['company']['name']}")
                return True
            else:
                print(f"✗ Login failed with {username}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Error with {username}: {str(e)}")
    
    return False

def main():
    print("=== Login Issue Diagnosis ===")
    
    # Test 1: Registration and immediate login
    if test_registration_and_login():
        print("\n🎉 Registration and login flow works!")
    else:
        print("\n❌ Registration and login flow has issues")
    
    # Test 2: Login with existing user
    if test_existing_user_login():
        print("\n🎉 Existing user login works!")
    else:
        print("\n❌ Existing user login has issues")
    
    print("\n=== Recommendations ===")
    print("1. Always register a new company first")
    print("2. Use the same credentials you registered with")
    print("3. Make sure to use the web interface at: http://127.0.0.1:8000/")

if __name__ == '__main__':
    main()