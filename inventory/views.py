from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import ProductForm
from .models import *
from django.apps import apps
from django.forms import modelform_factory
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, time as dt_time
from django.db.models import Q
from functools import wraps
from django.contrib.auth import authenticate, login as django_login, logout as django_logout, get_user_model
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username') or ''
        password = request.POST.get('password') or ''
        user = authenticate(request, username=identifier, password=password)
        if not user:
            # Try authenticating by email
            U = get_user_model()
            u = U.objects.filter(email=identifier).first()
            if u:
                user = authenticate(request, username=u.username, password=password)
        # Legacy fallback: if Django auth fails, check app Users (plaintext) and migrate
        if not user:
            try:
                legacy = Users.objects.filter(is_active=True).filter(Q(username=identifier) | Q(email=identifier)).get()
                if legacy.password and legacy.password == password:
                    U = get_user_model()
                    # Ensure a Django user exists and has this password hashed
                    dj = U.objects.filter(Q(username__iexact=legacy.username) | Q(email__iexact=legacy.email)).first()
                    if not dj:
                        # Create new Django auth user
                        username = legacy.username or legacy.email.split('@')[0]
                        dj = U.objects.create(username=username, email=legacy.email, first_name=legacy.first_name or '', last_name=legacy.last_name or '', is_active=legacy.is_active)
                    # Update password to the provided one (hashed)
                    dj.set_password(password)
                    dj.is_active = legacy.is_active
                    dj.save()
                    user = authenticate(request, username=dj.username, password=password)
            except Users.DoesNotExist:
                pass
        if user:
            django_login(request, user)
            # Session expiry: session-only unless 'remember' is checked
            if not request.POST.get('remember'):
                request.session.set_expiry(0)
            # Map to app Users for handled_by purposes
            app_user = Users.objects.filter(Q(username=user.username) | Q(email=user.email)).first()
            if app_user:
                request.session['user_id'] = app_user.id
                request.session['user_role'] = app_user.user_role
            # Redirect to next if it's a safe local URL
            next_url = request.POST.get('next') or request.GET.get('next')
            from django.utils.http import url_has_allowed_host_and_scheme
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('product_catalogue')
        return render(request, 'html/auth-login.html', {'error': 'Invalid credentials'})
    return render(request, 'html/auth-login.html')

def logout_view(request):
    django_logout(request)
    return redirect('auth_login')

@login_required
def manage_users(request):
    return render(request, 'html/manage-users.html')

@login_required
def add_user(request):
    return add_item(request, 'inventory', 'Users')

@login_required
def user_data(request):
    users = Users.objects.all().values('id', 'username', 'email', 'first_name', 'last_name', 'user_role', 'is_active', 'date_joined')
    data = list(users)
    return JsonResponse({'data': data})

