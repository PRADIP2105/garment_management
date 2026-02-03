#!/usr/bin/env python
"""
Test dashboard functionality specifically
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_dashboard_flow():
    """Test the complete dashboard flow"""
    print("=== Testing Dashboard Flow ===")
    
    # First register a user
    print("\n1. Registering test user...")
    reg_data = {
        "username": f"dashtest{int(time.time())}",
        "email": f"dashtest{int(time.time())}@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123",
        "company_name": "Dashboard Test Company",
        "company_address": "123 Dashboard Street",
        "company_city": "Dashboard City",
        "company_mobile": "9876543210",
        "company_email": "dashboard@test.com",
        "mobile_number": "9876543210",
        "language_preference": "en"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register/", json=reg_data)
        
        if response.status_code == 201:
            print("✓ Registration successful")
            data = response.json()
            token = data['tokens']['access']
            user_data = data['user']
            print(f"  User: {user_data['username']}")
            print(f"  Company: {user_data['company']['name']}")
            
            # Test dashboard API
            print("\n2. Testing dashboard API...")
            headers = {"Authorization": f"Bearer {token}"}
            dash_response = requests.get(f"{BASE_URL}/api/dashboard/stats/", headers=headers)
            
            if dash_response.status_code == 200:
                print("✓ Dashboard API working perfectly!")
                dash_data = dash_response.json()
                print(f"  Total workers: {dash_data.get('total_workers', 0)}")
                print(f"  Completed today: {dash_data.get('completed_today', {}).get('count', 0)}")
                print(f"  Low stock items: {len(dash_data.get('low_stock_materials', []))}")
                print(f"  Date: {dash_data.get('date', 'N/A')}")
                
                # Test web dashboard page
                print("\n3. Testing web dashboard page...")
                web_response = requests.get(f"{BASE_URL}/dashboard/")
                if web_response.status_code == 200:
                    print("✓ Web dashboard page loads successfully")
                else:
                    print(f"✗ Web dashboard page failed: {web_response.status_code}")
                
                return True
            else:
                print(f"✗ Dashboard API failed: {dash_response.status_code}")
                print(dash_response.text)
                return False
        else:
            print(f"✗ Registration failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    print("=== Dashboard Functionality Test ===")
    
    if test_dashboard_flow():
        print("\n🎉 SUCCESS! Dashboard is working perfectly!")
        print("\nYou can now:")
        print("1. Go to http://127.0.0.1:8000/")
        print("2. Register your company")
        print("3. Access the dashboard")
        print("4. View real-time statistics")
        print("\nThe dashboard will show:")
        print("- Total workers count")
        print("- Completed work today")
        print("- Low stock materials")
        print("- Work distribution summary")
    else:
        print("\n❌ Dashboard test failed")
        print("Please check the server logs for more details")

if __name__ == '__main__':
    main()