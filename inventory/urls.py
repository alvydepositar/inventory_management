from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.auth_login, name='auth_login'),
    
    path('manage-users/', views.manage_users, name='manage_users'),
    
    path('product-catalogue/', views.product_catalogue, name='product_catalogue'),
    
    path('product-data/', views.product_data, name='product_data'),
    path('add-product/', views.add_product, name='add_product'),

]