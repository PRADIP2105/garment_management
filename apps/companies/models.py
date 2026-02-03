from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('staff', 'Staff'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('gu', 'Gujarati'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    mobile_number = models.CharField(max_length=15, blank=True)
    language_preference = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.company.name}"