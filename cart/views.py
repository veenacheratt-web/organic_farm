# cart/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from .models import Cart, CartItem
from products.models import Product
from .forms import CartAddProductForm, CartUpdateForm


def get_or_create_cart(request):
    """Helper function to get or create cart for logged-in user"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    return None


@login_required
def cart_detail(request):
    """Display cart contents"""
    cart = get_or_create_cart(request)
    
    if cart:
        cart_items = cart.items.select_related('product').all()
        subtotal = cart.subtotal
        
        # Use Decimal for all monetary values
        shipping_threshold = Decimal('50.00')
        shipping_cost = Decimal('5.00') if subtotal > 0 and subtotal < shipping_threshold else Decimal('0.00')
        tax_rate = Decimal('0.05')
        tax = subtotal * tax_rate
        total = subtotal + shipping_cost + tax
        
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'tax': tax,
            'total': total,
        }
    else:
        context = {
            'cart_items': [],
            'subtotal': Decimal('0.00'),
            'shipping_cost': Decimal('0.00'),
            'tax': Decimal('0.00'),
            'total': Decimal('0.00'),
        }
    
    return render(request, 'cart/cart_detail.html', context)


@require_POST
@login_required
def cart_add(request, product_id):
    """Add product to cart"""
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        
        # Check stock availability
        if quantity > product.stock_quantity:
            messages.error(request, f'Sorry, only {product.stock_quantity} units of {product.name} are available.')
            return redirect('products:product_detail', product_id=product.id)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Check if new total quantity exceeds stock
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock_quantity:
                messages.error(request, f'Cannot add {quantity} more. Only {product.stock_quantity - cart_item.quantity} left in stock.')
            else:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, f'Added {quantity} x {product.name} to your cart.')
        else:
            messages.success(request, f'Added {product.name} to your cart.')
    
    return redirect('cart:cart_detail')


@require_POST
@login_required
def cart_remove(request, item_id):
    """Remove item from cart"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Removed {product_name} from your cart.')
    return redirect('cart:cart_detail')


@require_POST
@login_required
def cart_update(request, item_id):
    """Update item quantity in cart"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    form = CartUpdateForm(request.POST)
    
    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        
        if quantity == 0:
            cart_item.delete()
            messages.info(request, f'Removed {cart_item.product.name} from your cart.')
        else:
            # Check stock availability
            if quantity > cart_item.product.stock_quantity:
                messages.error(request, f'Sorry, only {cart_item.product.stock_quantity} units available.')
            else:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, f'Updated {cart_item.product.name} quantity to {quantity}.')
    
    return redirect('cart:cart_detail')


@login_required
def cart_count(request):
    """AJAX endpoint to get cart item count"""
    if request.user.is_authenticated:
        cart = get_or_create_cart(request)
        if cart:
            count = cart.total_items
            return JsonResponse({'count': count})
    return JsonResponse({'count': 0})