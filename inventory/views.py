from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
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
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

ADMIN_ROLES = {'admin'}


def _json_or_forbidden(request, message='Forbidden'):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': message}, status=403)
    raise PermissionDenied(message)


def _get_user_role(request):
    role = request.session.get('user_role')
    if not role and hasattr(request.user, 'user_role'):
        role = getattr(request.user, 'user_role', None)
    if not role and getattr(request.user, 'is_superuser', False):
        role = 'admin'
    return role


def _get_assigned_branch_id(request):
    return request.session.get('assigned_branch_id')


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            role = _get_user_role(request)
            if role in allowed_roles or role in ADMIN_ROLES:
                return view_func(request, *args, **kwargs)
            return _json_or_forbidden(request, 'You do not have permission to access this resource.')

        return _wrapped

    return decorator


def _resolve_branch_scope(request, incoming_branch_id):
    """
    For branch managers, force the branch to their assigned branch and block cross-branch access.
    """
    role = _get_user_role(request)
    if role != 'branch_manager':
        return incoming_branch_id
    assigned = _get_assigned_branch_id(request)
    if not assigned:
        raise PermissionDenied('No branch assigned to this user.')
    if incoming_branch_id:
        try:
            incoming_int = int(incoming_branch_id)
        except (TypeError, ValueError):
            raise PermissionDenied('Invalid branch.')
        if incoming_int != assigned:
            raise PermissionDenied('Branch access denied.')
    return assigned


def _sync_auth_user(app_user, raw_password=None):
    """
    Ensure a corresponding Django auth user exists and is updated.
    Password is updated only when raw_password is provided.
    """
    U = get_user_model()
    dj_user = U.objects.filter(Q(username__iexact=app_user.username) | Q(email__iexact=app_user.email)).first()
    if not dj_user:
        dj_user = U(username=app_user.username or app_user.email.split('@')[0] if app_user.email else '')
    dj_user.email = app_user.email or dj_user.email
    dj_user.first_name = app_user.first_name or ''
    dj_user.last_name = app_user.last_name or ''
    dj_user.is_active = app_user.is_active
    if raw_password:
        dj_user.set_password(raw_password)
    dj_user.username = app_user.username
    dj_user.save()
    return dj_user

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
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
                if legacy.password and (legacy.password == password or check_password(password, legacy.password)):
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
                request.session['assigned_branch_id'] = app_user.assigned_branch_id
            # Redirect to next if it's a safe local URL
            next_url = request.POST.get('next') or request.GET.get('next')
            from django.utils.http import url_has_allowed_host_and_scheme
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('dashboard')
        return render(request, 'html/auth-login.html', {'error': 'Invalid credentials'})
    return render(request, 'html/auth-login.html')

def logout_view(request):
    django_logout(request)
    return redirect('auth_login')

@login_required
@role_required('admin')
def manage_users(request):
    branches = Branches.objects.all()
    return render(request, 'html/manage-users.html', {'branches': branches})

@login_required
@role_required('admin')
def add_user(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)
    ModelForm = modelform_factory(Users, fields='__all__')
    data = request.POST.copy()
    raw_password = data.get('password') or ''
    if not data.get('is_active'):
        data['is_active'] = False
    form = ModelForm(data)
    if form.is_valid():
        app_user = form.save(commit=False)
        if raw_password:
            app_user.password = make_password(raw_password)
        else:
            app_user.password = ''
        app_user.save()
        _sync_auth_user(app_user, raw_password if raw_password else None)
        return JsonResponse({'success': True, 'message': 'User added successfully!'})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})

@login_required
@role_required('admin')
def user_data(request):
    users = Users.objects.all().values(
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'user_role',
        'is_active',
        'date_joined',
        'assigned_branch_id',
        'assigned_branch__name'
    )
    data = list(users)
    return JsonResponse({'data': data})

