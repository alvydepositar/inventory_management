# Inventory Management (Django)

Inventory Management is a Django-based web application for managing products, categories, brands, suppliers, branches, stock levels and movements, and a simple user management UI. It uses Bootstrap 5 and DataTables on the frontend and ships with SQLite by default (optional PostgreSQL config included).

This project appears tailored for a paint center (branding in the auth page), but it is generic enough to support typical retail inventory workflows.

## Features

- Product catalog with add/edit/delete and DataTables integration
- Categories, Brands, Suppliers CRUD
- Branches and per-branch stock levels
- Stock movements (IN/OUT) with handler attribution
- Simple user management UI with roles: `admin`, `stock_manager`, `branch_manager`
- Responsive UI using Bootstrap 5; interactive grids using DataTables

## Feature Overview

- **Authentication & RBAC**: Login with username/email; role-based access (admin, stock manager, branch manager). Branch managers are auto-scoped to their assigned branch.
- **Dashboard**: Branch-level stock cards (totals, SKU count, low-stock %), top low-stock items per branch, and filters for branch/category/product.
- **Users**: Admins can create/edit/delete users, set roles, active status, and assign branches (for branch managers); passwords are hashed and synced to Django auth.
- **Products & Masters**: Admin-only management for products, categories, brands, suppliers, and branches via DataTables with CRUD modals.
- **Stock Management**: Branch/product filters with adjustable column actions; record IN/OUT movements; soft-delete (archive) stock levels with balancing movement; branch managers limited to their branch.
- **Stock History**: Paginated/history DataTable with filters (branch, product, type, date range); respects branch scoping for branch managers.
- **Reporting/Exports**: DataTables export buttons (CSV/Excel/PDF/Copy) on user and product grids; stock tables can be filtered and adjusted inline.
- **Error Handling**: Custom 403/404/500 pages; forbidden access renders the 403 page; AJAX requests receive JSON errors.

## System User Guide

### Roles at a glance
- **Admin**: Full control (users, master data, branches, stocks, movements, dashboard).
- **Stock Manager**: Daily inventory operations across branches (stocks, movements, dashboard, history).
- **Branch Manager**: Same as Stock Manager but limited to their assigned branch (filters and queries are auto-scoped).

### Signing in
1. Go to `/`.
2. Enter username or email and password.
3. If already signed in, you’ll be redirected to the Dashboard.

### Dashboard
- Use the filters (branch/category/product) to scope data.
- Review branch cards (totals, SKUs, low-stock %). Click “Open branch stocks” to jump to Manage Stocks pre-filtered.
- See low-stock items per branch (top 5 by lowest quantity).

### Managing users (Admin only)
1. Navigate to `Manage Users`.
2. Add/Edit:
   - Set role (admin/stock_manager/branch_manager).
   - For branch managers, assign a branch.
   - Set Active to allow login; set a password (hashed/synced to Django auth).
3. Delete removes the app user record.

### Master data (Admin only)
- Products, Categories, Brands, Suppliers, Branches: Each page uses a DataTable with add/edit/delete modals. Exports available on some tables (CSV/Excel/PDF/Copy).

### Stock management (Stock/Branch managers; Admin)
- Filters: Branch and Product selectors (scrollable). Clear to reset.
- Actions:
  - **Adjust**: Opens modal to record IN/OUT movement.
  - **Delete**: Archives the stock level (soft delete); if quantity > 0 a balancing OUT movement is created.
- Branch managers can only see/act on their assigned branch.

### Stock history
- Filters: branch, product, type, date range.
- Shows movement log (IN/OUT, qty, balance after, remarks).
- Branch managers see only their branch.

### Error handling
- Forbidden access shows the custom 403 page (JSON 403 for AJAX).
- Missing pages show 404; server errors show 500 with a dashboard link.

### Exports
- User and product tables include export buttons (CSV/Excel/PDF/Copy). Filters apply to exports.

