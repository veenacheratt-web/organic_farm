# cart/context_processors.py

from .models import Cart

def cart_count(request):
    """Add cart item count to all templates"""
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            return {'cart_count': cart.total_items}
    return {'cart_count': 0}