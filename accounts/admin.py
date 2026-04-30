# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FarmerProfile, CustomerProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'profile_picture', 'address')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(FarmerProfile)
admin.site.register(CustomerProfile)