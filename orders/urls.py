# orders/urls.py

from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Customer order routes
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.dummy_payment, name='dummy_payment'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('list/', views.order_list, name='order_list'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('confirm-delivery/<int:order_id>/', views.confirm_delivery, name='confirm_delivery'),
    
    # Farmer order management routes
    path('farmer/orders/', views.farmer_orders, name='farmer_orders'),
    path('farmer/update-status/<int:order_id>/<str:status>/', views.farmer_update_order_status, name='farmer_update_status'),
]