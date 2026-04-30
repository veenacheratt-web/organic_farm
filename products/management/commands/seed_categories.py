# products/management/commands/seed_categories.py

from django.core.management.base import BaseCommand
from products.models import Category

class Command(BaseCommand):
    help = 'Seed initial categories'
    
    def handle(self, *args, **kwargs):
        categories = [
            {'name': 'Fruits', 'slug': 'fruits', 'icon_class': 'fas fa-apple-alt'},
            {'name': 'Vegetables', 'slug': 'vegetables', 'icon_class': 'fas fa-carrot'},
            {'name': 'Leafy Greens', 'slug': 'leafy-greens', 'icon_class': 'fas fa-leaf'},
            {'name': 'Root Vegetables', 'slug': 'root-vegetables', 'icon_class': 'fas fa-seedling'},
            {'name': 'Exotic Produce', 'slug': 'exotic', 'icon_class': 'fas fa-globe'},
            {'name': 'Herbs', 'slug': 'herbs', 'icon_class': 'fas fa-spa'},
        ]
        
        for cat in categories:
            Category.objects.get_or_create(
                name=cat['name'],
                defaults={'slug': cat['slug'], 'icon_class': cat['icon_class']}
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded categories'))