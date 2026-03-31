from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.companies.models import Company
from apps.workers.models import Worker
from apps.suppliers.models import Supplier
from apps.materials.models import Material
from apps.work.models import MaterialInward
from apps.work.models import WorkType, WorkDistribution, WorkReceived, WorkReturn
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Add dummy data for a specific user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to add dummy data for')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
            return

        company = user.company
        self.stdout.write(f'Adding dummy data for user {username} and company {company.name}')

        # Delete existing data for the company
        self.stdout.write('Deleting existing data...')
        WorkReturn.objects.filter(company=company).delete()
        WorkReceived.objects.filter(company=company).delete()
        WorkDistribution.objects.filter(company=company).delete()
        MaterialInward.objects.filter(company=company).delete()
        Material.objects.filter(company=company).delete()
        Supplier.objects.filter(company=company).delete()
        Worker.objects.filter(company=company).delete()
        WorkType.objects.filter(company=company).delete()
        self.stdout.write('Existing data deleted successfully')

        # Add dummy workers
        workers = []
        for i in range(20):
            worker = Worker.objects.create(
                company=company,
                name=f'Worker {i+1}',
                mobile_number=f'98765432{i+1:02d}',
                address=f'Address {i+1}',
                city='Ahmedabad',
                skill_type=Worker.SkillType.STITCHING,
                machine_type=Worker.MachineType.SIMPLE,
                status=Worker.Status.ACTIVE,
                language_preference='gu'
            )
            workers.append(worker)
        self.stdout.write('Added 20 dummy workers')

        # Add dummy suppliers
        suppliers = []
        for i in range(20):
            supplier = Supplier.objects.create(
                company=company,
                name=f'Supplier {i+1}',
                mobile_number=f'91234567{i+1:02d}',
                address=f'Supplier Address {i+1}',
                city='Surat'
            )
            suppliers.append(supplier)
        self.stdout.write('Added 20 dummy suppliers')

        # Add dummy materials
        materials = []
        for i in range(20):
            material = Material.objects.create(
                company=company,
                material_name=f'Material {i+1}',
                unit='meter'
            )
            materials.append(material)
        self.stdout.write('Added 20 dummy materials')

        # Add dummy material inwards
        for i in range(20):
            MaterialInward.objects.create(
                company=company,
                material=materials[i],
                supplier=suppliers[i % 20],
                quantity=50 + i*10,
                received_date=date.today()
            )
        self.stdout.write('Added 20 dummy material inwards')

        # Add dummy work types
        work_types = []
        for i in range(20):
            work_type = WorkType.objects.create(
                company=company,
                name=f'Work Type {i+1}'
            )
            work_types.append(work_type)
        self.stdout.write('Added 20 dummy work types')

        # Add dummy work distributions
        for i in range(20):
            WorkDistribution.objects.create(
                company=company,
                worker=workers[i % 20],
                work_type=work_types[i % 20],
                lot_size=10 + i,
                distributed_date=date.today()
            )
        self.stdout.write('Added 20 dummy work distributions')

        # Add dummy work received
        for i in range(5):
            WorkReceived.objects.create(
                company=company,
                distribution=WorkDistribution.objects.filter(company=company)[i],
                received_quantity=8 + i,
                received_date=date.today()
            )
        self.stdout.write('Added 5 dummy work received entries')

        # Add dummy work returns
        for i in range(5):
            WorkReturn.objects.create(
                company=company,
                distribution=WorkDistribution.objects.filter(company=company)[i],
                completed_quantity=8 + i,
                pending_quantity=0,
                return_date=date.today()
            )
        self.stdout.write('Added 5 dummy work return entries')

        self.stdout.write(self.style.SUCCESS('Dummy data added successfully'))
