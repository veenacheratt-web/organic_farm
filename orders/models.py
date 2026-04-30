# orders/models.py

from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from decimal import Decimal

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Delivery details
    delivery_address = models.TextField()
    phone_number = models.CharField(max_length=15)
    delivery_instructions = models.TextField(blank=True, null=True)
    
    # Payment details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Financial details - use DecimalField with max_digits and decimal_places
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    delivered_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            import datetime
            self.order_number = f"ORD-{datetime.datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)
        
    def can_review(self, product):
        """Check if this order can review a specific product"""
        return self.status == 'delivered' and self.orderitem_set.filter(product=product).exists()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    farmer = models.ForeignKey('accounts.FarmerProfile', on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.order_number})"
    
    def save(self, *args, **kwargs):
        self.total_price = Decimal(str(self.price_at_purchase)) * Decimal(str(self.quantity))
        if not self.farmer:
            self.farmer = self.product.farmer
        super().save(*args, **kwargs)