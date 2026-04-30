# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, FarmerProfile, CustomerProfile

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'address', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'customer'
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.address = self.cleaned_data['address']
        if commit:
            user.save()
            # Create customer profile
            CustomerProfile.objects.create(
                user=user,
                default_delivery_address=self.cleaned_data['address']
            )
        return user


class FarmerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    farm_name = forms.CharField(max_length=100, required=True)
    farm_location = forms.CharField(max_length=200, required=True)
    bio = forms.CharField(widget=forms.Textarea, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'farm_name', 'farm_location', 'bio', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'farmer'
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
            # Create farmer profile
            FarmerProfile.objects.create(
                user=user,
                farm_name=self.cleaned_data['farm_name'],
                farm_location=self.cleaned_data['farm_location'],
                bio=self.cleaned_data['bio']
            )
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))