@login_required
@role_required('admin')
def edit_user(request, pk):
    user = get_object_or_404(Users, pk=pk)
    ModelForm = modelform_factory(Users, fields='__all__')
    if request.method == 'POST':
        data = request.POST.copy()
        raw_password = data.get('password') or ''
        if not raw_password:
            # Do not overwrite password with empty string
            data.pop('password', None)
        if not data.get('is_active'):
            data['is_active'] = False
        form = ModelForm(data, instance=user)
        if form.is_valid():
            app_user = form.save(commit=False)
            if raw_password:
                app_user.password = make_password(raw_password)
            app_user.save()
            _sync_auth_user(app_user, raw_password if raw_password else None)
            return JsonResponse({'success': True, 'message': 'User updated successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)

@login_required
@role_required('admin')
def delete_user(request, pk):
    return delete_item(request, 'inventory', 'Users', pk)

@login_required
@role_required('admin')
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

@login_required
@role_required('admin')
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

@login_required
@role_required('admin')
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

@login_required
@role_required('admin')
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

@login_required
@role_required('admin')
def product_data(request):
    products = Products.objects.all().values(
        'id', 'product_id', 'product_name', 'category__name', 'category__id', 'brand__name', 'brand__id', 'unit_price', 'supplier__name', 'supplier__id', 'created_at', 'updated_at'
    )
    data = list(products)
    return JsonResponse({'data': data})

@login_required
@role_required('admin')
def add_product(request):
    return add_item(request, 'inventory', 'Products')

@login_required
@role_required('admin')
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

@login_required
@role_required('admin')
def delete_product(request, pk):
    return delete_item(request, 'inventory', 'Products', pk)

@login_required
@role_required('admin')
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

@login_required
@role_required('admin')
def category_data(request):
    categories = apps.get_model('inventory', 'Categories').objects.all().values('id', 'name')
    data = list(categories)
    return JsonResponse({'data': data})

@login_required
@role_required('admin')
def add_category(request):
    return add_item(request, 'inventory', 'Categories')

@login_required
@role_required('admin')
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

@login_required
@role_required('admin')
def delete_category(request, pk):
    return delete_item(request, 'inventory', 'Categories', pk)

@login_required
@role_required('admin')
def brand_data(request):
    brands = apps.get_model('inventory', 'Brands').objects.all().values('id', 'name')
    data = list(brands)
    return JsonResponse({'data': data})

@login_required
@role_required('admin')
def add_brand(request):
    return add_item(request, 'inventory', 'Brands')

@login_required
@role_required('admin')
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

@login_required
@role_required('admin')
def delete_brand(request, pk):
    return delete_item(request, 'inventory', 'Brands', pk)

@login_required
@role_required('admin')
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

@login_required
@role_required('admin')
def supplier_data(request):
    suppliers = apps.get_model('inventory', 'Suppliers').objects.all().values('id', 'name', 'contact_person', 'contact_number', 'email', 'address')
    data = list(suppliers)
    return JsonResponse({'data': data})

@login_required
@role_required('admin')
def add_supplier(request):
    return add_item(request, 'inventory', 'Suppliers')

@login_required
@role_required('admin')
def edit_supplier(request, pk):
    return edit_item(request, 'inventory', 'Suppliers', pk)

@login_required
@role_required('admin')
def delete_supplier(request, pk):
    return delete_item(request, 'inventory', 'Suppliers', pk)

@login_required
@role_required('admin')
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

@login_required
@role_required('admin')
def add_branch(request):
    return add_item(request, 'inventory', 'Branches')

@login_required
@role_required('admin')
def edit_branch(request, pk):
    return edit_item(request, 'inventory', 'Branches', pk)

@login_required
@role_required('admin')
def delete_branch(request, pk):
    return delete_item(request, 'inventory', 'Branches', pk)

@login_required
@role_required('admin')
def branch_data(request):
    branches = apps.get_model('inventory', 'Branches').objects.all().values('id', 'name', 'location')
    data = list(branches)
    return JsonResponse({'data': data})

@login_required
@role_required('stock_manager', 'branch_manager')
def manage_stocks(request, branch_id=None, stock_id=None):
    # Support query param for branch_id as well
    incoming_branch_id = branch_id
    if incoming_branch_id is None:
        incoming_branch_id = request.GET.get('branch_id')
    try:
        branch_id = _resolve_branch_scope(request, incoming_branch_id)
    except PermissionDenied as e:
        return _json_or_forbidden(request, str(e))
    branch = None
    if branch_id:
        branch = get_object_or_404(Branches, pk=branch_id)
        stocks = StockLevel.objects.filter(branch=branch, is_active=True).select_related('product', 'product__brand')
        products = Products.objects.all().select_related('brand')
        branches_list = Branches.objects.filter(pk=branch_id)
    else:
        if _get_user_role(request) == 'branch_manager':
            branches_list = Branches.objects.filter(pk=branch_id) if branch_id else Branches.objects.none()
        else:
            branches_list = Branches.objects.all()
        stocks = StockLevel.objects.filter(is_active=True).select_related('product', 'product__brand')
        products = Products.objects.all().select_related('brand')

    if stock_id:
        stock = get_object_or_404(StockLevel, pk=stock_id, branch=branch, is_active=True) if branch else get_object_or_404(StockLevel, pk=stock_id, is_active=True)
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
@role_required('stock_manager', 'branch_manager')
def stock_history(request):
    branches_list = Branches.objects.all()
    products = Products.objects.all().select_related('brand')
    branch = None
    incoming_branch_id = request.GET.get('branch_id')
    try:
        resolved_branch_id = _resolve_branch_scope(request, incoming_branch_id)
    except PermissionDenied as e:
        return _json_or_forbidden(request, str(e))
    if resolved_branch_id:
        try:
            branch = Branches.objects.get(pk=int(resolved_branch_id))
        except (Branches.DoesNotExist, ValueError):
            branch = None
    if _get_user_role(request) == 'branch_manager':
        branches_list = Branches.objects.filter(pk=resolved_branch_id) if resolved_branch_id else Branches.objects.none()
    context = {
        'branch': branch,
        'branches': branches_list,
        'products': products,
    }
    return render(request, 'html/stock-history.html', context)

@login_required
def dashboard(request):
    role = _get_user_role(request)
    branch_param = request.GET.get('branch_id')
    category_param = request.GET.get('category_id')
    product_param = request.GET.get('product_id')

    try:
        resolved_branch_id = _resolve_branch_scope(request, branch_param)
    except PermissionDenied as e:
        return _json_or_forbidden(request, str(e))

    stock_qs = StockLevel.objects.filter(is_active=True).select_related('branch', 'product', 'product__brand', 'product__category')
    if resolved_branch_id:
        stock_qs = stock_qs.filter(branch__id=resolved_branch_id)

    if category_param:
        try:
            stock_qs = stock_qs.filter(product__category_id=int(category_param))
        except (TypeError, ValueError):
            pass

    if product_param:
        try:
            stock_qs = stock_qs.filter(product__id=int(product_param))
        except (TypeError, ValueError):
            pass

    branch_cards = []
    branch_rows = stock_qs.values('branch_id', 'branch__name').annotate(
        total_qty=models.Sum('quantity'),
        sku_count=models.Count('product', distinct=True),
        low_count=models.Count('id', filter=models.Q(quantity__lt=10))
    ).order_by('branch__name')
    for row in branch_rows:
        sku_count = row['sku_count'] or 0
        low_pct = 0
        if sku_count:
            low_pct = round((row['low_count'] or 0) * 100.0 / sku_count, 1)
        branch_cards.append({
            'id': row['branch_id'],
            'name': row['branch__name'],
            'total_qty': row['total_qty'] or 0,
            'sku_count': sku_count,
            'low_count': row['low_count'] or 0,
            'low_pct': low_pct,
            'low_items': [],
        })

    for row in branch_cards:
        items = stock_qs.filter(branch__id=row['id']).order_by('quantity', 'product__product_name')[:5]
        row['low_items'] = list(items.values('product__product_name', 'product__brand__name', 'quantity'))

    summary = {
        'stock_items': stock_qs.count(),
        'total_quantity': stock_qs.aggregate(total=models.Sum('quantity'))['total'] or 0,
        'low_stock': stock_qs.filter(quantity__lt=10).count(),
        'products': stock_qs.values('product_id').distinct().count(),
        'branches': branch_rows.count(),
    }

    # Filter options
    branch_choices = Branches.objects.all()
    if role == 'branch_manager':
        branch_choices = branch_choices.filter(pk=resolved_branch_id) if resolved_branch_id else Branches.objects.none()

    context = {
        'summary': summary,
        'branch_cards': branch_cards,
        'branches': branch_choices,
        'categories': Categories.objects.all(),
        'products': Products.objects.all(),
        'selected_branch': int(resolved_branch_id) if resolved_branch_id else None,
        'selected_category': int(category_param) if category_param and category_param.isdigit() else None,
        'selected_product': int(product_param) if product_param and product_param.isdigit() else None,
    }
    return render(request, 'html/dashboard.html', context)

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

@login_required
@role_required('stock_manager', 'branch_manager')
def movement_data(request):
    branch_id = request.GET.get('branch_id')
    product_id = request.GET.get('product_id')
    txn_type = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    qs = StockMovement.objects.select_related('branch', 'product', 'product__brand', 'handled_by').all()
    try:
        resolved_branch_id = _resolve_branch_scope(request, branch_id)
    except PermissionDenied as e:
        return _json_or_forbidden(request, str(e))
    if resolved_branch_id:
        qs = qs.filter(branch__id=resolved_branch_id)
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
@role_required('stock_manager', 'branch_manager')
def stock_data(request, branch_id=None):
    try:
        resolved_branch_id = _resolve_branch_scope(request, branch_id)
    except PermissionDenied as e:
        return _json_or_forbidden(request, str(e))
    qs = StockLevel.objects.filter(is_active=True)
    if resolved_branch_id:
        qs = qs.filter(branch__id=resolved_branch_id)
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
    stock_level, _ = StockLevel.objects.get_or_create(
        branch=branch,
        product=product,
        is_active=True,
        defaults={"quantity": 0}
    )
    if transaction_type == 'IN':
        stock_level.quantity = stock_level.quantity + quantity
    else:
        new_qty = stock_level.quantity - quantity
        if new_qty < 0:
            raise ValueError('Insufficient stock for this operation.')
        stock_level.quantity = new_qty
    stock_level.save()
    return stock_level

@login_required
@role_required('stock_manager', 'branch_manager')
def add_stock(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    branch_raw = request.POST.get('branch')
    product_raw = request.POST.get('product')
    try:
        branch_id = int(branch_raw) if branch_raw else None
        product_id = int(product_raw) if product_raw else None
        transaction_type = request.POST.get('transaction_type')
        quantity = int(request.POST.get('quantity') or 0)
        remarks = request.POST.get('remarks') or ''
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'message': 'Invalid input values.'}, status=400)

    try:
        branch_id = _resolve_branch_scope(request, branch_id)
    except PermissionDenied as e:
        return _json_or_forbidden(request, str(e))

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

@login_required
@role_required('stock_manager', 'branch_manager')
def edit_stock(request, pk):
    movement = get_object_or_404(StockMovement, pk=pk)
    if _get_user_role(request) == 'branch_manager':
        assigned = _get_assigned_branch_id(request)
        if not assigned or movement.branch_id != assigned:
            return _json_or_forbidden(request, 'You do not have permission to edit this movement.')
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    # Revert the old movement first
    revert_type = 'OUT' if movement.transaction_type == 'IN' else 'IN'
    try:
        _apply_movement_to_stocklevel(movement.branch, movement.product, revert_type, movement.quantity)
    except ValueError as e:
        return JsonResponse({'success': False, 'message': f'Failed to revert previous movement: {e}'}, status=400)

    # Apply new values
    branch_raw = request.POST.get('branch')
    product_raw = request.POST.get('product')
    try:
        branch_id = int(branch_raw) if branch_raw else None
        product_id = int(product_raw) if product_raw else None
        transaction_type = request.POST.get('transaction_type')
        quantity = int(request.POST.get('quantity') or 0)
        remarks = request.POST.get('remarks') or ''
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'message': 'Invalid input values.'}, status=400)

    try:
        branch_id = _resolve_branch_scope(request, branch_id)
    except PermissionDenied as e:
        return _json_or_forbidden(request, str(e))

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