### Passwords
- User passwords entered in Manage Users are hashed and synced to Django auth. Use Manage Users to reset passwords; ensure the user is Active.

## Tech Stack

- Backend: Django 5.x
- Database: SQLite (default), PostgreSQL (optional)
- Frontend: Bootstrap 5, jQuery, DataTables

## Project Structure

- `manage.py`: Django management entrypoint
- `inventory_management/`: Django project configuration (settings, URLs, WSGI/ASGI)
- `inventory/`: Core app (models, views, forms, URLs, templates)
  - Models: `Users`, `Products`, `Categories`, `Brands`, `Suppliers`, `Branches`, `StockLevel`, `StockMovement` (see `inventory/models.py:1`)
  - Views: CRUD pages + JSON endpoints for DataTables (see `inventory/views.py:1`)
  - Forms: ModelForms for Products, Categories, Brands, Suppliers, Branches, Stock (see `inventory/forms.py:1`)
  - URLs: App routes (see `inventory/urls.py:1`)
  - Templates: UI pages (see `inventory/templates/html/base.html:1`, `inventory/templates/html/product-catalogue.html:1`, `inventory/templates/html/manage-users.html:1`, etc.)
- `static/`: Vendor assets, JS, CSS used by the UI (see `static/assets/js/tables.js:1`)

## Getting Started

Prerequisites:

- Python 3.10+ (3.12 OK)
- pip and venv (or your preferred environment manager)

Setup:

1. Create and activate a virtual environment
   - Windows (PowerShell):
     - `python -m venv .venv`
     - `.\\.venv\\Scripts\\Activate.ps1`
   - macOS/Linux:
     - `python3 -m venv .venv`
     - `source .venv/bin/activate`
2. Install dependencies
   - `pip install -r requirements.txt`
3. Apply migrations
   - `python manage.py migrate`
4. (Optional) Create a superuser for Django admin
   - `python manage.py createsuperuser`
5. Run the development server
   - `python manage.py runserver`

App entry is routed through the inventory app URLs (`inventory_management/urls.py:1`). With the dev server running, open:

- Login page: `http://127.0.0.1:8000/`
- Products: `http://127.0.0.1:8000/product-catalogue/`
- Users: `http://127.0.0.1:8000/manage-users/`
- Suppliers: `http://127.0.0.1:8000/suppliers/`
- Branches: `http://127.0.0.1:8000/branches/`
- Stocks (all branches): `http://127.0.0.1:8000/manage-stocks/`

Note: Authentication on the login page is not wired to Django’s auth system yet; it is currently a UI shell.

## Configuration

The project defaults to SQLite (`inventory_management/settings.py:1`). A commented PostgreSQL configuration is included for convenience:

- `ENGINE`: `django.db.backends.postgresql`
- `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT`

For production, you should:

- Move `SECRET_KEY` and DB credentials to environment variables
- Set `DEBUG = False`
- Set `ALLOWED_HOSTS`
- Configure static files collection (`python manage.py collectstatic`) and a production web server

## Key URLs and Endpoints

UI routes (HTML pages):

- Login: `''` → `views.auth_login`
- Manage Users: `'manage-users/'` → `views.manage_users`
- Product Catalogue: `'product-catalogue/'` → `views.product_catalogue`
- Suppliers: `'suppliers/'` → `views.suppliers`
- Branches: `'branches/'` → `views.branches`
- Manage Stocks: `'manage-stocks/'` and `'manage-stocks/<int:branch_id>/'` → `views.manage_stocks`

JSON endpoints (DataTables):

- Users: `'users-data/'` → `views.user_data` (see `inventory/views.py:1`)
- Products: `'product-data/'` → `views.product_data`
- Categories: `'category-data/'` → `views.category_data`
- Brands: `'brand-data/'` → `views.brand_data`
- Suppliers: `'supplier-data/'` → `views.supplier_data`
- Stocks: `'stock-data/'` and `'stock-data/<int:branch_id>/'` → `views.stock_data`

