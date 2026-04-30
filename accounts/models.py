# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User Model with role-based flags
    """
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('farmer', 'Farmer'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.username
    
    @property
    def is_customer(self):
        return self.user_type == 'customer'
    
    @property
    def is_farmer(self):
        return self.user_type == 'farmer'


class FarmerProfile(models.Model):
    """
    Additional fields specific to farmers
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=100)
    farm_location = models.CharField(max_length=200)
    bio = models.TextField(help_text="Tell customers about your organic farming practices")
    is_organic_certified = models.BooleanField(default=False)
    certification_details = models.CharField(max_length=200, blank=True, null=True)
    established_year = models.IntegerField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)  # Admin verification
    
    def __str__(self):
        return f"{self.farm_name} - {self.user.username}"


class CustomerProfile(models.Model):
    """
    Additional fields specific to customers
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    default_delivery_address = models.TextField(blank=True, null=True)
    preferred_payment_method = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"Customer: {self.user.username}"