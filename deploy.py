#!/usr/bin/env python
"""
Deployment script for Garment Management System
"""
import os
import sys
import subprocess

def run_command(command, check=True):
    """Run a shell command"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=check)
    return result.returncode == 0

def main():
    print("=== Garment Management System Deployment ===")
    
    # Check if we're in production mode
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    if debug:
        print("Warning: DEBUG is set to True. This should be False in production.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Install requirements
    print("\n1. Installing requirements...")
    if not run_command("pip install -r requirements.txt"):
        print("Failed to install requirements")
        sys.exit(1)
    
    # Run migrations
    print("\n2. Running migrations...")
    if not run_command("python manage.py migrate"):
        print("Failed to run migrations")
        sys.exit(1)
    
    # Collect static files
    print("\n3. Collecting static files...")
    if not run_command("python manage.py collectstatic --noinput"):
        print("Failed to collect static files")
        sys.exit(1)
    
    # Check deployment
    print("\n4. Checking deployment...")
    run_command("python manage.py check --deploy", check=False)
    
    print("\n=== Deployment Complete ===")
    print("Your application is ready for production!")
    print("\nRecommended next steps:")
    print("1. Set up a proper web server (nginx + gunicorn)")
    print("2. Configure SSL/HTTPS")
    print("3. Set up monitoring and logging")
    print("4. Configure backup for your database")

if __name__ == '__main__':
    main()