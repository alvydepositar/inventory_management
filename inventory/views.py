from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import ProductForm
from .models import *
from django.apps import apps
from django.forms import modelform_factory
from django.urls import reverse

def auth_login(request):
    return render(request, 'html/auth-login.html')

def manage_users(request):
    return render(request, 'html/manage-users.html')

def add_user(request):
    return add_item(request, 'inventory', 'Users')

def user_data(request):
    users = Users.objects.all().values()
    data = list(users)
    return JsonResponse({'data': data})

def edit_user(request, pk):
    if request.method == 'POST':
        form = modelform_factory(Users, fields='__all__')(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.id = pk  # Ensure we update the correct user
            user.save()
            return redirect('manage_users')  # Redirect to the user management page after saving
    else:
        user = get_object_or_404(Users, pk=pk)
        form = modelform_factory(Users, fields='__all__')(instance=user)
    
    return edit_item(request, 'inventory', 'Users', pk)

def delete_user(request, pk):
    return delete_item(request, 'inventory', 'Users', pk)

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
        product = get_object_or_404(Products, pk=id)
        modal_title = "Edit Product"
        form_action = reverse('edit_product', args=[product.pk])
        editing = True
    else:  # Adding a new product
        product = None
        modal_title = "Add New Record"
        form_action = reverse('add_product')
        editing = False

    categories = Categories.objects.all()
    brands = Brands.objects.all()
    suppliers = Suppliers.objects.all()
    
    context = {
        'modal_title': modal_title,
        'form_action': form_action,
        'editing': editing,
        'product': product,
        'categories': categories,
        'brands': brands,
        'suppliers': suppliers,
    }
    return render(request, 'html/product-catalogue.html', context)

def product_data(request):
    products = Products.objects.all().values(
        'id', 'product_id', 'product_name', 'category__name', 'category__id', 'brand__name', 'brand__id', 'unit_price', 'supplier__name', 'supplier__id', 'created_at', 'updated_at'
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
        product = get_object_or_404(Products, pk=pk)
        form = ProductForm(instance=product)
        
    return edit_item(request, 'inventory', 'Products', pk)

def delete_product(request, pk):
    return delete_item(request, 'inventory', 'Products', pk)

def product_details(request, category_id=None, brand_id=None):
    if category_id:
        category = get_object_or_404(apps.get_model('inventory', 'Categories'), pk=category_id)
        category_modal_title = "Edit Category"
        category_form_action = reverse('edit_category', args=[category.pk])
        category_editing = True
    else:
        category = None
        category_modal_title = "Add New Record"
        category_form_action = reverse('add_category')
        category_editing = False

    if brand_id:
        brand = get_object_or_404(apps.get_model('inventory', 'Brands'), pk=brand_id)
        brand_modal_title = "Edit Brand"
        brand_form_action = reverse('edit_brand', args=[brand.pk])
        brand_editing = True
    else:
        brand = None
        brand_modal_title = "Add New Record"
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

def suppliers(request, id=None):
    if id: # Editing an existing supplier
        supplier = get_object_or_404(Suppliers, pk=id)
        modal_title = "Edit Supplier"
        form_action = reverse('edit_supplier', args=[supplier.pk])
        editing = True
    else: # Adding a new supplier
        supplier = None
        modal_title = "Add New Record"
        form_action = reverse('add_supplier')
        editing = False
    context = {
        'modal_title': modal_title,
        'form_action': form_action,
        'editing': editing,
        'supplier': supplier,
    }

    return render(request, 'html/suppliers.html', context)

def supplier_data(request):
    suppliers = apps.get_model('inventory', 'Suppliers').objects.all().values('id', 'name', 'contact_person', 'contact_number', 'email', 'address')
    data = list(suppliers)
    return JsonResponse({'data': data})

def add_supplier(request):
    return add_item(request, 'inventory', 'Suppliers')

def edit_supplier(request, pk):
    return edit_item(request, 'inventory', 'Suppliers', pk)

def delete_supplier(request, pk):
    return delete_item(request, 'inventory', 'Suppliers', pk)

def branches(request, id=None):
    if id:  # Editing an existing branch
        branch = get_object_or_404(Branches, pk=id)
        modal_title = "Edit Branch"
        form_action = reverse('edit_branch', args=[branch.pk])
        editing = True
    else:  # Adding a new branch
        branch = None
        modal_title = "Add New Record"
        form_action = reverse('add_branch')
        editing = False

    context = {
        'modal_title': modal_title,
        'form_action': form_action,
        'editing': editing,
        'branch': branch,
    }
    return render(request, 'html/branches.html', context)

def add_branch(request):
    return add_item(request, 'inventory', 'Branches')

def edit_branch(request, pk):
    return edit_item(request, 'inventory', 'Branches', pk)

def delete_branch(request, pk):
    return delete_item(request, 'inventory', 'Branches', pk)

def branch_data(request):
    branches = apps.get_model('inventory', 'Branches').objects.all().values('id', 'name', 'location')
    data = list(branches)
    return JsonResponse({'data': data})

def manage_stocks(request, branch_id=None, stock_id=None):
    if branch_id:
        branches = get_object_or_404(Branches, pk=branch_id)
        stocks = StockLevel.objects.filter(branch=branches).select_related('product')
        products = Products.objects.all().select_related('brand')
    
    else:
        branches = Branches.objects.all()
        stocks = StockLevel.objects.all().select_related('product')
        products = Products.objects.all().select_related('brand')
        
    if stock_id:
        stock = get_object_or_404(StockLevel, pk=stock_id, branch=branch)
        modal_title = "Edit Stock"
        form_action = reverse('edit_stock')
        editing = True
    else:
        stock = None
        modal_title = "Add New Stock"
        form_action = reverse('add_stock')
        editing = False
        
    context = {
            'branches': branches,
            'stocks': stocks,
            'modal_title': modal_title,
            'form_action': form_action,
            'editing': editing,
            'stock': stock,
            'products': products,
        }
        
    return render(request, 'html/manage-stocks.html', context)

def stock_data(_request, branch_id=None):
    if branch_id:
        stocks = StockLevel.objects.filter(branch__id=branch_id).values('id', 'product__product_name', 'product__brand__name', 'quantity', 'branch__id', 'product__id', 'product__brand__name', 'product__brand__id')
    else:
        stocks = StockLevel.objects.all().values('id', 'product__product_name', 'product__brand__name', 'quantity', 'branch__id', 'product__id', 'product__brand__name', 'product__brand__id')
    stock_levels = []
    for stock in stocks:
        if stock['quantity'] < 10:
            stock['stock_level'] = 'Low'
        elif stock['quantity'] < 50:
            stock['stock_level'] = 'Medium'
        else:
            stock['stock_level'] = 'High'
        stock_levels.append(stock)
    data = list(stock_levels)
    return JsonResponse({'data': data})

def add_stock(request):
    return add_item(request, 'inventory', 'StockMovement')

def edit_stock(request, pk):
    return edit_item(request, 'inventory', 'StockMovement', pk)

def delete_stock(request, pk):
    return delete_item(request, 'inventory', 'StockMovement', pk)