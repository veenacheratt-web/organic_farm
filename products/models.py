# products/models.py

from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import FarmerProfile
from django.utils.text import slugify

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    icon_class = models.CharField(max_length=50, default='fas fa-leaf')
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = (
        ('kg', 'Kilogram (kg)'),
        ('g', 'Gram (g)'),
        ('dozen', 'Dozen'),
        ('piece', 'Piece'),
        ('bunch', 'Bunch'),
    )
    
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_organic_certified = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.farmer.farm_name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Create a slug from the product name
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # Ensure uniqueness
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        from reviews.models import Review
        result = Review.objects.filter(product=self).aggregate(models.Avg('rating'))
        return result['rating__avg'] or 0
    
    @property
    def review_count(self):
        """Get total number of reviews"""
        from reviews.models import Review
        return Review.objects.filter(product=self).count()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/gallery/')
    caption = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Image for {self.product.name}"