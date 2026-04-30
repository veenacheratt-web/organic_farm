# reviews/urls.py

from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:product_id>/', views.add_review, name='add_review'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('helpful/<int:review_id>/', views.mark_helpful, name='mark_helpful'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
]