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

def product_catalogue(request, product_id=None):
    if product_id:  # Editing an existing product
        product = get_object_or_404(Product, product_id=product_id)
        modal_title = "Edit Product"
        form_action = reverse('edit_product', args=[product_id])
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


def product_data(request):
    products = Product.objects.all().values(
        'product_id', 'product_name', 'category', 'brand', 'unit_price', 'supplier'
    )
    data = list(products)
    return JsonResponse({'data': data})


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
    """
    A dynamic view to edit items in the database for different models.

    Args:
        request: The HTTP request object.
        app_label: The label of the Django app (e.g., 'inventory').
        model_name: The name of the model (e.g., 'Product').
        item_id: The ID of the item to be edited.

    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    try:
        # Retrieve the model class dynamically
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return JsonResponse({'success': False, 'message': 'Invalid model name.'})

    try:
        # Retrieve the item to be edited
        item = model.objects.get(pk=item_id)
    except model.DoesNotExist:
        return JsonResponse({'success': False, 'message': f'{model_name} not found.'})

    # Create a dynamic form class
    ModelForm = modelform_factory(model, fields='__all__')

    if request.method == 'POST':
        form = ModelForm(request.POST, instance=item)  # instance=item for editing
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': f'{model_name} updated successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        # If it's a GET request, pre-populate the form with the item's data
        form = ModelForm(instance=item)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def add_product(request):
    return add_item(request, 'inventory', 'Product')

def edit_product(request, product_id):
    return edit_item(request, 'inventory', 'Product', product_id)