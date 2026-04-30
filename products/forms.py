# products/forms.py

from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'unit', 'stock_quantity', 'image', 'is_organic_certified', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'min': 0}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label="All Categories")
    min_price = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Min $'}))
    max_price = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Max $'}))
    organic_only = forms.BooleanField(required=False, label="Certified Organic Only")
    in_stock_only = forms.BooleanField(required=False, label="In Stock Only")
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search products...'}))