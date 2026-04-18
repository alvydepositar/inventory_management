from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import ProductForm
from .models import *
from django.apps import apps
from django.forms import modelform_factory
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, time as dt_time
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum, Value
from django.db import transaction
from django.db.models.functions import Coalesce, TruncDate
from functools import wraps
from random import randint
from django.contrib.auth import authenticate, login as django_login, logout as django_logout, get_user_model
from django.contrib.auth.decorators import login_required

def login_view(request):
    from django.utils.http import url_has_allowed_host_and_scheme

    if request.user.is_authenticated:
        next_url = request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
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
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('dashboard')
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
        'id', 'product_id', 'product_name', 'category__name', 'category__id', 'brand__name', 'brand__id',
        'unit_price', 'low_stock_limit', 'supplier__name', 'supplier__id', 'created_at', 'updated_at'
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

def _branch_inventory_summary_queryset():
    active_stock_filter = Q(stocklevel__is_active=True)
    return Branches.objects.all().order_by('name').annotate(
        tracked_products_count=Count(
            'stocklevel',
            filter=active_stock_filter,
            distinct=True,
        ),
        low_stock_count=Count(
            'stocklevel',
            filter=active_stock_filter & Q(stocklevel__quantity__lte=F('stocklevel__product__low_stock_limit')),
            distinct=True,
        ),
        total_quantity=Coalesce(
            Sum('stocklevel__quantity', filter=active_stock_filter),
            Value(0),
        ),
    )

DASHBOARD_LOW_STOCK_PREVIEW_LIMIT = 5

def _attach_branch_low_stock_items(branches_list, preview_limit=None):
    branch_lookup = {branch.id: branch for branch in branches_list}
    for branch in branches_list:
        branch.low_stock_items = []
        branch.remaining_low_stock_items = 0

    low_stock_items = (
        StockLevel.objects.filter(
            is_active=True,
            branch__isnull=False,
            product__isnull=False,
            quantity__lte=F('product__low_stock_limit'),
        )
        .select_related('branch', 'product', 'product__brand')
        .order_by('branch__name', 'product__product_name')
    )

    for stock_item in low_stock_items:
        stock_item.short_by = max((stock_item.product.low_stock_limit or 0) - stock_item.quantity, 0)
        branch = branch_lookup.get(stock_item.branch_id)
        if branch is not None:
            branch.low_stock_items.append(stock_item)

    for branch in branches_list:
        branch.low_stock_items.sort(key=lambda stock_item: (-stock_item.short_by, stock_item.product.product_name.lower()))
        if preview_limit is not None:
            branch.remaining_low_stock_items = max(len(branch.low_stock_items) - preview_limit, 0)
            branch.low_stock_items = branch.low_stock_items[:preview_limit]

    return branches_list

