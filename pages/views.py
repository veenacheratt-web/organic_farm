# pages/views.py

from django.shortcuts import render
from products.models import Product

def home(request):
    """Home page view with featured products from database"""
    # Get featured products (first 6 available products with stock)
    featured_products = Product.objects.filter(
        is_available=True, 
        stock_quantity__gt=0
    ).order_by('-created_at')[:6]  # Get latest 6 products
    
    # Get top rated products (alternative featured products)
    from django.db.models import Avg
    top_rated_products = Product.objects.filter(
        is_available=True, 
        stock_quantity__gt=0
    ).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating')[:6]
    
    context = {
        'featured_products': featured_products,
        'top_rated_products': top_rated_products,
    }
    return render(request, 'pages/home.html', context)


def about(request):
    """About page"""
    return render(request, 'pages/about.html')


def contact(request):
    """Contact page"""
    return render(request, 'pages/contact.html')