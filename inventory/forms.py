from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_id', 'product_name', 'category', 'brand', 'unit_price', 'supplier']
        widgets = {
            'unit_price': forms.NumberInput(attrs={'step': '0.01'}),
        }
        
    def clean_product_id(self):
        product_id = self.cleaned_data.get('product_id')
        if not product_id:
            raise forms.ValidationError("Product ID cannot be empty.")
        return product_id
    
    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')
        if not product_name:
            raise forms.ValidationError("Product Name cannot be empty.")
        return product_name
    
    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError("Category cannot be empty.")
        return category
    
    def clean_brand(self):
        brand = self.cleaned_data.get('brand')
        if not brand:
            raise forms.ValidationError("Brand cannot be empty.")
        return brand
    
    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price is None or unit_price < 0:
            raise forms.ValidationError("Unit Price must be a positive number.")
        return unit_price
    
    def clean_supplier(self):
        supplier = self.cleaned_data.get('supplier')
        if not supplier:
            raise forms.ValidationError("Supplier cannot be empty.")
        return supplier
    
