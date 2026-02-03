from django.db import models
from apps.companies.models import Company
from apps.materials.models import RawMaterial


class StockLedger(models.Model):
    TRANSACTION_TYPES = [
        ('inward', 'Inward'),
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('wastage', 'Wastage'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    balance_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    reference_type = models.CharField(max_length=50)  # 'inward', 'distribution', 'return'
    reference_id = models.PositiveIntegerField()
    transaction_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.material.material_name} - {self.transaction_type} - {self.quantity}"


class CurrentStock(models.Model):
    """Current stock summary for each material"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    current_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['company', 'material']

    def __str__(self):
        return f"{self.material.material_name} - {self.current_quantity} {self.material.unit}"