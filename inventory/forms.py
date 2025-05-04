from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_id', 'product_name', 'category', 'brand', 'unit_price', 'supplier']
        widgets = {
            'unit_price': forms.NumberInput(attrs={'step': '0.01'}),
        }