from django.db import models
from apps.companies.models import Company


class Worker(models.Model):
    SKILL_CHOICES = [
        ('stitching', 'Stitching'),
        ('button', 'Button'),
        ('collar', 'Collar'),
        ('color', 'Color'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('gu', 'Gujarati'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    skill_type = models.CharField(max_length=20, choices=SKILL_CHOICES)
    machine_type = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)  # active/inactive
    language_preference = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['company', 'mobile_number']

    def __str__(self):
        return f"{self.name} - {self.skill_type}"