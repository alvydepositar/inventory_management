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

def product_details(request, category_id=None, brand_id=None):
    if category_id:
        category = get_object_or_404(apps.get_model('inventory', 'Categories'), pk=category_id)
        category_modal_title = "Edit Category"
        category_form_action = reverse('edit_category', args=[category.pk])
        category_editing = True
    else:
        category = None
        category_modal_title = "Add New Category"
        category_form_action = reverse('add_category')
        category_editing = False

    if brand_id:
        brand = get_object_or_404(apps.get_model('inventory', 'Brands'), pk=brand_id)
        brand_modal_title = "Edit Brand"
        brand_form_action = reverse('edit_brand', args=[brand.pk])
        brand_editing = True
    else:
        brand = None
        brand_modal_title = "Add New Brand"
        brand_form_action = reverse('add_brand')
        brand_editing = False

    context = {
        'category_modal_title': category_modal_title,
        'category_form_action': category_form_action,
        'category': category,
        'category_editing': category_editing,
        'brand_modal_title': brand_modal_title,
        'brand_form_action': brand_form_action,
        'brand': brand,
        'brand_editing': brand_editing,
    }
    return render(request, 'html/product-details.html', context)

def category_data(request):
    categories = apps.get_model('inventory', 'Categories').objects.all().values('id', 'name')
    data = list(categories)
    return JsonResponse({'data': data})

def add_category(request):
    return add_item(request, 'inventory', 'Categories')

def edit_category(request, pk):
    """
    Edit a category by its primary key (pk).
    If the request method is POST, it updates the category with the provided data.
    Returns a JsonResponse for AJAX or calls edit_item for fallback.
    """
    Categories = apps.get_model('inventory', 'Categories')
    category = get_object_or_404(Categories, pk=pk)
    ModelForm = modelform_factory(Categories, fields='__all__')

    if request.method == 'POST':
        form = ModelForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Category updated successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return edit_item(request, 'inventory', 'Categories', pk)

def delete_category(request, pk):
    return delete_item(request, 'inventory', 'Categories', pk)

def brand_data(request):
    brands = apps.get_model('inventory', 'Brands').objects.all().values('id', 'name')
    data = list(brands)
    return JsonResponse({'data': data})

def add_brand(request):
    return add_item(request, 'inventory', 'Brands')

def edit_brand(request, pk):
    Brands = apps.get_model('inventory', 'Brands')
    brand = get_object_or_404(Brands, pk=pk)
    ModelForm = modelform_factory(Brands, fields='__all__')

    if request.method == 'POST':
        form = ModelForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Brand updated successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return edit_item(request, 'inventory', 'Brands', pk)

def delete_brand(request, pk):
    return delete_item(request, 'inventory', 'Brands', pk)

def supplier_data(request):
    suppliers = apps.get_model('inventory', 'Suppliers').objects.all().values('id', 'name', 'contact_info')
    data = list(suppliers)
    return JsonResponse({'data': data})

def add_supplier(request):
    return add_item(request, 'inventory', 'Suppliers')

def edit_supplier(request, pk):
    return edit_item(request, 'inventory', 'Suppliers', pk)

def delete_supplier(request, pk):
    return delete_item(request, 'inventory', 'Suppliers', pk)