Generic CRUD helpers:

- Add: `'add-item/<str:app_label>/<str:model_name>/'` → `views.add_item`
- Edit: `'edit-item/<str:app_label>/<str:model_name>/<int:item_id>/'` → `views.edit_item`
- Delete: `'delete-item/<str:app_label>/<str:model_name>/<int:item_id>/'` → `views.delete_item`

Product-specific CRUD (used by the UI):

- Add: `'add-product/'` → `views.add_product`
- Edit: `'edit-product/<int:pk>/'` → `views.edit_product`
- Delete: `'delete-product/<int:pk>/'` → `views.delete_product`

See full routing in `inventory/urls.py:1`.

## Data Model

Defined in `inventory/models.py:1`:

- `Users`: Simple app-specific user with `username`, `email`, `password` (string), `first_name`, `last_name`, `user_role`, `is_active`.
- `Products`: `product_id`, `product_name`, foreign keys to `Categories`, `Brands`, `Suppliers`, and `unit_price`.
- `Categories`, `Brands`, `Suppliers`: Basic reference data with timestamps.
- `Branches`: Store/branch where stock is held.
- `StockLevel`: Unique per (`branch`, `product`), tracks `quantity`.
- `StockMovement`: Transaction log with `IN`/`OUT`, quantity, handler, and remarks.

## Frontend

- Base layout and assets: `inventory/templates/html/base.html:1`
- DataTables behavior: `static/assets/js/tables.js:1` implements tables and modals for Users, Products, etc.
- Pages: `inventory/templates/html/*.html` (e.g., `product-catalogue.html:1`, `manage-users.html:1`, `suppliers.html:1`, `branches.html:1`, `manage-stocks.html:1`)

## Roles and Permissions

- `admin`: Full control over all data and pages (users, master data, branches, stocks, movements, dashboard).
- `stock_manager`: Manages daily inventory operations across branches (view/manage stocks, record IN/OUT, view dashboard/history). No access to user or master-data management.
- `branch_manager`: Same as stock manager but scoped to their assigned branch (enforced in stock, movement, and dashboard views). No access to user or master-data management.

## Development Notes

- Admin site is available at `/admin/` once a superuser is created.
- The app currently uses a separate `Users` model not integrated with Django authentication. For real authentication/authorization, prefer Django’s `User` or a custom `AUTH_USER_MODEL`.
- `tables.js` uses DataTables with server-sourced JSON from the endpoints above. Ensure the server is running and CSRF tokens are available for POST/DELETE actions.

## Known Issues and Caveats

- Security: `inventory/models.py:1` defines a plain-text `password` field on `Users`. Do not use this for real auth. Use Django auth with hashed passwords instead.
- Settings: `SECRET_KEY` and `DEBUG=True` are committed for development only. Externalize secrets for production.
- Minor bugs to review:
  - `StockLevel.__str__` references `self.product.name` but the model field is `product_name` on `Products` (see `inventory/models.py:1`).
  - `manage_stocks` view uses `branch` when assembling the edit case, but the variable set earlier is `branches` (see `inventory/views.py:1`).
  - DELETE requests from JS may need CSRF handling or method overrides if blocked by middleware.

## Scripts and Commands

- Run dev server: `python manage.py runserver`
- Apply migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`

## Contributing

- Keep code consistent with Django conventions used in this repo.
- Prefer ModelForms for validation and server-side checks.
- When adding models, wire up:
  - Model in `inventory/models.py`
  - Admin registration in `inventory/admin.py`
  - Optional forms in `inventory/forms.py`
  - CRUD endpoints and JSON feeds in `inventory/views.py` + routes in `inventory/urls.py`
  - A DataTables- backed page template in `inventory/templates/html/`

## License

This project is provided as-is for demonstration and internal use. No explicit license is included.
