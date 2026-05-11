from django.db import models

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    user_role = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('user', 'User'), ('branch_manager', 'Branch Manager')], default='user')
    assigned_branch = models.ForeignKey('Branches', null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_users')
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Products(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=50, unique=True)
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey('Categories', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    brand = models.ForeignKey('Brands', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_stock_limit = models.PositiveIntegerField(default=10)
    supplier = models.ForeignKey('Suppliers', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

class Categories(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Suppliers(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Brands(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class Branches(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class ActiveStockLevelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class StockLevel(models.Model):
    id = models.AutoField(primary_key=True)
    branch = models.ForeignKey(Branches, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    objects = ActiveStockLevelManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = ('branch', 'product', 'is_active')
        indexes = [
            models.Index(fields=['branch']),
            models.Index(fields=['product']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        # Products has field `product_name`
        return f"{self.branch.name} - {self.product.product_name} = {self.quantity}"
    
    
class StockMovement(models.Model):
    TRANSACTION_CHOICES = (
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('BLO', 'Backload Out'),
        ('BLI', 'Backload In'),
        ('MIX_OUT', 'Mix Out'),
        ('MIX_IN', 'Mix In'),
    )
    id = models.AutoField(primary_key=True)
    transaction_id = models.CharField(max_length=20, unique=True)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_CHOICES)
    branch = models.ForeignKey(Branches, on_delete=models.SET_NULL, null=True, blank=True)
    related_branch = models.ForeignKey(
        Branches,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_stock_movements',
    )
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    remarks = models.TextField(blank=True)
    handled_by = models.ForeignKey(Users, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    transaction_group_id = models.CharField(max_length=20, null=True, blank=True)
    balance_before = models.PositiveIntegerField(null=True, blank=True)
    balance_after = models.PositiveIntegerField(null=True, blank=True)
    conversion = models.ForeignKey(
        'StockConversion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movements',
    )

    class Meta:
        indexes = [
            models.Index(fields=['branch']),
            models.Index(fields=['product']),
            models.Index(fields=['date']),
            models.Index(fields=['transaction_type']),
        ]

    def __str__(self):
        # Products has field `product_name`
        return f"{self.transaction_type} - {self.transaction_id} - {self.product.product_name}"


class StockConversion(models.Model):
    id = models.AutoField(primary_key=True)
    branch = models.ForeignKey(Branches, on_delete=models.SET_NULL, null=True, related_name='stock_conversions')
    output_product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True, related_name='stock_conversions_output')
    output_quantity = models.PositiveIntegerField()
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_conversions_created',
    )
    handled_by = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_conversions_handled',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['branch']),
            models.Index(fields=['output_product']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        output_name = self.output_product.product_name if self.output_product else 'Unknown Product'
        branch_name = self.branch.name if self.branch else 'Unknown Branch'
        return f"CONV-{self.id} - {output_name} @ {branch_name}"


class StockConversionInput(models.Model):
    id = models.AutoField(primary_key=True)
    conversion = models.ForeignKey(StockConversion, on_delete=models.CASCADE, related_name='inputs')
    input_product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True, related_name='stock_conversion_inputs')
    quantity_used = models.PositiveIntegerField()

    class Meta:
        unique_together = ('conversion', 'input_product')
        indexes = [
            models.Index(fields=['conversion']),
            models.Index(fields=['input_product']),
        ]

    def __str__(self):
        product_name = self.input_product.product_name if self.input_product else 'Unknown Product'
        return f"CONV-{self.conversion_id} - {product_name} ({self.quantity_used})"