@login_required
@role_required('stock_manager', 'branch_manager')
def delete_stock(request, pk):
    movement = get_object_or_404(StockMovement, pk=pk)
    if _get_user_role(request) == 'branch_manager':
        assigned = _get_assigned_branch_id(request)
        if not assigned or movement.branch_id != assigned:
            return _json_or_forbidden(request, 'You do not have permission to delete this movement.')
    # Revert the movement effect
    revert_type = 'OUT' if movement.transaction_type == 'IN' else 'IN'
    try:
        _apply_movement_to_stocklevel(movement.branch, movement.product, revert_type, movement.quantity)
    except ValueError as e:
        return JsonResponse({'success': False, 'message': f'Failed to revert movement: {e}'}, status=400)
    movement.delete()
    return JsonResponse({'success': True, 'message': 'Stock movement deleted successfully.'})

@login_required
@role_required('stock_manager', 'branch_manager')
def delete_stock_level(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    level = get_object_or_404(StockLevel, pk=pk, is_active=True)
    if _get_user_role(request) == 'branch_manager':
        assigned = _get_assigned_branch_id(request)
        if not assigned or level.branch_id != assigned:
            return _json_or_forbidden(request, 'You do not have permission to archive this stock level.')
    if not level.branch or not level.product:
        level.is_active = False
        level.archived_at = timezone.now()
        level.save(update_fields=['is_active', 'archived_at'])
        return JsonResponse({'success': True, 'message': 'Stock level archived (no branch/product; no balancing movement created).'})

    # Determine handler from session if available
    handled_by = None
    user_id = request.session.get('user_id')
    if user_id:
        try:
            handled_by = Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
            handled_by = None

    qty = level.quantity or 0
    try:
        if qty > 0:
            updated_level = _apply_movement_to_stocklevel(level.branch, level.product, 'OUT', qty)
            StockMovement.objects.create(
                transaction_id=_generate_transaction_id(),
                transaction_type='OUT',
                branch=level.branch,
                product=level.product,
                quantity=qty,
                remarks='Stock level archived',
                handled_by=handled_by,
                balance_after=updated_level.quantity
            )
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

    level.is_active = False
    level.archived_at = timezone.now()
    level.save(update_fields=['is_active', 'archived_at'])

    return JsonResponse({'success': True, 'message': 'Stock level archived successfully.'})


# Error handlers
def error_404(request, exception):
    return render(request, 'html/errors/404.html', status=404)


def error_500(request):
    return render(request, 'html/errors/500.html', status=500)


def error_403(request, exception=None):
    return render(request, 'html/errors/403.html', status=403)
