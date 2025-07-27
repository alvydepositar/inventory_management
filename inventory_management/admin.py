from django.contrib import admin
from inventory.models import Products, Categories, Suppliers, Brands
from django.utils.html import format_html

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_id', 'product_name', 'category', 'brand', 'unit_price', 'supplier')
    search_fields = ('product_id', 'product_name', 'category', 'brand')  # Optional: Add search functionality
    list_filter = ('category', 'brand')  # Optional: Add filters for better admin usability
    
admin.site.site_header = "Inventory Management Admin"
admin.site.site_title = "Inventory Management Admin Portal"
admin.site.index_title = "Welcome to the Inventory Management Admin Portal"

# Register your models here.
admin.site.register(Products, ProductAdmin)
admin.site.register(Categories)
admin.site.register(Suppliers)
admin.site.register(Brands)
