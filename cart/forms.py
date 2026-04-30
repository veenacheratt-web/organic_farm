# cart/forms.py

from django import forms

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=99, initial=1)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

class CartUpdateForm(forms.Form):
    quantity = forms.IntegerField(min_value=0, max_value=99)