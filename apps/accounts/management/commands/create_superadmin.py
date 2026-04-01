from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.companies.models import Company
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a default superadmin user if not exists'

    def handle(self, *args, **kwargs):
        username = os.getenv('SUPERADMIN_USERNAME', 'superadmin')
        password = os.getenv('SUPERADMIN_PASSWORD', 'admin@1234')

        if User.objects.filter(username=username).exists():
            self.stdout.write(f'Superadmin "{username}" already exists, skipping.')
            return

        company, _ = Company.objects.get_or_create(name='Admin Company')
        User.objects.create_superuser(
            username=username,
            password=password,
            email='',
            company=company,
        )
        self.stdout.write(self.style.SUCCESS(f'Superadmin "{username}" created successfully.'))
