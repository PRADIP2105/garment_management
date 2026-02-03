#!/usr/bin/env python
"""
Create a test user for login testing
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garment_management.settings')
django.setup()

from django.contrib.auth.models import User
from apps.companies.models import Company, UserProfile

def create_test_user():
    """Create a test user with known credentials"""
    
    # Check if test user already exists
    if User.objects.filter(username='logintest').exists():
        print("Test user 'logintest' already exists")
        return
    
    try:
        # Create company
        company = Company.objects.create(
            name="Login Test Company",
            address="123 Test Street",
            city="Test City",
            mobile_number="9876543210",
            email="test@company.com"
        )
        
        # Create user
        user = User.objects.create_user(
            username='logintest',
            email='logintest@example.com',
            password='password123'
        )
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            company=company,
            role='owner',
            mobile_number='9876543210',
            language_preference='en'
        )
        
        print("✓ Test user created successfully!")
        print("  Username: logintest")
        print("  Password: password123")
        print("  Company: Login Test Company")
        
    except Exception as e:
        print(f"✗ Error creating test user: {str(e)}")

if __name__ == '__main__':
    create_test_user()