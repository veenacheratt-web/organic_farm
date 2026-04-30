# pages/urls.py

from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home, name='home'),
    #path('shop/', views.product_list, name='product_list'),
]