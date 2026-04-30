# products/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .models import Product, Category
from .forms import ProductForm, ProductFilterForm
from accounts.models import FarmerProfile
from orders.models import OrderItem  
from reviews.models import Review    

def is_farmer(user):
    return user.is_authenticated and user.is_farmer


def product_list(request):
    """Display all available products with filtering"""
    products = Product.objects.filter(is_available=True, stock_quantity__gt=0)
    
    form = ProductFilterForm(request.GET)
    if form.is_valid():
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        organic_only = form.cleaned_data.get('organic_only')
        in_stock_only = form.cleaned_data.get('in_stock_only')
        search = form.cleaned_data.get('search')
        
        if category:
            products = products.filter(category=category)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        if organic_only:
            products = products.filter(is_organic_certified=True)
        if in_stock_only:
            products = products.filter(stock_quantity__gt=0)
        if search:
            products = products.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(farmer__farm_name__icontains=search)
            )
    
    # Annotate with average rating
    products = products.annotate(avg_rating=Avg('reviews__rating'))
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'filter_form': form,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, product_id):
    """Display single product details using ID"""
    try:
        # Get the product
        product = get_object_or_404(Product, id=product_id, is_available=True)
    except Exception as e:
        messages.error(request, f'Product not found: {e}')
        return redirect('products:product_list')
    
    # Get related products (same category)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True,
        stock_quantity__gt=0
    ).exclude(id=product.id)[:4]
    
    # Get reviews for this product
    reviews = product.reviews.all().order_by('-created_at')
    
    # Check if current user has already reviewed this product
    existing_review = None
    user_has_delivered_order = False

    if request.user.is_authenticated and request.user.is_customer:
        from reviews.models import Review
        existing_review = Review.objects.filter(
            product=product, 
            customer=request.user
        ).first()
    
        # Check if user has a delivered order containing this product
        user_has_delivered_order = OrderItem.objects.filter(
            order__customer=request.user,
            product=product,
            order__status='delivered'
        ).exists()

    # Calculate average rating
    from reviews.models import Review
    avg_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'existing_review': existing_review,
        'avg_rating': avg_rating,
        'user_has_delivered_order': user_has_delivered_order,
        'review_count': reviews.count(),
    }
    return render(request, 'products/product_detail.html', context)


def farmer_public_profile(request, farmer_id):
    """Public view of a farmer's storefront"""
    try:
        farmer_profile = get_object_or_404(FarmerProfile, id=farmer_id)
    except:
        messages.error(request, 'Farmer profile not found.')
        return redirect('products:product_list')
    
    products = Product.objects.filter(
        farmer=farmer_profile, 
        is_available=True, 
        stock_quantity__gt=0
    )
    
    avg_rating = products.aggregate(Avg('reviews__rating'))['reviews__rating__avg'] or 0
    
    context = {
        'farmer': farmer_profile,
        'products': products,
        'avg_rating': avg_rating,
        'product_count': products.count(),
    }
    return render(request, 'products/farmer_public_profile.html', context)


@login_required
@user_passes_test(is_farmer)
def farmer_product_list(request):
    """Farmer dashboard - list all products of logged-in farmer"""
    farmer_profile = get_object_or_404(FarmerProfile, user=request.user)
    products = Product.objects.filter(farmer=farmer_profile).order_by('-created_at')
    
    context = {
        'products': products,
        'farmer': farmer_profile,
    }
    return render(request, 'products/farmer_product_list.html', context)


@login_required
@user_passes_test(is_farmer)
def farmer_product_create(request):
    """Farmer creates a new product"""
    farmer_profile = get_object_or_404(FarmerProfile, user=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = farmer_profile
            product.save()
            messages.success(request, f'{product.name} has been added successfully!')
            return redirect('products:farmer_product_list')
    else:
        form = ProductForm()
    
    return render(request, 'products/farmer_product_form.html', {
        'form': form,
        'title': 'Add New Product',
        'button_text': 'Add Product'
    })


@login_required
@user_passes_test(is_farmer)
def farmer_product_edit(request, product_id):
    """Farmer edits an existing product"""
    farmer_profile = get_object_or_404(FarmerProfile, user=request.user)
    product = get_object_or_404(Product, id=product_id, farmer=farmer_profile)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'{product.name} has been updated!')
            return redirect('products:farmer_product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/farmer_product_form.html', {
        'form': form,
        'title': 'Edit Product',
        'button_text': 'Update Product',
        'product': product
    })


@login_required
@user_passes_test(is_farmer)
def farmer_product_delete(request, product_id):
    """Farmer deletes a product"""
    farmer_profile = get_object_or_404(FarmerProfile, user=request.user)
    product = get_object_or_404(Product, id=product_id, farmer=farmer_profile)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'{product_name} has been deleted.')
        return redirect('products:farmer_product_list')
    
    return render(request, 'products/farmer_product_confirm_delete.html', {'product': product})