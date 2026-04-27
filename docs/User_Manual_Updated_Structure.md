# User Manual Updated Structure (Aligned to Current App)

This is a proposed replacement structure for the combined User Guide and User Manual.

## A. User Guide

### 1. Overview

- What the system does.
- Who should use it.
- Core inventory goals: accuracy, traceability, and branch visibility.

### 2. System Scope and Key Capabilities

- Product, category, brand, supplier, and branch maintenance.
- Stock actions: Receive, Release, Transfer to Branch.
- Branch and all-branches reporting.
- Exporting transaction and report data.

### 3. Roles and Responsibilities

- Administrator
- User
- Branch Manager

Include a simple access matrix for:

- Manage users
- Master data maintenance
- Stock actions
- Report viewing and export

### 4. Navigation Overview

Main menu groups:

- Dashboard
- Administrator
- Stocks
- Inventory Management
- Profile

## B. User Manual

### 1. Access and Authentication

1. Open the assigned URL.
2. Sign in using Email or Username and Password.
3. Optional: Remember Me.
4. Handle invalid credential message.
5. Log Out from Profile menu.

Routes:

- `/` (login)
- `/logout/`

### 2. Dashboard

What users see:

- Branches, Products, Tracked Stock, On Hand.
- Branches With Alerts and Low Stock Items.
- Per-branch low-stock preview and quick links.

Route:

- `/dashboard/`

### 3. Account Management

Procedures:

1. Update profile fields.
2. Save profile changes.
3. Change password.
4. Re-login after password update.

Routes:

- `/account/`
- `/account/update/`
- `/account/change-password/`

### 4. User Management (Admin)

Procedures:

1. View user list.
2. Add user.
3. Edit user.
4. Deactivate or delete user.

Route:

- `/manage-users/`

### 5. Inventory Master Data

#### 5.1 Product Catalog

- View products.
- Add new product.
- Edit product.

Route:

- `/product-catalogue/`

#### 5.2 Product Management

- Add/edit categories.
- Add/edit brands.

Route:

- `/product-details`

#### 5.3 Supplier Management

- Add/edit suppliers.

Route:

- `/suppliers/`

#### 5.4 Branch Management

- Add/edit/view/delete branches.
- Open branch stocks shortcut.

Route:

- `/branches/`

### 6. Stocks Workspace (Branch-Level)

Entry:

1. Open Stocks.
2. Choose a branch workspace.

Core tabs:

1. Stocks On Hand
2. Daily Sales
3. Branch Transfers
4. Low Stocks
5. Transaction Log

Procedures:

1. Receive stock.
2. Release stock.
3. Transfer stock to another branch.
4. Adjust stock from row actions.
5. Filter by product, action, and date range.
6. Open full Transaction Log tab.
7. Export table data (CSV, Excel, PDF, Copy).

Routes:

- `/manage-stocks/`
- `/manage-stocks/<branch_id>/`
- `/stock-history/` (redirect helper to transaction log view)

### 7. All Branches Workspace (Cross-Branch)

Core tabs:

1. Stocks on Hand
2. Daily Sales
3. Branch Transfers

Procedures:

1. Filter by branch, product, and date.
2. Review item summary.
3. Review totals by brand and category.
4. Export report tables.

Route:

- `/all-branches-view/`

### 8. Reports and Export Guide

Standard export formats:

- CSV
- Excel
- PDF
- Copy

Best practices:

1. Apply filters before export.
2. Verify date range before export.
3. Export from the view that already matches the intended report scope.

### 9. Data Field Glossary

Recommended definitions:

- Transaction ID
- Action
- Before
- Ending Balance
- Handled By
- Remarks
- Low Stock Limit

### 10. Troubleshooting

Suggested entries:

1. Invalid credentials.
2. Password change failed.
3. Missing records due to filters.
4. Export button not visible.
5. Cannot find branch workspace.

### 11. Appendix

- Route index (screen to URL map).
- Revision history.
- Contact and escalation path.

## C. Route Index (quick reference)

- Login: `/`
- Dashboard: `/dashboard/`
- Manage Users: `/manage-users/`
- Product Catalog: `/product-catalogue/`
- Product Management: `/product-details`
- Supplier Management: `/suppliers/`
- Branch Management: `/branches/`
- Stocks Workspace: `/manage-stocks/`
- Branch Stocks Workspace: `/manage-stocks/<branch_id>/`
- Transaction Log redirect: `/stock-history/`
- All Branches Workspace: `/all-branches-view/`
- Account: `/account/`

