from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.auth_login, name='auth_login'),
    
    path('manage-users/', views.manage_users, name='manage_users'),

    path('add-item/<str:app_label>/<str:model_name>/', views.add_item, name='add_item'),
    path('edit-item/<str:app_label>/<str:model_name>/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete-item/<str:app_label>/<str:model_name>/<int:item_id>/', views.delete_item, name='delete_item'),
    
    path('product-catalogue/', views.product_catalogue, name='product_catalogue'),
    
    path('product-data/', views.product_data, name='product_data'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    
    path('product-details', views.product_details, name='product_details'),

    path('category-data/', views.category_data, name='category_data'),
    path('add-category/', views.add_category, name='add_category'),
    path('edit-category/<int:pk>/', views.edit_category, name='edit_category'),
    path('delete-category/<int:pk>/', views.delete_category, name='delete_category'),

    path('brand-data/', views.brand_data, name='brand_data'),
    path('add-brand/', views.add_brand, name='add_brand'),
    path('edit-brand/<int:pk>/', views.edit_brand, name='edit_brand'),
    path('delete-brand/<int:pk>/', views.delete_brand, name='delete_brand'),
    
    path('supplier-data/', views.supplier_data, name='supplier_data'),
    path('add-supplier/', views.add_supplier, name='add_supplier'),
    path('edit-supplier/<int:pk>/', views.edit_supplier, name='edit_supplier'),
    path('delete-supplier/<int:pk>/', views.delete_supplier, name='delete_supplier'),

]