from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='auth_login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('manage-users/', views.manage_users, name='manage_users'),
    path('users-data/', views.user_data, name='user_data'),
    path('add-user/', views.add_user, name='add_user'),
    path('edit-user/<int:pk>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:pk>/', views.delete_user, name='delete_user'),

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

    path('suppliers/', views.suppliers, name='suppliers'),
    
    path('supplier-data/', views.supplier_data, name='supplier_data'),
    path('add-supplier/', views.add_supplier, name='add_supplier'),
    path('edit-supplier/<int:pk>/', views.edit_supplier, name='edit_supplier'),
    path('delete-supplier/<int:pk>/', views.delete_supplier, name='delete_supplier'),
    
    path('branches/', views.branches, name='branches'),
    
    path('branch-data/', views.branch_data, name='branch_data'),
    path('add-branch/', views.add_branch, name='add_branch'),
    path('edit-branch/<int:pk>/', views.edit_branch, name='edit_branch'),
    path('delete-branch/<int:pk>/', views.delete_branch, name='delete_branch'),
    
    path('manage-stocks/', views.manage_stocks, name='manage_stocks'),
    path('manage-stocks/<int:branch_id>/', views.manage_stocks, name='manage_stocks'),
    
    path('stock-data/', views.stock_data, name='stock_data_all'),
    path('stock-data/<int:branch_id>/', views.stock_data, name='stock_data'),
    path('movement-data/', views.movement_data, name='movement_data'),
    path('summary-report-data/', views.summary_report_data, name='summary_report_data'),
    path('daily-sales-data/', views.daily_sales_data, name='daily_sales_data'),
    path('transfer-report-data/', views.transfer_report_data, name='transfer_report_data'),
    path('add-stock/', views.add_stock, name='add_stock'),
    path('edit-stock/<int:pk>/', views.edit_stock, name='edit_stock'),
    path('delete-stock/<int:pk>/', views.delete_stock, name='delete_stock'),

    # New pages
    path('low-stock-alerts/', views.low_stock_alerts, name='low_stock_alerts'),
    path('summary-reports/', views.summary_reports, name='summary_reports'),
    path('daily-sales-report/', views.daily_sales_report, name='daily_sales_report'),
    path('stock-history/', views.stock_history, name='stock_history'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('account/', views.account, name='account'),
    path('account/update/', views.account_update, name='account_update'),
    path('account/change-password/', views.account_change_password, name='account_change_password'),

]
