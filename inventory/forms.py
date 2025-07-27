from django import forms
from .models import *

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
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
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['name']
    name = forms.CharField(max_length=100, required=True, label='Category Name')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Category Name cannot be empty.")
        return name

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Suppliers
        fields = ['name', 'contact_person', 'contact_number', 'email', 'address']
    name = forms.CharField(max_length=100, required=True, label='Supplier Name')
    contact_person = forms.CharField(max_length=100, required=True, label='Contact Person')
    contact_number = forms.CharField(max_length=15, required=False, label='Contact Number')
    email = forms.EmailField(required=False, label='Email')
    address = forms.CharField(widget=forms.Textarea, required=False, label='Address')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Supplier Name cannot be empty.")
        return name

    def clean_contact_person(self):
        contact_person = self.cleaned_data.get('contact_person')
        if not contact_person:
            raise forms.ValidationError("Contact Person cannot be empty.")
        return contact_person

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if not contact_number:
            raise forms.ValidationError("Contact Number cannot be empty.")
        return contact_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email cannot be empty.")
        return email

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            raise forms.ValidationError("Address cannot be empty.")
        return address

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brands
        fields = ['name']
    name = forms.CharField(max_length=100, required=True, label='Brand Name')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Brand Name cannot be empty.")
        return name
    
class BranchForm(forms.ModelForm):
    class Meta:
        model = Branches
        fields = ['name', 'location']
    name = forms.CharField(max_length=100, required=True, label='Branch Name')
    location = forms.CharField(max_length=255, required=False, label='Location')
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Branch Name cannot be empty.")
        return name
    def clean_location(self):
        location = self.cleaned_data.get('location')
        if not location:
            raise forms.ValidationError("Location cannot be empty.")
        return location

class StockForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['branch', 'product', 'quantity', 'remarks', 'handled_by']
    transaction_type = forms.ChoiceField(choices=StockMovement.TRANSACTION_CHOICES, required=True, label='Transaction Type')
    branch = forms.ModelChoiceField(queryset=Branches.objects.all(), required=True, label='Branch')
    product = forms.ModelChoiceField(queryset=Products.objects.all(), required=True, label='Products')
    quantity = forms.IntegerField(min_value=0, required=True, label='Quantity')
    remarks = forms.CharField(widget=forms.Textarea, required=False, label='Remarks')
    handled_by = forms.ModelChoiceField(queryset=Users.objects.all(), required=False, label='Handled By')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].label_from_instance = lambda obj: f"{obj.product_name} ({obj.brand.name})"