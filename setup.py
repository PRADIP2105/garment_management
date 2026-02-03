#!/usr/bin/env python
"""
Setup script for Garment Management System
"""
import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command):
    """Run a shell command"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garment_management.settings')
    django.setup()

def main():
    print("=== Garment Management System Setup ===")
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Virtual environment not detected. It's recommended to use a virtual environment.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Install requirements
    print("\n1. Installing requirements...")
    if not run_command("pip install -r requirements.txt"):
        print("Failed to install requirements")
        sys.exit(1)
    
    # Setup Django
    setup_django()
    
    # Create migrations
    print("\n2. Creating migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    # Run migrations
    print("\n3. Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create superuser
    print("\n4. Creating superuser...")
    print("You'll be prompted to create a superuser account.")
    try:
        execute_from_command_line(['manage.py', 'createsuperuser'])
    except KeyboardInterrupt:
        print("\nSuperuser creation skipped.")
    
    # Collect static files
    print("\n5. Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    print("\n=== Setup Complete ===")
    print("To start the development server, run:")
    print("python manage.py runserver")
    print("\nTo start the mobile app, run:")
    print("python mobile_app.py")
    print("\nAccess the web application at: http://localhost:8000")

if __name__ == '__main__':
    main()