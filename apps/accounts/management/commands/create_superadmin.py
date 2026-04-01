from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.companies.models import Company
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create or fix the default superadmin user'

    def handle(self, *args, **kwargs):
        username = os.getenv('SUPERADMIN_USERNAME', 'superadmin')
        password = os.getenv('SUPERADMIN_PASSWORD', 'admin@1234')

        user = User.objects.filter(username=username).first()

        if user:
            # Fix flags if they were not set correctly
            changed = False
            if not user.is_superuser:
                user.is_superuser = True
                changed = True
            if not user.is_staff:
                user.is_staff = True
                changed = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'Superadmin "{username}" updated — is_staff=True, is_superuser=True, password reset.'
            ))
        else:
            company, _ = Company.objects.get_or_create(name='Admin Company')
            User.objects.create_superuser(
                username=username,
                password=password,
                email='',
                company=company,
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS(f'Superadmin "{username}" created successfully.'))
