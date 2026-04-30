# orders/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Order, OrderItem
from .forms import CheckoutForm
from cart.models import Cart
from products.models import Product
from accounts.models import FarmerProfile


@login_required
def checkout(request):
    """Display checkout page and process order"""
    cart = Cart.objects.filter(user=request.user).first()
    
    if not cart or cart.total_items == 0:
        messages.warning(request, 'Your cart is empty. Please add some products first.')
        return redirect('cart:cart_detail')
    
    # Calculate totals using Decimal
    subtotal = cart.subtotal
    shipping_threshold = Decimal('50.00')
    shipping_cost = Decimal('5.00') if subtotal > 0 and subtotal < shipping_threshold else Decimal('0.00')
    tax_rate = Decimal('0.05')
    tax = subtotal * tax_rate
    total = subtotal + shipping_cost + tax
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create order
                    order = form.save(commit=False)
                    order.customer = request.user
                    order.subtotal = subtotal
                    order.shipping_cost = shipping_cost
                    order.tax = tax
                    order.total_amount = total
                    
                    # For COD, payment is pending until delivery
                    if order.payment_method == 'cod':
                        order.payment_status = 'pending'
                        order.status = 'confirmed'  # Auto-confirm for COD
                    else:
                        order.payment_status = 'pending'  # Will be updated after card payment
                        order.status = 'pending'
                    
                    order.save()
                    
                    # Create order items and deduct stock
                    for cart_item in cart.items.select_related('product'):
                        product = cart_item.product
                        
                        # Check stock again before finalizing
                        if cart_item.quantity > product.stock_quantity:
                            raise Exception(f'Sorry, {product.name} is now out of stock or has insufficient quantity.')
                        
                        # Deduct stock
                        product.stock_quantity -= cart_item.quantity
                        product.save()
                        
                        # Create order item
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            farmer=product.farmer,
                            quantity=cart_item.quantity,
                            price_at_purchase=product.price,
                        )
                    
                    # Clear cart
                    cart.clear_cart()
                    
                    messages.success(request, f'Order #{order.order_number} placed successfully!')
                    
                    # For COD, redirect to order detail
                    if order.payment_method == 'cod':
                        return redirect('orders:order_detail', order_id=order.id)
                    else:
                        # For card payment, redirect to dummy payment page
                        return redirect('orders:dummy_payment', order_id=order.id)
                    
            except Exception as e:
                messages.error(request, str(e))
                return redirect('cart:cart_detail')
    else:
        # Pre-fill form with user's saved data if available
        initial_data = {}
        if request.user.address:
            initial_data['delivery_address'] = request.user.address
        if request.user.phone:
            initial_data['phone_number'] = request.user.phone
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'tax': tax,
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def dummy_payment(request, order_id):
    """Dummy payment page for card payments"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.payment_status == 'paid':
        messages.info(request, 'This order has already been paid.')
        return redirect('orders:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        # Simulate payment processing
        card_number = request.POST.get('card_number', '').replace(' ', '')
        expiry = request.POST.get('expiry')
        cvv = request.POST.get('cvv')
        
        # Basic validation (dummy - accept any valid format)
        if len(card_number) >= 15 and len(cvv) == 3:
            # Simulate successful payment
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.transaction_id = f'TXN-{order.order_number}-{int(timezone.now().timestamp())}'
            order.save()
            
            messages.success(request, 'Payment successful! Your order has been confirmed.')
            return redirect('orders:order_detail', order_id=order.id)
        else:
            messages.error(request, 'Invalid payment details. Please try again.')
    
    return render(request, 'orders/dummy_payment.html', {'order': order})


@login_required
def order_detail(request, order_id):
    """Display order details"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    order_items = order.items.select_related('product').all()
    
    # Check which products can be reviewed
    from reviews.models import Review
    reviewable_products = []
    for item in order_items:
        has_reviewed = Review.objects.filter(
            product=item.product, 
            customer=request.user
        ).exists()
        reviewable_products.append({
            'product': item.product,
            'can_review': order.status == 'delivered' and not has_reviewed,
            'has_reviewed': has_reviewed
        })
    
    context = {
        'order': order,
        'order_items': order_items,
        'reviewable_products': reviewable_products,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_list(request):
    """Display all orders for the customer"""
    orders = Order.objects.filter(customer=request.user).order_by('-order_date')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def cancel_order(request, order_id):
    """Cancel an order if not yet shipped"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status in ['pending', 'confirmed']:
        # Restore stock
        for item in order.items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.save()
        
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'Order #{order.order_number} has been cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled as it has already been shipped.')
    
    return redirect('orders:order_detail', order_id=order.id)


def confirm_delivery(request, order_id):
    """Customer confirms delivery (enables reviews)"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status == 'shipped':
        order.status = 'delivered'
        order.delivered_date = timezone.now()
        order.save()
        messages.success(request, f'Order #{order.order_number} marked as delivered! You can now review your purchased products.')
    else:
        messages.error(request, 'This order cannot be marked as delivered.')
    
    return redirect('orders:order_detail', order_id=order.id)


# Farmer order management views
@login_required
def farmer_orders(request):
    """Display orders for the farmer's products"""
    if not request.user.is_farmer:
        messages.error(request, 'Access denied.')
        return redirect('pages:home')
    
    farmer_profile = FarmerProfile.objects.get(user=request.user)
    
    # Get all order items for this farmer's products
    order_items = OrderItem.objects.filter(farmer=farmer_profile).select_related('order', 'product').order_by('-order__order_date')
    
    # Group by order
    orders_dict = {}
    for item in order_items:
        if item.order.id not in orders_dict:
            orders_dict[item.order.id] = {
                'order': item.order,
                'items': []
            }
        orders_dict[item.order.id]['items'].append(item)
    
    orders = list(orders_dict.values())
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/farmer_orders.html', context)


@login_required
def farmer_update_order_status(request, order_id, status):
    """Update order status (for farmers)"""
    if not request.user.is_farmer:
        messages.error(request, 'Access denied.')
        return redirect('pages:home')
    
    order = get_object_or_404(Order, id=order_id)
    
    valid_statuses = ['confirmed', 'processing', 'shipped', 'delivered']
    if status in valid_statuses:
        order.status = status
        if status == 'delivered':
            order.delivered_date = timezone.now()
        order.save()
        messages.success(request, f'Order #{order.order_number} status updated to {status}.')
    else:
        messages.error(request, 'Invalid status update.')
    
    return redirect('orders:farmer_orders')