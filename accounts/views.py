# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import CustomerRegistrationForm, FarmerRegistrationForm, UserLoginForm

# accounts/views.py (add these to existing file)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, FarmerProfile, CustomerProfile
from products.models import Product
from orders.models import Order, OrderItem
from reviews.models import Review

# Add these imports at the top if not already present
from django.db.models import Sum, Count, Avg

@login_required
def customer_dashboard(request):
    """Customer dashboard with order history and stats"""
    if not request.user.is_customer:
        messages.warning(request, 'Access denied. Customer dashboard only.')
        return redirect('pages:home')
    
    # Get customer's orders
    orders = Order.objects.filter(customer=request.user).order_by('-order_date')[:5]
    
    # Get stats
    total_orders = Order.objects.filter(customer=request.user).count()
    total_spent = Order.objects.filter(customer=request.user, status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_reviews = Review.objects.filter(customer=request.user).count()
    pending_orders = Order.objects.filter(customer=request.user, status__in=['pending', 'confirmed', 'processing', 'shipped']).count()
    
    # Get products that can be reviewed (delivered but not reviewed)
    delivered_order_items = OrderItem.objects.filter(
        order__customer=request.user,
        order__status='delivered'
    ).exclude(
        product__reviews__customer=request.user
    ).select_related('product').distinct('product')
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'total_reviews': total_reviews,
        'pending_orders': pending_orders,
        'reviewable_products': delivered_order_items,
    }
    return render(request, 'accounts/customer_dashboard.html', context)


@login_required
def farmer_dashboard(request):
    """Farmer dashboard with sales analytics"""
    if not request.user.is_farmer:
        messages.warning(request, 'Access denied. Farmer dashboard only.')
        return redirect('pages:home')
    
    farmer_profile = get_object_or_404(FarmerProfile, user=request.user)
    
    # Get farmer's products
    products = Product.objects.filter(farmer=farmer_profile)
    total_products = products.count()
    total_stock = products.aggregate(Sum('stock_quantity'))['stock_quantity__sum'] or 0
    low_stock_products = products.filter(stock_quantity__lt=10)
    
    # Get order items for this farmer
    order_items = OrderItem.objects.filter(farmer=farmer_profile).select_related('order')
    
    # Stats
    total_orders = order_items.values('order').distinct().count()
    total_items_sold = order_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_revenue = order_items.filter(order__status='delivered').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Recent orders
    recent_orders = order_items.select_related('order', 'product').order_by('-order__order_date')[:10]
    
    # Average rating
    avg_rating = products.aggregate(avg=Avg('reviews__rating'))['avg'] or 0
    
    # Group orders by status
    pending_orders_count = Order.objects.filter(
        items__farmer=farmer_profile,
        status='pending'
    ).distinct().count()
    
    context = {
        'farmer': farmer_profile,
        'total_products': total_products,
        'total_stock': total_stock,
        'total_orders': total_orders,
        'total_items_sold': total_items_sold,
        'total_revenue': total_revenue,
        'avg_rating': avg_rating,
        'pending_orders_count': pending_orders_count,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/farmer_dashboard.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.address = request.POST.get('address', '')
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        
        # Update farmer profile if user is farmer
        if user.is_farmer:
            farmer_profile = user.farmer_profile
            farmer_profile.farm_name = request.POST.get('farm_name', farmer_profile.farm_name)
            farmer_profile.farm_location = request.POST.get('farm_location', farmer_profile.farm_location)
            farmer_profile.bio = request.POST.get('bio', farmer_profile.bio)
            farmer_profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:edit_profile')
    
    return render(request, 'accounts/edit_profile.html', {'user': request.user})

def register_choice(request):
    """Page to choose between customer and farmer registration"""
    return render(request, 'accounts/register_choice.html')

def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Organic Farm Marketplace.')
            return redirect('pages:home')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': 'Customer'})

def register_farmer(request):
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Farmer registration successful! Please wait for admin verification to start selling.')
            return redirect('pages:home')
    else:
        form = FarmerRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': 'Farmer'})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('pages:home')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('pages:home')