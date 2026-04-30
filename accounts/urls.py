# accounts/urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/choice/', views.register_choice, name='register_choice'),
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/farmer/', views.register_farmer, name='register_farmer'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/farmer/', views.farmer_dashboard, name='farmer_dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]