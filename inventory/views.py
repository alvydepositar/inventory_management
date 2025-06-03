from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import ProductForm
from .models import Product
from django.apps import apps
from django.forms import modelform_factory
from django.urls import reverse

def auth_login(request):
    return render(request, 'html/auth-login.html')

def manage_users(request):
    return render(request, 'html/manage-users.html')

def product_catalogue(request, id=None):
    if id:  # Editing an existing product
        product = get_object_or_404(Product, pk=id)
        modal_title = "Edit Product"
        form_action = reverse('edit_product', args=[product.pk])
        editing = True
    else:  # Adding a new product
        product = None
        modal_title = "Add New Product"
        form_action = reverse('add_product')
        editing = False

    context = {
        'modal_title': modal_title,
        'form_action': form_action,
        'editing': editing,
        'product': product,
    }
    return render(request, 'html/product-catalogue.html', context)

def add_item(request, app_label, model_name):
    """
    A dynamic view to add items to the database for different models.

    Args:
        request: The HTTP request object.
        app_label: The label of the Django app (e.g., 'inventory').
        model_name: The name of the model (e.g., 'Product').

    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    try:
        # Retrieve the model class dynamically
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return JsonResponse({'success': False, 'message': 'Invalid model name.'})

    # Create a dynamic form class
    ModelForm = modelform_factory(model, fields='__all__')

    if request.method == 'POST':
        form = ModelForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': f'{model_name} added successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def edit_item(request, app_label, model_name, item_id):
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return JsonResponse({'success': False, 'message': 'Invalid model name.'})

    try:
        item = model.objects.get(pk=item_id)
    except model.DoesNotExist:
        return JsonResponse({'success': False, 'message': f'{model_name} not found.'})

    ModelForm = modelform_factory(model, fields='__all__')

    if request.method == 'POST':
        form = ModelForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': f'{model_name} updated successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)

def delete_item(request, app_label, model_name, item_id):
    """
    A dynamic view to delete items from the database for different models.

    Args:
        request: The HTTP request object.
        app_label: The label of the Django app (e.g., 'inventory').
        model_name: The name of the model (e.g., 'Product').
        item_id: The ID of the item to be deleted.

    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    try:
        # Retrieve the model class dynamically
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return JsonResponse({'success': False, 'message': 'Invalid model name.'})

    try:
        # Retrieve the item to be deleted
        item = model.objects.get(pk=item_id)
        item.delete()
        return JsonResponse({'success': True, 'message': f'{model_name} deleted successfully!'})
    except model.DoesNotExist:
        return JsonResponse({'success': False, 'message': f'{model_name} not found.'})

def product_data(request):
    products = Product.objects.all().values(
        'id', 'product_id', 'product_name', 'category', 'brand', 'unit_price', 'supplier'
    )
    data = list(products)
    return JsonResponse({'data': data})

def add_product(request):
    return add_item(request, 'inventory', 'Product')

def edit_product(request, pk):
    """
    Edit a product by its primary key (pk).
    If the request method is POST, it updates the product with the provided data.
    
    """
    # Open the modal with the product data
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.id = pk  # Ensure we update the correct product
            product.save()
            return redirect('product_catalogue')  # Redirect to the product catalogue after saving
    else:
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(instance=product)
        
    return edit_item(request, 'inventory', 'Product', pk)

def delete_product(request, pk):
    return delete_item(request, 'inventory', 'Product', pk)

