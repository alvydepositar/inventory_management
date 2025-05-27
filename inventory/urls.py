from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.auth_login, name='auth_login'),
    
    path('manage-users/', views.manage_users, name='manage_users'),
    
    path('product-catalogue/', views.product_catalogue, name='product_catalogue'),
    
    path('product-data/', views.product_data, name='product_data'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    
    path('add-item/<str:app_label>/<str:model_name>/', views.add_item, name='add_item'),
    path('edit-item/<str:app_label>/<str:model_name>/<int:item_id>/', views.edit_item, name='edit_item'),

]