@login_required
def edit_user(request, pk):
    user = get_object_or_404(Users, pk=pk)
    ModelForm = modelform_factory(Users, fields='__all__')
    if request.method == 'POST':
        data = request.POST.copy()
        if not data.get('password'):
            # Do not overwrite password with empty string
            data.pop('password', None)
        form = ModelForm(data, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'User updated successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)

@login_required
def delete_user(request, pk):
    return delete_item(request, 'inventory', 'Users', pk)

@login_required
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
    return add_item(request, 'inventory', 'Products')

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
            return JsonResponse({'success': True, 'message': 'Product updated successfully!'})
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

@login_required
def manage_stocks(request, branch_id=None, stock_id=None):
    # Support query param for branch_id as well
    if branch_id is None:
        q_branch_id = request.GET.get('branch_id')
        if q_branch_id:
            try:
                branch_id = int(q_branch_id)
            except ValueError:
                branch_id = None
    branch = None
    if branch_id:
        branch = get_object_or_404(Branches, pk=branch_id)
        stocks = StockLevel.objects.filter(branch=branch).select_related('product', 'product__brand')
        products = Products.objects.all().select_related('brand')
        branches_list = Branches.objects.all()
    else:
        branches_list = Branches.objects.all()
        stocks = StockLevel.objects.all().select_related('product', 'product__brand')
        products = Products.objects.all().select_related('brand')

    if stock_id:
        stock = get_object_or_404(StockLevel, pk=stock_id, branch=branch) if branch else get_object_or_404(StockLevel, pk=stock_id)
        modal_title = "Edit Stock"
        form_action = reverse('edit_stock', args=[stock.pk])
        editing = True
    else:
        stock = None
        modal_title = "Add New Stock"
        form_action = reverse('add_stock')
        editing = False

    context = {
        'branch': branch,
        'branches': branches_list,
        'stocks': stocks,
        'modal_title': modal_title,
        'form_action': form_action,
        'editing': editing,
        'stock': stock,
        'products': products,
    }

    return render(request, 'html/manage-stocks.html', context)

@login_required
def stock_history(request):
    branches_list = Branches.objects.all()
    products = Products.objects.all().select_related('brand')
    branch = None
    branch_id = request.GET.get('branch_id')
    if branch_id:
        try:
            branch = Branches.objects.get(pk=int(branch_id))
        except (Branches.DoesNotExist, ValueError):
            branch = None
    context = {
        'branch': branch,
        'branches': branches_list,
        'products': products,
    }
    return render(request, 'html/stock-history.html', context)

@login_required
def dashboard(request):
    counts = {
        'products': Products.objects.count(),
        'categories': Categories.objects.count(),
        'brands': Brands.objects.count(),
        'suppliers': Suppliers.objects.count(),
        'branches': Branches.objects.count(),
        'stock_items': StockLevel.objects.count(),
        'total_quantity': StockLevel.objects.aggregate(total=models.Sum('quantity'))['total'] or 0,
        'low_stock': StockLevel.objects.filter(quantity__lt=10).count(),
    }
    return render(request, 'html/dashboard.html', {'counts': counts})

@login_required
def account(request):
    dj_user = request.user
    app_user = Users.objects.filter(Q(username=dj_user.username) | Q(email=dj_user.email)).first()
    return render(request, 'html/account.html', {'dj_user': dj_user, 'app_user': app_user})

@login_required
def account_update(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')
    email = request.POST.get('email', '')
    user = request.user
    user.first_name = first_name
    user.last_name = last_name
    if email:
        user.email = email
    user.save()
    # Mirror into app Users if exists
    app_user = Users.objects.filter(Q(username=user.username) | Q(email=user.email)).first()
    if app_user:
        app_user.first_name = first_name
        app_user.last_name = last_name
        if email:
            app_user.email = email
        app_user.save()
    return JsonResponse({'success': True, 'message': 'Profile updated'})

@login_required
def account_change_password(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    current = request.POST.get('current_password')
    new = request.POST.get('new_password')
    confirm = request.POST.get('confirm_password')
    if not new or new != confirm:
        return JsonResponse({'success': False, 'message': 'Passwords do not match'}, status=400)
    if not request.user.check_password(current):
        return JsonResponse({'success': False, 'message': 'Current password incorrect'}, status=400)
    request.user.set_password(new)
    request.user.save()
    return JsonResponse({'success': True, 'message': 'Password changed. Please login again.'})

def movement_data(request):
    branch_id = request.GET.get('branch_id')
    product_id = request.GET.get('product_id')
    txn_type = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    qs = StockMovement.objects.select_related('branch', 'product', 'product__brand', 'handled_by').all()
    if branch_id:
        qs = qs.filter(branch__id=branch_id)
    if product_id:
        qs = qs.filter(product__id=product_id)
    if txn_type in ['IN', 'OUT']:
        qs = qs.filter(transaction_type=txn_type)
    # Robust ISO date parsing (YYYY-MM-DD or full ISO timestamps)
    def _parse_date(s, end=False):
        if not s:
            return None
        try:
            # If only a date is provided, attach start/end of day
            if len(s) == 10:
                d = datetime.fromisoformat(s)
                dt = datetime.combine(d.date(), dt_time.max if end else dt_time.min)
            else:
                dt = datetime.fromisoformat(s)
            # Make aware if settings use TZ
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            return dt
        except Exception:
            return None

    dt_from = _parse_date(date_from, end=False)
    dt_to = _parse_date(date_to, end=True)
    if dt_from:
        qs = qs.filter(date__gte=dt_from)
    if dt_to:
        qs = qs.filter(date__lte=dt_to)

    data = list(qs.values(
        'id', 'transaction_id', 'transaction_type', 'quantity', 'remarks', 'balance_after',
        'date',
        'branch__id', 'branch__name',
        'product__id', 'product__product_name', 'product__brand__name',
        'handled_by__id', 'handled_by__username'
    ))
    return JsonResponse({'data': data})

@login_required
def stock_data(request, branch_id=None):
    qs = StockLevel.objects.all()
    if branch_id:
        qs = qs.filter(branch__id=branch_id)
    # Optional filter by product id
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            qs = qs.filter(product__id=int(product_id))
        except ValueError:
            pass
    stocks = qs.values('id', 'product__product_name', 'product__brand__name', 'quantity', 'branch__id', 'product__id', 'product__brand__name', 'product__brand__id', 'branch__name')
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

def _generate_transaction_id() -> str:
    ts = timezone.now().strftime('%Y%m%d%H%M%S')
    return f"SM-{ts}"

def _apply_movement_to_stocklevel(branch, product, transaction_type, quantity):
    stock_level, _ = StockLevel.objects.get_or_create(branch=branch, product=product, defaults={"quantity": 0})
    if transaction_type == 'IN':
        stock_level.quantity = stock_level.quantity + quantity
    else:
        new_qty = stock_level.quantity - quantity
        if new_qty < 0:
            raise ValueError('Insufficient stock for this operation.')
        stock_level.quantity = new_qty
    stock_level.save()
    return stock_level

def add_stock(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    try:
        branch_id = int(request.POST.get('branch')) if request.POST.get('branch') else None
        product_id = int(request.POST.get('product')) if request.POST.get('product') else None
        transaction_type = request.POST.get('transaction_type')
        quantity = int(request.POST.get('quantity') or 0)
        remarks = request.POST.get('remarks') or ''
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'message': 'Invalid input values.'}, status=400)

    if not branch_id or not product_id or transaction_type not in ['IN', 'OUT'] or quantity <= 0:
        return JsonResponse({'success': False, 'message': 'Missing or invalid fields.'}, status=400)

    branch = get_object_or_404(Branches, pk=branch_id)
    product = get_object_or_404(Products, pk=product_id)

    # Determine handler from session if available
    handled_by = None
    user_id = request.session.get('user_id')
    if user_id:
        try:
            handled_by = Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
            handled_by = None

    try:
        level = _apply_movement_to_stocklevel(branch, product, transaction_type, quantity)
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

    StockMovement.objects.create(
        transaction_id=_generate_transaction_id(),
        transaction_type=transaction_type,
        branch=branch,
        product=product,
        quantity=quantity,
        remarks=remarks,
        handled_by=handled_by,
        balance_after=level.quantity
    )

    return JsonResponse({'success': True, 'message': 'Stock movement recorded successfully.'})

def edit_stock(request, pk):
    movement = get_object_or_404(StockMovement, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    # Revert the old movement first
    revert_type = 'OUT' if movement.transaction_type == 'IN' else 'IN'
    try:
        _apply_movement_to_stocklevel(movement.branch, movement.product, revert_type, movement.quantity)
    except ValueError as e:
        return JsonResponse({'success': False, 'message': f'Failed to revert previous movement: {e}'}, status=400)

    # Apply new values
    try:
        branch_id = int(request.POST.get('branch')) if request.POST.get('branch') else None
        product_id = int(request.POST.get('product')) if request.POST.get('product') else None
        transaction_type = request.POST.get('transaction_type')
        quantity = int(request.POST.get('quantity') or 0)
        remarks = request.POST.get('remarks') or ''
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'message': 'Invalid input values.'}, status=400)

    if not branch_id or not product_id or transaction_type not in ['IN', 'OUT'] or quantity <= 0:
        return JsonResponse({'success': False, 'message': 'Missing or invalid fields.'}, status=400)

    branch = get_object_or_404(Branches, pk=branch_id)
    product = get_object_or_404(Products, pk=product_id)

    try:
        level = _apply_movement_to_stocklevel(branch, product, transaction_type, quantity)
    except ValueError as e:
        # If new apply fails, re-apply original to keep consistency
        _apply_movement_to_stocklevel(movement.branch, movement.product, movement.transaction_type, movement.quantity)
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

    movement.transaction_type = transaction_type
    movement.branch = branch
    movement.product = product
    movement.quantity = quantity
    movement.remarks = remarks
    movement.balance_after = level.quantity
    movement.save()

    return JsonResponse({'success': True, 'message': 'Stock movement updated successfully.'})

def delete_stock(request, pk):
    movement = get_object_or_404(StockMovement, pk=pk)
    # Revert the movement effect
    revert_type = 'OUT' if movement.transaction_type == 'IN' else 'IN'
    try:
        _apply_movement_to_stocklevel(movement.branch, movement.product, revert_type, movement.quantity)
    except ValueError as e:
        return JsonResponse({'success': False, 'message': f'Failed to revert movement: {e}'}, status=400)
    movement.delete()
    return JsonResponse({'success': True, 'message': 'Stock movement deleted successfully.'})