def _attach_branch_sales_metrics(branches_list, day=None):
    if not branches_list:
        return branches_list

    for branch in branches_list:
        branch.daily_sales_quantity = 0
        branch.total_sales_quantity = 0
        branch.daily_sales_value = 0
        branch.total_sales_value = 0

    branch_ids = [branch.id for branch in branches_list if branch.id]
    if not branch_ids:
        return branches_list

    target_day = day or timezone.localdate()
    tz = timezone.get_current_timezone()
    day_start = timezone.make_aware(datetime.combine(target_day, dt_time.min), tz)
    day_end = timezone.make_aware(datetime.combine(target_day, dt_time.max), tz)

    value_expr = ExpressionWrapper(
        F('quantity') * F('product__unit_price'),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    zero_decimal = Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))

    sales_rows = StockMovement.objects.filter(
        transaction_type='OUT',
        branch_id__in=branch_ids,
    ).values('branch_id').annotate(
        daily_sales_quantity=Coalesce(
            Sum('quantity', filter=Q(date__gte=day_start, date__lte=day_end)),
            0,
        ),
        total_sales_quantity=Coalesce(Sum('quantity'), 0),
        daily_sales_value=Coalesce(
            Sum(value_expr, filter=Q(date__gte=day_start, date__lte=day_end)),
            zero_decimal,
        ),
        total_sales_value=Coalesce(Sum(value_expr), zero_decimal),
    )

    sales_lookup = {row['branch_id']: row for row in sales_rows}
    for branch in branches_list:
        row = sales_lookup.get(branch.id)
        if not row:
            continue
        branch.daily_sales_quantity = row.get('daily_sales_quantity') or 0
        branch.total_sales_quantity = row.get('total_sales_quantity') or 0
        branch.daily_sales_value = row.get('daily_sales_value') or 0
        branch.total_sales_value = row.get('total_sales_value') or 0

    return branches_list

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
    branches_list = list(_branch_inventory_summary_queryset())
    _attach_branch_sales_metrics(branches_list)
    branch_summary = None
    products = Products.objects.all().select_related('brand')
    if branch_id:
        branch = get_object_or_404(Branches, pk=branch_id)
        branch_summary = next((branch_item for branch_item in branches_list if branch_item.id == branch.id), None)
        stocks = StockLevel.objects.filter(branch=branch).select_related('product', 'product__brand')
    else:
        stocks = StockLevel.objects.none()

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

    selected_product_id = None
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            selected_product_id = int(product_id)
        except ValueError:
            selected_product_id = None

    context = {
        'branch': branch,
        'branches': branches_list,
        'stocks': stocks,
        'modal_title': modal_title,
        'form_action': form_action,
        'editing': editing,
        'stock': stock,
        'products': products,
        'selected_product_id': selected_product_id,
        'selected_txn_type': request.GET.get('type', '') if request.GET.get('type', '') in ['IN', 'OUT', 'BACKLOAD'] else '',
        'selected_date_from': request.GET.get('date_from', ''),
        'selected_date_to': request.GET.get('date_to', ''),
        'selected_txn_group_id': request.GET.get('group_id', ''),
        'stocks_section': request.GET.get('stocks_section', 'stocks-on-hand'),
        'selected_daily_date': request.GET.get('daily_date', timezone.localdate().isoformat()),
        'branch_daily_sales_quantity': getattr(branch_summary, 'daily_sales_quantity', 0),
        'branch_total_sales_quantity': getattr(branch_summary, 'total_sales_quantity', 0),
        'branch_daily_sales_value': getattr(branch_summary, 'daily_sales_value', 0),
        'branch_total_sales_value': getattr(branch_summary, 'total_sales_value', 0),
    }

    return render(request, 'html/manage-stocks.html', context)

@login_required
def stock_history(request):
    params = request.GET.copy()
    params['stocks_section'] = 'transaction-log'
    url = reverse('manage_stocks')
    query = params.urlencode()
    if query:
        url = f'{url}?{query}'
    if params.get('branch_id'):
        return redirect(f'{url}#stocks-transaction-log')
    return redirect(url)

@login_required
def low_stock_alerts(request):
    params = request.GET.copy()
    branch_id = params.get('branch_id')

    if branch_id:
        params['stocks_section'] = 'low-stock'
        url = reverse('manage_stocks')
        query = params.urlencode()
        if query:
            url = f'{url}?{query}'
        return redirect(f'{url}#stocks-low-stock')

    params.pop('stocks_section', None)
    url = reverse('manage_stocks')
    query = params.urlencode()
    if query:
        url = f'{url}?{query}'
    return redirect(url)

@login_required
def summary_reports(request):
    params = request.GET.copy()
    reports_section = params.get('reports_section', 'current-summary')
    branch_id = params.get('branch_id')

    if branch_id:
        section_map = {
            'current-summary': 'stocks-on-hand',
            'daily-stock-out': 'daily-sales',
            'transfers': 'branch-transfers',
        }
        stocks_section = section_map.get(reports_section, 'stocks-on-hand')
        params['stocks_section'] = stocks_section
        params.pop('reports_section', None)

        url = reverse('manage_stocks')
        query = params.urlencode()
        if query:
            url = f'{url}?{query}'

        anchor_map = {
            'stocks-on-hand': '#stocks-on-hand',
            'daily-sales': '#stocks-daily-sales',
            'branch-transfers': '#stocks-branch-transfers',
        }
        return redirect(f"{url}{anchor_map.get(stocks_section, '#stocks-on-hand')}")

    url = reverse('all_branches_view')
    query = params.urlencode()
    if query:
        url = f'{url}?{query}'
    return redirect(url)

