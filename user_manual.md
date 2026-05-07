# User Manual for Inventory Management System

## Introduction

### System Overview
This manual provides guidance for end users of the Inventory Management System, a web-based application built with Django for managing products, stock levels, and related operations in a retail environment.

### Purpose
The system helps track inventory across multiple branches, manage product catalogs, record stock movements, and generate reports for efficient inventory control.

### Prerequisites
- Access to the web application via a supported browser (Chrome, Firefox, Safari).
- Valid login credentials provided by the administrator.
- Basic computer skills for navigation and data entry.

## Getting Started

### Logging In
1. Open your web browser and navigate to the application URL.
2. Enter your username/email and password.
3. Click the "Login" button.
4. Upon successful login, you will be redirected to the dashboard or product catalog.

[Screenshot: Login Page]

### Navigation
The application uses a sidebar menu for navigation. Key sections include:
- Dashboard: Overview of system statistics.
- Product Catalogue: Manage products, categories, brands, and suppliers.
- Manage Stocks: View and update stock levels and movements.
- Manage Users: (Admin only) Add, edit, or delete users.
- Stock History: View transaction logs.
- Account: Update your profile and password.

[Screenshot: Sidebar Navigation]

### User Roles
- **Admin**: Full access to all features, including user management.
- **Branch Manager**: Access to stock management for assigned branches.
- **User**: Basic access to view and limited editing of inventory data.

## Core Modules

### Product Catalog
Manage the list of products available in the system.

#### Viewing Products
- Navigate to Product Catalogue.
- Use the search and filter options to find specific products.

[Screenshot: Product Catalogue Page]

#### Adding a Product
1. Click "Add Product" button.
2. Fill in details: Product ID, Name, Category, Brand, Supplier, Unit Price.
3. Save the product.

[Screenshot: Add Product Form]

#### Editing/Deleting Products
- Select a product from the list.
- Use edit or delete options in the modal.

### Stock Management
Track and update stock levels per branch.

#### Viewing Stock Levels
- Go to Manage Stocks.
- Filter by branch and product to see current quantities.

[Screenshot: Stock Levels Page]

#### Recording Stock Movements
1. Select a branch and product.
2. Choose movement type (IN or OUT).
3. Enter quantity and remarks.
4. Save to update stock and log the transaction.

[Screenshot: Stock Movement Form]

### User Management (Admin Only)
Manage system users.

#### Adding a User
1. Navigate to Manage Users.
2. Click "Add User".
3. Enter details: Username, Email, Role, etc.
4. Save the user.

[Screenshot: Add User Form]

### Reporting
View reports and history.

#### Dashboard
- Overview counts: Products, Categories, Branches, etc.
- Low stock alerts.

[Screenshot: Dashboard]

#### Stock History
- Filter transactions by branch, product, type, date.
- View detailed logs.

[Screenshot: Stock History Page]

## Workflows

### Adding a New Product
1. Log in as Admin or authorized user.
2. Navigate to Product Catalogue.
3. Click "Add Product".
4. Fill in all required fields.
5. Save and verify in the list.

### Managing Stock for a Branch
1. Go to Manage Stocks.
2. Select branch.
3. For each product, record IN/OUT movements as needed.
4. Check updated stock levels.

### Viewing Reports
1. Access Dashboard for summaries.
2. Use Stock History for detailed transaction views.
3. Export or print as needed.

## Troubleshooting

### Common Issues
- **Login Problems**: Ensure correct credentials; contact admin if locked out.
- **Data Not Saving**: Check required fields; refresh page if needed.
- **Slow Loading**: Clear browser cache or check internet connection.

### FAQs
- Q: How to reset password? A: Use the Account page or contact admin.
- Q: Can I edit stock without permission? A: Only authorized roles can modify stock.

## Appendices

### User Roles and Permissions
- Admin: All access.
- Branch Manager: Stock and branch-specific data.
- User: Read-only mostly.

### Glossary
- Stock Movement: IN (adding stock) or OUT (removing stock).
- Branch: Physical location for inventory.

### Contact Information
For support, contact the system administrator at [email] or [phone].