# products/urls.py

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('farmer/<int:farmer_id>/', views.farmer_public_profile, name='farmer_public_profile'),
    
    # Farmer routes
    path('farmer/products/', views.farmer_product_list, name='farmer_product_list'),
    path('farmer/products/create/', views.farmer_product_create, name='farmer_product_create'),
    path('farmer/products/<int:product_id>/edit/', views.farmer_product_edit, name='farmer_product_edit'),
    path('farmer/products/<int:product_id>/delete/', views.farmer_product_delete, name='farmer_product_delete'),
]