@login_required
def all_branches_view(request):
    branches_list = Branches.objects.all().order_by('name')
    products = Products.objects.all().select_related('brand').order_by('product_name')
    selected_branch_id = request.GET.get('branch_id', '')
    today = timezone.localdate()
    tz = timezone.get_current_timezone()
    day_start = timezone.make_aware(datetime.combine(today, dt_time.min), tz)
    day_end = timezone.make_aware(datetime.combine(today, dt_time.max), tz)

    value_expr = ExpressionWrapper(
        F('quantity') * F('product__unit_price'),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    zero_decimal = Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
    sales_totals = StockMovement.objects.filter(transaction_type='OUT').aggregate(
        daily_sales_quantity=Coalesce(
            Sum('quantity', filter=Q(date__gte=day_start, date__lte=day_end)),
            0,
        ),
        total_sales_quantity=Coalesce(Sum('quantity'), 0),
        daily_sales_value=Coalesce(
            Sum(value_expr, filter=Q(date__gte=day_start, date__lte=day_end)),
            zero_decimal,
        ),
        total_sales_value=Coalesce(Sum(value_expr), zero_decimal),
    )

    return render(
        request,
        'html/summary-reports.html',
        {
            'branches': branches_list,
            'products': products,
            'selected_branch_id': selected_branch_id,
            'selected_product_id': request.GET.get('product_id', ''),
            'selected_date_from': request.GET.get('date_from', ''),
            'selected_date_to': request.GET.get('date_to', ''),
            'reports_section': request.GET.get('reports_section', 'current-summary'),
            'all_daily_sales_quantity': sales_totals.get('daily_sales_quantity') or 0,
            'all_total_sales_quantity': sales_totals.get('total_sales_quantity') or 0,
            'all_daily_sales_value': sales_totals.get('daily_sales_value') or 0,
            'all_total_sales_value': sales_totals.get('total_sales_value') or 0,
        },
    )

@login_required
def daily_sales_report(request):
    params = request.GET.copy()
    params['reports_section'] = 'daily-stock-out'
    url = reverse('all_branches_view')
    query = params.urlencode()
    if query:
        url = f'{url}?{query}'
    return redirect(url)

@login_required
def dashboard(request):
    active_stock_qs = StockLevel.objects.filter(is_active=True)
    low_stock_qs = active_stock_qs.filter(quantity__lte=F('product__low_stock_limit'))
    branches_list = list(_branch_inventory_summary_queryset())
    _attach_branch_low_stock_items(branches_list, preview_limit=DASHBOARD_LOW_STOCK_PREVIEW_LIMIT)
    counts = {
        'branches': len(branches_list),
        'products': Products.objects.count(),
        'stock_items': active_stock_qs.count(),
        'total_quantity': active_stock_qs.aggregate(total=Sum('quantity'))['total'] or 0,
        'branches_with_low_stock': sum(1 for branch in branches_list if branch.low_stock_count),
        'low_stock': low_stock_qs.count(),
    }
    return render(
        request,
        'html/dashboard.html',
        {
            'counts': counts,
            'branches': branches_list,
            'dashboard_low_stock_preview_limit': DASHBOARD_LOW_STOCK_PREVIEW_LIMIT,
        },
    )

def _parse_date_param(s, end=False):
    if not s:
        return None
    try:
        if len(s) == 10:
            d = datetime.fromisoformat(s)
            dt = datetime.combine(d.date(), dt_time.max if end else dt_time.min)
        else:
            dt = datetime.fromisoformat(s)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt
    except Exception:
        return None

def _is_incoming_transaction(transaction_type):
    return transaction_type in ['IN', 'BLI']

def _is_outgoing_transaction(transaction_type):
    return transaction_type in ['OUT', 'BLO']

def _display_transaction_matches_backload_filter(transaction_type):
    return transaction_type in ['BLO', 'BLI']

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
    transaction_group_id = request.GET.get('group_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    qs = StockMovement.objects.select_related('branch', 'related_branch', 'product', 'product__brand', 'handled_by').all()
    if transaction_group_id:
        qs = qs.filter(transaction_group_id=transaction_group_id)
    if branch_id:
        qs = qs.filter(branch__id=branch_id)
    if product_id:
        qs = qs.filter(product__id=product_id)
    if txn_type in ['IN', 'OUT', 'BLO', 'BLI']:
        qs = qs.filter(transaction_type=txn_type)
    elif txn_type == 'BACKLOAD':
        qs = qs.filter(transaction_type__in=['BLO', 'BLI'])
    dt_from = _parse_date_param(date_from, end=False)
    dt_to = _parse_date_param(date_to, end=True)
    if dt_from:
        qs = qs.filter(date__gte=dt_from)
    if dt_to:
        qs = qs.filter(date__lte=dt_to)

    data = list(qs.values(
        'id', 'transaction_id', 'transaction_type', 'quantity', 'remarks', 'balance_before', 'balance_after',
        'date',
        'branch__id', 'branch__name',
        'related_branch__id', 'related_branch__name',
        'transaction_group_id',
        'product__id', 'product__product_name', 'product__brand__name',
        'handled_by__id', 'handled_by__username'
    ))
    for row in data:
        if row['balance_before'] is None and row['balance_after'] is not None:
            if _is_incoming_transaction(row['transaction_type']):
                row['balance_before'] = max(row['balance_after'] - row['quantity'], 0)
            else:
                row['balance_before'] = row['balance_after'] + row['quantity']
        if row['balance_after'] is None and row['balance_before'] is not None:
            if _is_incoming_transaction(row['transaction_type']):
                row['balance_after'] = row['balance_before'] + row['quantity']
            else:
                row['balance_after'] = max(row['balance_before'] - row['quantity'], 0)
    return JsonResponse({'data': data})

@login_required
def summary_report_data(request):
    group_by = request.GET.get('group_by')
    branch_id = request.GET.get('branch_id')
    qs = StockLevel.objects.select_related('product', 'product__brand', 'product__category')
    if branch_id:
        try:
            qs = qs.filter(branch__id=int(branch_id))
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid branch filter.'}, status=400)

    value_expr = ExpressionWrapper(
        F('quantity') * F('product__unit_price'),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    zero_decimal = Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))

    if group_by == 'brand':
        data = list(
            qs.values('product__brand__id', 'product__brand__name')
            .annotate(
                item_count=Count('product', distinct=True),
                total_quantity=Coalesce(Sum('quantity'), 0),
                total_value=Coalesce(Sum(value_expr), zero_decimal),
            )
            .order_by('product__brand__name')
        )
        for row in data:
            row['group_id'] = row.pop('product__brand__id')
            row['group_name'] = row.pop('product__brand__name') or 'Unassigned'
        return JsonResponse({'data': data})

    if group_by == 'category':
        data = list(
            qs.values('product__category__id', 'product__category__name')
            .annotate(
                item_count=Count('product', distinct=True),
                total_quantity=Coalesce(Sum('quantity'), 0),
                total_value=Coalesce(Sum(value_expr), zero_decimal),
            )
            .order_by('product__category__name')
        )
        for row in data:
            row['group_id'] = row.pop('product__category__id')
            row['group_name'] = row.pop('product__category__name') or 'Unassigned'
        return JsonResponse({'data': data})

    if group_by == 'item':
        data = list(
            qs.values(
                'product__id',
                'product__product_id',
                'product__product_name',
                'product__brand__name',
                'product__category__name',
                'product__unit_price',
                'product__low_stock_limit',
            )
            .annotate(
                total_quantity=Coalesce(Sum('quantity'), 0),
                branch_count=Count('branch', distinct=True),
                total_value=Coalesce(Sum(value_expr), zero_decimal),
            )
            .order_by('product__product_name')
        )
        for row in data:
            low_stock_limit = row['product__low_stock_limit'] or 0
            medium_limit = low_stock_limit * 2
            if row['total_quantity'] <= low_stock_limit:
                stock_status = 'Low'
            elif row['total_quantity'] <= medium_limit:
                stock_status = 'Medium'
            else:
                stock_status = 'High'
            row['product_id'] = row.pop('product__id')
            row['product_code'] = row.pop('product__product_id')
            row['product_name'] = row.pop('product__product_name')
            row['brand_name'] = row.pop('product__brand__name') or 'Unassigned'
            row['category_name'] = row.pop('product__category__name') or 'Unassigned'
            row['unit_price'] = row.pop('product__unit_price')
            row['low_stock_limit'] = low_stock_limit
            row['stock_status'] = stock_status
        return JsonResponse({'data': data})

    return JsonResponse({'success': False, 'message': 'Invalid report group.'}, status=400)

@login_required
def daily_sales_data(request):
    branch_id = request.GET.get('branch_id')
    product_id = request.GET.get('product_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    qs = StockMovement.objects.select_related('branch', 'product', 'product__brand').filter(transaction_type='OUT')
    if branch_id:
        try:
            qs = qs.filter(branch__id=int(branch_id))
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid branch filter.'}, status=400)
    if product_id:
        try:
            qs = qs.filter(product__id=int(product_id))
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid product filter.'}, status=400)

    dt_from = _parse_date_param(date_from, end=False)
    dt_to = _parse_date_param(date_to, end=True)
    if dt_from:
        qs = qs.filter(date__gte=dt_from)
    if dt_to:
        qs = qs.filter(date__lte=dt_to)

    value_expr = ExpressionWrapper(
        F('quantity') * F('product__unit_price'),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    zero_decimal = Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))

    data = list(
        qs.annotate(sale_date=TruncDate('date'))
        .values(
            'sale_date',
            'branch__id',
            'branch__name',
            'product__id',
            'product__product_name',
            'product__brand__name',
        )
        .annotate(
            total_quantity=Coalesce(Sum('quantity'), 0),
            estimated_value=Coalesce(Sum(value_expr), zero_decimal),
        )
        .order_by('-sale_date', 'branch__name', 'product__product_name')
    )

    stock_map = {
        (row['branch_id'], row['product_id']): row['quantity']
        for row in StockLevel.objects.values('branch_id', 'product_id', 'quantity')
    }
    for row in data:
        branch_key = row['branch__id']
        product_key = row['product__id']
        row['current_balance'] = stock_map.get((branch_key, product_key), 0)
        row['branch_id'] = branch_key
        row['branch_name'] = row.pop('branch__name')
        row['product_id'] = product_key
        row['product_name'] = row.pop('product__product_name')
        row['brand_name'] = row.pop('product__brand__name') or 'Unassigned'
        row['sale_date'] = row['sale_date'].isoformat() if row['sale_date'] else ''
    return JsonResponse({'data': data})

@login_required
def transfer_report_data(request):
    branch_id = request.GET.get('branch_id')
    product_id = request.GET.get('product_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    qs = StockMovement.objects.select_related(
        'branch',
        'related_branch',
        'product',
        'product__brand',
        'handled_by',
    ).filter(transaction_type='BLO')

    if branch_id:
        try:
            branch_value = int(branch_id)
            qs = qs.filter(Q(branch__id=branch_value) | Q(related_branch__id=branch_value))
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid branch filter.'}, status=400)
    if product_id:
        try:
            qs = qs.filter(product__id=int(product_id))
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid product filter.'}, status=400)

    dt_from = _parse_date_param(date_from, end=False)
    dt_to = _parse_date_param(date_to, end=True)
    if dt_from:
        qs = qs.filter(date__gte=dt_from)
    if dt_to:
        qs = qs.filter(date__lte=dt_to)

    data = list(
        qs.values(
            'transaction_group_id',
            'date',
            'branch__id',
            'branch__name',
            'related_branch__id',
            'related_branch__name',
            'product__id',
            'product__product_name',
            'product__brand__name',
            'quantity',
            'handled_by__username',
            'remarks',
        ).order_by('-date', 'branch__name', 'product__product_name')
    )

    for row in data:
        transfer_date = row.pop('date')
        row['transfer_date'] = transfer_date.isoformat() if transfer_date else ''
        row['source_branch_id'] = row.pop('branch__id')
        row['source_branch_name'] = row.pop('branch__name') or ''
        row['destination_branch_id'] = row.pop('related_branch__id')
        row['destination_branch_name'] = row.pop('related_branch__name') or ''
        row['product_id'] = row.pop('product__id')
        row['product_name'] = row.pop('product__product_name') or ''
        row['brand_name'] = row.pop('product__brand__name') or 'Unassigned'
        row['handled_by_name'] = row.pop('handled_by__username') or ''

    return JsonResponse({'data': data})

@login_required
def stock_data(request, branch_id=None):
    qs = StockLevel.objects.all()
    if branch_id is None:
        q_branch_id = request.GET.get('branch_id')
        if q_branch_id:
            try:
                branch_id = int(q_branch_id)
            except ValueError:
                branch_id = None
    if branch_id:
        qs = qs.filter(branch__id=branch_id)
    # Optional filter by product id
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            qs = qs.filter(product__id=int(product_id))
        except ValueError:
            pass
    low_only = request.GET.get('low_only') in ['1', 'true', 'True']
    if low_only:
        qs = qs.filter(quantity__lte=F('product__low_stock_limit'))
    stocks = qs.values(
        'id', 'product__product_name', 'product__brand__name', 'product__low_stock_limit',
        'quantity', 'branch__id', 'product__id', 'product__brand__name',
        'product__brand__id', 'branch__name'
    )
    stock_levels = []
    for stock in stocks:
        low_stock_limit = stock['product__low_stock_limit'] or 0
        medium_limit = low_stock_limit * 2

        if stock['quantity'] <= low_stock_limit:
            stock['stock_level'] = 'Low'
        elif stock['quantity'] <= medium_limit:
            stock['stock_level'] = 'Medium'
        else:
            stock['stock_level'] = 'High'
        stock['short_by'] = max(low_stock_limit - stock['quantity'], 0)
        stock_levels.append(stock)
    data = list(stock_levels)
    return JsonResponse({'data': data})

def _generate_code(prefix: str, field_name: str = 'transaction_id') -> str:
    for _ in range(20):
        ts = timezone.now().strftime('%Y%m%d%H%M%S')
        suffix = f"{randint(0, 999):03d}"
        value = f"{prefix}{ts}{suffix}"
        lookup = {field_name: value}
        if not StockMovement.objects.filter(**lookup).exists():
            return value
    raise ValueError('Unable to generate a unique transaction reference.')

def _generate_transaction_id() -> str:
    return _generate_code('SM-')

def _generate_transaction_group_id() -> str:
    return _generate_code('BL-', field_name='transaction_group_id')

def _get_stock_quantity(branch, product):
    if not branch or not product:
        return 0
    return (
        StockLevel.objects.filter(branch=branch, product=product)
        .values_list('quantity', flat=True)
        .first()
        or 0
    )

def _apply_movement_to_stocklevel(branch, product, transaction_type, quantity):
    stock_level, _ = StockLevel.objects.get_or_create(branch=branch, product=product, defaults={"quantity": 0})
    if _is_incoming_transaction(transaction_type):
        stock_level.quantity = stock_level.quantity + quantity
    else:
        new_qty = stock_level.quantity - quantity
        if new_qty < 0:
            raise ValueError('Insufficient stock for this operation.')
        stock_level.quantity = new_qty
    stock_level.save()
    return stock_level

def _recalculate_movement_balances(branch, product):
    if not branch or not product:
        return

    movements = list(
        StockMovement.objects.filter(branch=branch, product=product).order_by('date', 'id')
    )
    running_balance = 0
    for movement in movements:
        movement.balance_before = running_balance
        if _is_incoming_transaction(movement.transaction_type):
            running_balance += movement.quantity
        else:
            running_balance = max(running_balance - movement.quantity, 0)
        movement.balance_after = running_balance

    if movements:
        StockMovement.objects.bulk_update(movements, ['balance_before', 'balance_after'])

def _build_backload_remarks(base_remarks, source_branch, destination_branch, direction):
    route_note = (
        f"Transfer to {destination_branch.name}"
        if direction == 'OUT'
        else f"Transfer from {source_branch.name}"
    )
    return f"{route_note}. {base_remarks}".strip() if base_remarks else route_note

def add_stock(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    try:
        branch_id = int(request.POST.get('branch')) if request.POST.get('branch') else None
        related_branch_id = int(request.POST.get('related_branch')) if request.POST.get('related_branch') else None
        product_id = int(request.POST.get('product')) if request.POST.get('product') else None
        transaction_type = request.POST.get('transaction_type')
        quantity = int(request.POST.get('quantity') or 0)
        remarks = request.POST.get('remarks') or ''
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'message': 'Invalid input values.'}, status=400)

    if not branch_id or not product_id or transaction_type not in ['IN', 'OUT', 'BACKLOAD'] or quantity <= 0:
        return JsonResponse({'success': False, 'message': 'Missing or invalid fields.'}, status=400)

    branch = get_object_or_404(Branches, pk=branch_id)
    product = get_object_or_404(Products, pk=product_id)
    related_branch = None
    if transaction_type == 'BACKLOAD':
        if not related_branch_id:
            return JsonResponse({'success': False, 'message': 'Destination branch is required for a transfer.'}, status=400)
        if related_branch_id == branch_id:
            return JsonResponse({'success': False, 'message': 'Destination branch must be different from the source branch.'}, status=400)
        related_branch = get_object_or_404(Branches, pk=related_branch_id)

    # Determine handler from session if available
    handled_by = None
    user_id = request.session.get('user_id')
    if user_id:
        try:
            handled_by = Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
            handled_by = None

    try:
        with transaction.atomic():
            if transaction_type == 'BACKLOAD':
                group_id = _generate_transaction_group_id()
                source_balance_before = _get_stock_quantity(branch, product)
                source_level = _apply_movement_to_stocklevel(branch, product, 'OUT', quantity)
                destination_balance_before = _get_stock_quantity(related_branch, product)
                destination_level = _apply_movement_to_stocklevel(related_branch, product, 'IN', quantity)

                StockMovement.objects.create(
                    transaction_id=_generate_transaction_id(),
                    transaction_type='BLO',
                    transaction_group_id=group_id,
                    branch=branch,
                    related_branch=related_branch,
                    product=product,
                    quantity=quantity,
                    remarks=_build_backload_remarks(remarks, branch, related_branch, 'OUT'),
                    handled_by=handled_by,
                    balance_before=source_balance_before,
                    balance_after=source_level.quantity
                )
                StockMovement.objects.create(
                    transaction_id=_generate_transaction_id(),
                    transaction_type='BLI',
                    transaction_group_id=group_id,
                    branch=related_branch,
                    related_branch=branch,
                    product=product,
                    quantity=quantity,
                    remarks=_build_backload_remarks(remarks, branch, related_branch, 'IN'),
                    handled_by=handled_by,
                    balance_before=destination_balance_before,
                    balance_after=destination_level.quantity
                )
                _recalculate_movement_balances(branch, product)
                _recalculate_movement_balances(related_branch, product)
            else:
                balance_before = _get_stock_quantity(branch, product)
                level = _apply_movement_to_stocklevel(branch, product, transaction_type, quantity)
                StockMovement.objects.create(
                    transaction_id=_generate_transaction_id(),
                    transaction_type=transaction_type,
                    branch=branch,
                    product=product,
                    quantity=quantity,
                    remarks=remarks,
                    handled_by=handled_by,
                    balance_before=balance_before,
                    balance_after=level.quantity
                )
                _recalculate_movement_balances(branch, product)
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

    if transaction_type == 'BACKLOAD':
        return JsonResponse({'success': True, 'message': 'Transfer recorded successfully.'})
    return JsonResponse({'success': True, 'message': 'Stock action recorded successfully.'})

