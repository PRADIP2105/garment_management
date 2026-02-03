#!/usr/bin/env python
"""
Test materials API specifically
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def get_auth_token():
    """Get authentication token"""
    reg_data = {
        "username": f"mattest{int(time.time())}",
        "email": f"mattest{int(time.time())}@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123",
        "company_name": "Materials Test Company",
        "company_address": "123 Materials Street",
        "company_city": "Materials City",
        "company_mobile": "9876543210",
        "company_email": "materials@test.com",
        "mobile_number": "9876543210",
        "language_preference": "en"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=reg_data)
    if response.status_code == 201:
        data = response.json()
        return data['tokens']['access']
    return None

def test_materials_crud():
    """Test materials CRUD operations"""
    print("=== Testing Materials API ===")
    
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return False
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test raw material creation
    print("\n1. Creating raw material...")
    material_data = {
        "material_name": "Test Fabric",
        "unit": "meter",
        "description": "Test fabric for testing"
    }
    
    response = requests.post(f"{BASE_URL}/materials/raw-materials/", json=material_data, headers=headers)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ Raw material created successfully")
        material = response.json()
        print(f"  Material: {material['material_name']} ({material['unit']})")
        return True
    else:
        print("❌ Raw material creation failed")
        print(f"  Error: {response.text}")
        return False

if __name__ == '__main__':
    test_materials_crud()