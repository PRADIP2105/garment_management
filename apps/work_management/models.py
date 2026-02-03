from django.db import models
from apps.companies.models import Company
from apps.workers.models import Worker
from apps.materials.models import RawMaterial


class WorkType(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['company', 'name']

    def __str__(self):
        return self.name


class WorkDistribution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('partially_returned', 'Partially Returned'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    work_type = models.ForeignKey(WorkType, on_delete=models.CASCADE)
    lot_size = models.PositiveIntegerField()
    distributed_date = models.DateField()
    expected_return_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.worker.name} - {self.work_type.name} - {self.lot_size}"


class DistributedMaterial(models.Model):
    work_distribution = models.ForeignKey(WorkDistribution, on_delete=models.CASCADE, related_name='materials')
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    issued_quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.material.material_name} - {self.issued_quantity}"


class WorkReturn(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    work_distribution = models.ForeignKey(WorkDistribution, on_delete=models.CASCADE, related_name='returns')
    completed_quantity = models.PositiveIntegerField()
    pending_quantity = models.PositiveIntegerField()
    return_date = models.DateField()
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return - {self.work_distribution.worker.name} - {self.completed_quantity}"


class ReturnedMaterial(models.Model):
    work_return = models.ForeignKey(WorkReturn, on_delete=models.CASCADE, related_name='materials')
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    returned_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wastage_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.material.material_name} - Returned: {self.returned_quantity}, Wastage: {self.wastage_quantity}"