def edit_stock(request, pk):
    movement = get_object_or_404(StockMovement, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)
    if movement.transaction_group_id or movement.transaction_type in ['BLO', 'BLI']:
        return JsonResponse(
            {'success': False, 'message': 'Editing transfer transactions is not supported. Delete and recreate the transfer instead.'},
            status=400
        )

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
    old_branch = movement.branch
    old_product = movement.product
    revert_type = 'OUT' if _is_incoming_transaction(movement.transaction_type) else 'IN'

    try:
        with transaction.atomic():
            _apply_movement_to_stocklevel(old_branch, old_product, revert_type, movement.quantity)
            balance_before = _get_stock_quantity(branch, product)
            level = _apply_movement_to_stocklevel(branch, product, transaction_type, quantity)

            movement.transaction_type = transaction_type
            movement.branch = branch
            movement.product = product
            movement.quantity = quantity
            movement.remarks = remarks
            movement.balance_before = balance_before
            movement.balance_after = level.quantity
            movement.save()

            affected_pairs = {
                (old_branch.id, old_product.id) if old_branch and old_product else None,
                (branch.id, product.id),
            }
            for pair in affected_pairs:
                if not pair:
                    continue
                recalc_branch = old_branch if old_branch and old_branch.id == pair[0] else branch
                recalc_product = old_product if old_product and old_product.id == pair[1] else product
                _recalculate_movement_balances(recalc_branch, recalc_product)
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

    return JsonResponse({'success': True, 'message': 'Stock movement updated successfully.'})

