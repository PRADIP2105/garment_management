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

        company, _ = Company.objects.get_or_create(name='Admin Company')

        user, created = User.objects.get_or_create(username=username)

        # Always force correct flags and password
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.company = company
        user.save()

        status = 'created' if created else 'updated'
        self.stdout.write(self.style.SUCCESS(
            f'Superadmin "{username}" {status}. '
            f'is_staff={user.is_staff}, is_superuser={user.is_superuser}, is_active={user.is_active}'
        ))
