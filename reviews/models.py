# reviews/models.py

from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from orders.models import Order

User = get_user_model()


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified_purchase = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('product', 'customer')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.username} - {self.product.name} - {self.rating} stars"
    
    def save(self, *args, **kwargs):
        # Check if customer has purchased this product
        if not self.is_verified_purchase and not self.order:
            has_purchased = OrderItem.objects.filter(
                order__customer=self.customer,
                product=self.product,
                order__status='delivered'
            ).exists()
            self.is_verified_purchase = has_purchased
        super().save(*args, **kwargs)


class ReviewHelpful(models.Model):
    """Track if users found a review helpful"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('review', 'user')
    
    def __str__(self):
        return f"{self.user.username} found review {self.review.id} helpful"