def delete_stock(request, pk):
    movement = get_object_or_404(StockMovement, pk=pk)
    branch = movement.branch
    product = movement.product
    revert_type = 'OUT' if _is_incoming_transaction(movement.transaction_type) else 'IN'
    try:
        with transaction.atomic():
            if movement.transaction_group_id:
                grouped_movements = list(
                    StockMovement.objects.filter(transaction_group_id=movement.transaction_group_id).select_related('branch', 'product')
                )
                touched_pairs = set()
                for grouped_movement in grouped_movements:
                    grouped_revert_type = 'OUT' if _is_incoming_transaction(grouped_movement.transaction_type) else 'IN'
                    _apply_movement_to_stocklevel(
                        grouped_movement.branch,
                        grouped_movement.product,
                        grouped_revert_type,
                        grouped_movement.quantity
                    )
                    if grouped_movement.branch and grouped_movement.product:
                        touched_pairs.add((grouped_movement.branch.id, grouped_movement.product.id))
                StockMovement.objects.filter(transaction_group_id=movement.transaction_group_id).delete()
                for branch_id, product_id in touched_pairs:
                    recalc_branch = Branches.objects.get(pk=branch_id)
                    recalc_product = Products.objects.get(pk=product_id)
                    _recalculate_movement_balances(recalc_branch, recalc_product)
                return JsonResponse({'success': True, 'message': 'Transfer deleted successfully.'})

            _apply_movement_to_stocklevel(branch, product, revert_type, movement.quantity)
            movement.delete()
            _recalculate_movement_balances(branch, product)
    except ValueError as e:
        return JsonResponse({'success': False, 'message': f'Failed to revert movement: {e}'}, status=400)
    return JsonResponse({'success': True, 'message': 'Stock action deleted successfully.'})
