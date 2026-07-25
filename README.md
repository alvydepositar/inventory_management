# Inventory Management System

A branch-aware inventory application built with Django. The system manages product master data, per-branch stock, stock movements, inter-branch transfers, product mixing/conversion, users, alerts, and operational reports.

The frontend uses Bootstrap 5, jQuery, and DataTables. SQLite is configured by default for local development, with PostgreSQL support available through the included driver.

## Features

- Email or username authentication with password-reset support
- Role-based access for administrators, branch managers, and users
- Branch-scoped dashboards, inventory views, and reports
- Product, category, brand, supplier, and branch management
- Stock receiving (`IN`) and releasing (`OUT`)
- Atomic inter-branch transfers with linked outgoing and incoming records
- Stock mixing/conversion from one or more input products into an output product
- Low-stock limits and branch-level alerts
- Stock history with product, branch, transaction type, and date filters
- Current-stock summaries, daily sales, and transfer reports
- User profile and password management
- DataTables-based grids and report exports
- Custom HTML and JSON error responses

## Roles and Access

| Capability | Admin | Branch Manager | User |
| --- | :---: | :---: | :---: |
| View products and master data | Yes | Yes | Yes |
| Create or update products, categories, brands, and suppliers | Yes | Yes | No |
| Delete master data | Yes | No | No |
| Manage branches and users | Yes | No | No |
| View all branches | Yes | No | No |
| View assigned-branch stock and reports | Yes | Yes | Yes |
| Receive, release, transfer, and mix stock | Yes | Yes | Yes |
| Edit or delete existing stock movements | Yes | Yes | No |

Non-admin accounts must have an assigned branch before they can access stock, dashboard, or reporting modules. Their inventory queries and source-branch actions are restricted to that branch. Administrators can work across all branches.

## Tech Stack

- Python 3.10+
- Django 5.0.1
- SQLite by default; PostgreSQL driver included
- Bootstrap 5
- jQuery and DataTables
- Pillow

## Getting Started

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Apply database migrations

```bash
python manage.py migrate
```

Migration `0022_sync_users_to_django_auth` synchronizes existing application users with Django authentication. Current login and password-reset flows rely on this synchronization.

### 4. Create an administrator

For a Django superuser:

```bash
python manage.py createsuperuser
```

A Django staff member or superuser receives administrator access in the inventory application. Application users can also be created from **Manage Users**, where their profile, role, assigned branch, active state, and password are synchronized to Django auth.

### 5. Run the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and sign in with a username or email address.

## Configuration

Settings are defined in `inventory_management/settings.py`. On startup, the project loads environment values from `.env` in either the repository root or the `inventory_management/` directory. Existing process environment variables take precedence.

### Email and Password Reset

Without a remote `EMAIL_HOST`, password-reset messages are printed to the development console. To send mail through SMTP, create a local `.env` file:

```dotenv
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=inventory@example.com
EMAIL_HOST_PASSWORD=replace-with-an-app-password
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
DEFAULT_FROM_EMAIL=inventory@example.com
```

Optional override:

```dotenv
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

Do not commit `.env`; it is excluded by `.gitignore`.

### Database

Local development uses `db.sqlite3`. A PostgreSQL configuration example is present in `inventory_management/settings.py`, and `psycopg2-binary` is included in `requirements.txt`. Update the database settings and credentials before migrating if PostgreSQL is required.

The other SQLite files in the repository are not used by the default configuration.

## Inventory Workflows

### Receive and Release

The Manage Stocks page records positive quantities as:

- `IN`: adds stock to the selected branch
- `OUT`: removes stock and rejects the transaction if inventory is insufficient

Every movement stores a unique transaction ID, handler, timestamp, remarks, and before/after balances.

### Transfer Between Branches

A transfer is recorded atomically as two linked movements under one transaction group:

- `BLO`: backload/transfer out from the source branch
- `BLI`: backload/transfer in to the destination branch

The source and destination must differ, and the source must have sufficient inventory.

### Mix or Convert Stock

A conversion consumes one or more input products and adds a specified quantity of an output product in the same branch. The operation is atomic and records:

- `MIX_OUT` movements for consumed products
- A `MIX_IN` movement for the output product
- A conversion record linking the inputs, output, branch, handler, and remarks

Administrators and branch managers may create a new output product during conversion. Users must select an existing output product.

## Main Pages

| Page | Route |
| --- | --- |
| Login | `/` |
| Password reset | `/password-reset/` |
| Dashboard | `/dashboard/` |
| Manage stocks | `/manage-stocks/` |
| Stock history | `/stock-history/` |
| Low-stock alerts | `/low-stock-alerts/` |
| Summary reports | `/summary-reports/` |
| Daily sales report | `/daily-sales-report/` |
| All branches view | `/all-branches-view/` |
| Product catalogue | `/product-catalogue/` |
| Suppliers | `/suppliers/` |
| Branches | `/branches/` |
| Manage users | `/manage-users/` |
| Account | `/account/` |
| Django admin | `/admin/` |

Detailed JSON and mutation routes are defined in `inventory/urls.py`.

## Data Model

The core models in `inventory/models.py` are:

- `Users`: application profile, role, status, and optional branch assignment
- `Products`: product code, name, category, brand, supplier, price, and low-stock limit
- `Categories`, `Brands`, and `Suppliers`: reusable product reference data
- `Branches`: inventory locations
- `StockLevel`: active quantity for a product at a branch
- `StockMovement`: inventory history for stock actions, transfers, and mixing
- `StockConversion`: conversion header and output details
- `StockConversionInput`: products and quantities consumed by a conversion

`StockLevel.objects` returns active records. Use `StockLevel.all_objects` only when code explicitly needs inactive stock-level records.

## Project Structure

```text
inventory_management/
|-- manage.py
|-- requirements.txt
|-- inventory_management/     # Django settings, root URLs, auth backend, middleware
|-- inventory/                # Models, views, forms, services, access rules, tests
|   |-- migrations/
|   `-- templates/html/
|-- static/                   # Source CSS, JavaScript, images, and vendor assets
|-- staticfiles/              # collectstatic output
`-- docs/                     # User manuals and supporting documentation
```

Key implementation files:

- `inventory/access.py`: role and branch-scoping rules
- `inventory/auth_sync.py`: application-user to Django-auth synchronization
- `inventory/services.py`: transactional stock conversion service
- `inventory/views.py`: pages, DataTables feeds, and inventory actions
- `inventory_management/middleware.py`: global login enforcement and JSON `401` responses

## Testing and Validation

Run the automated tests:

```bash
python manage.py test
```

Run Django's configuration checks:

```bash
python manage.py check
```

The current automated suite focuses on stock conversions, including inventory updates, validation, rollback behavior, branch restrictions, and output-product creation.

## Production Checklist

The committed settings are development defaults. Before deployment:

1. Move `SECRET_KEY` and database credentials out of source control.
2. Set `DEBUG = False` and configure the deployment host in `ALLOWED_HOSTS`.
3. Configure HTTPS, SMTP, and a production database.
4. Run `python manage.py collectstatic`.
5. Run `python manage.py check --deploy` and review every warning.
6. Serve Django through a production WSGI or ASGI stack rather than `runserver`.

## Documentation

Additional end-user documentation is available in `docs/`, including `docs/User_Guide_and_Manual_PDF_Ready.md` and its PDF version.

## License

No license file is currently included. Treat the project as internal-use software unless the repository owner specifies otherwise.
