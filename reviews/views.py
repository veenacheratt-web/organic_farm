# reviews/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.http import JsonResponse
from products.models import Product
from orders.models import Order, OrderItem
from .models import Review, ReviewHelpful
from .forms import ReviewForm


@login_required
def add_review(request, product_id):
    """Add or edit a review for a product"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user has purchased AND received this product (delivered order)
    has_purchased_and_delivered = OrderItem.objects.filter(
        order__customer=request.user,
        product=product,
        order__status='delivered'  # Must be delivered
    ).exists()
    
    if not has_purchased_and_delivered:
        messages.error(request, 'You can only review products that have been delivered to you.')
        return redirect('products:product_detail', product_id=product.id)
    
    # Check if user already reviewed this product
    existing_review = Review.objects.filter(product=product, customer=request.user).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            if existing_review:
                # Update existing review
                existing_review.rating = form.cleaned_data['rating']
                existing_review.comment = form.cleaned_data['comment']
                existing_review.save()
                messages.success(request, 'Your review has been updated!')
            else:
                # Create new review
                review = form.save(commit=False)
                review.product = product
                review.customer = request.user
                review.is_verified_purchase = True
                review.save()
                messages.success(request, 'Thank you for your review!')
            
            return redirect('products:product_detail', product_id=product.id)
    else:
        form = ReviewForm(instance=existing_review)
    
    context = {
        'form': form,
        'product': product,
        'existing_review': existing_review,
    }
    return render(request, 'reviews/review_form.html', context)


@login_required
def delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id, customer=request.user)
    product_id = review.product.id
    review.delete()
    messages.success(request, 'Your review has been deleted.')
    return redirect('products:product_detail', product_id=product_id)


@login_required
def mark_helpful(request, review_id):
    """Mark a review as helpful"""
    review = get_object_or_404(Review, id=review_id)
    
    helpful_vote, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user,
        defaults={'is_helpful': True}
    )
    
    if not created:
        if helpful_vote.is_helpful:
            helpful_vote.delete()
            helpful = False
        else:
            helpful_vote.is_helpful = True
            helpful_vote.save()
            helpful = True
    else:
        helpful = True
    
    helpful_count = review.helpful_votes.filter(is_helpful=True).count()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'helpful': helpful, 'count': helpful_count})
    
    return redirect('products:product_detail', product_id=review.product.id)


@login_required
def my_reviews(request):
    """Display all reviews by the logged-in customer"""
    reviews = Review.objects.filter(customer=request.user).select_related('product', 'product__farmer').order_by('-created_at')
    
    context = {
        'reviews': reviews,
    }
    return render(request, 'reviews/my_reviews.html', context)