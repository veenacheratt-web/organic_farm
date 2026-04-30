# orders/forms.py

from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'phone_number', 'delivery_instructions', 'payment_method']
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your complete delivery address'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            'delivery_instructions': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any special delivery instructions?'}),
            'payment_method': forms.RadioSelect(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'payment_method':
                self.fields[field].widget.attrs['class'] = 'form-control'