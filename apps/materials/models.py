from django.db import models
from apps.companies.models import Company
from apps.suppliers.models import Supplier


class RawMaterial(models.Model):
    UNIT_CHOICES = [
        ('meter', 'Meter'),
        ('roll', 'Roll'),
        ('piece', 'Piece'),
        ('kg', 'Kilogram'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    material_name = models.CharField(max_length=200)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['company', 'material_name']

    def __str__(self):
        return f"{self.material_name} ({self.unit})"


class MaterialInward(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    received_date = models.DateField()
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.material.material_name} - {self.quantity} {self.material.unit}"