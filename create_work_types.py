#!/usr/bin/env python
"""
Create default work types for testing
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garment_management.settings')
django.setup()

from apps.work_management.models import WorkType
from apps.companies.models import Company

def create_work_types():
    """Create default work types for all companies"""
    
    default_work_types = [
        {'name': 'Stitching', 'description': 'Basic stitching work'},
        {'name': 'Button Work', 'description': 'Button hole and button attachment'},
        {'name': 'Collar Work', 'description': 'Collar stitching and finishing'},
        {'name': 'Color Work', 'description': 'Dyeing and color work'},
        {'name': 'Finishing', 'description': 'Final finishing and pressing'},
    ]
    
    companies = Company.objects.all()
    
    for company in companies:
        print(f"Creating work types for company: {company.name}")
        
        for work_type_data in default_work_types:
            work_type, created = WorkType.objects.get_or_create(
                company=company,
                name=work_type_data['name'],
                defaults={'description': work_type_data['description']}
            )
            
            if created:
                print(f"  ✓ Created: {work_type.name}")
            else:
                print(f"  - Already exists: {work_type.name}")
    
    print(f"\nWork types created for {companies.count()} companies")

if __name__ == '__main__':
    create_work_types()