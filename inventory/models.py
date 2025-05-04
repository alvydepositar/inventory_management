from django.db import models

class Product(models.Model):
    product_id = models.CharField(max_length=50, unique=True)
    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=255)

    def __str__(self):
        return self.product_name
