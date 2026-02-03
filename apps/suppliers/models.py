from django.db import models
from apps.companies.models import Company


class Supplier(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['company', 'mobile_number']

    def __str__(self):
        return self.name