from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import ProductForm
from .models import Product

def auth_login(request):
    return render(request, 'html/auth-login.html')

def manage_users(request):
    return render(request, 'html/manage-users.html')

def product_catalogue(request):
    return render(request, 'html/product-catalogue.html')

def product_data(request):
    products = Product.objects.all().values(
        'product_id', 'product_name', 'category', 'brand', 'unit_price', 'supplier'
    )
    data = list(products)
    return JsonResponse({'data': data})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Product added successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})