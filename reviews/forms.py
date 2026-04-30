# reviews/forms.py

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control', 
                'placeholder': 'Share your experience with this product...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].choices = [
            (5, '⭐⭐⭐⭐⭐ 5 - Excellent'),
            (4, '⭐⭐⭐⭐ 4 - Very Good'),
            (3, '⭐⭐⭐ 3 - Good'),
            (2, '⭐⭐ 2 - Fair'),
            (1, '⭐ 1 - Poor')
        ]