# User Manual for Inventory Management System

## 1. Introduction

### 1.1 Purpose of the User Manual
This user manual serves as a comprehensive guide for users of the Inventory Management System, a Django-based web application designed to streamline inventory operations in retail environments. It provides detailed instructions on system navigation, core functionalities, and best practices to ensure effective utilization of the platform. The manual is intended to facilitate user onboarding, promote operational efficiency, and minimize errors in inventory management tasks.

### 1.2 Intended Users
The system is designed for a diverse range of users within retail organizations, including:

- **Administrators**: Individuals responsible for system configuration, user management, and oversight of all inventory operations. They require full access to all features for maintaining system integrity and generating comprehensive reports.
- **Branch Managers**: Personnel overseeing specific store locations who need to monitor and update stock levels, record stock movements, and manage branch-specific inventory data.
- **Standard Users**: General staff members who view product catalogs, check stock levels, and perform limited editing tasks under role-based permissions.

All users should possess basic computer literacy, including web browser navigation and form completion skills. Access is granted via role-based authentication, ensuring secure and appropriate feature exposure.

### 1.3 Scope of the System
The Inventory Management System encompasses a complete suite of tools for managing retail inventory across multiple branches. Key functionalities include:

- Product catalog management with support for categories, brands, and suppliers.
- Branch-specific stock level tracking and real-time quantity monitoring.
- Stock movement logging for inbound (IN) and outbound (OUT) transactions, including transaction attribution and remarks.
- User management with role-based access control (Admin, Branch Manager, User).
- Responsive web interface with interactive data tables for efficient data visualization and manipulation.
- Dashboard analytics providing overview statistics and low-stock alerts.

The system supports both SQLite (default) and PostgreSQL databases, making it adaptable for small-scale operations or enterprise deployments. It excludes advanced features such as financial reporting, automated procurement, or integration with external ERP systems, focusing instead on core inventory tracking and control.

### 1.4 Document Organization
This manual is structured to provide a logical progression from foundational concepts to detailed operational procedures:

- **Introduction and System Overview**: Provides context, purpose, and high-level system capabilities.
- **Getting Started**: Covers login procedures, interface navigation, and user role definitions.
- **Core Modules**: Detailed guides for product management, stock operations, user administration, and reporting.
- **Troubleshooting and Support**: Addresses common issues, known limitations, and maintenance procedures.
- **Appendices**: Includes technical specifications, glossary, and reference materials.

Each section includes screenshots, step-by-step instructions, and annotations to enhance usability. The document assumes familiarity with web-based applications and prioritizes clarity for non-technical users.

## 2. System Overview

### 2.1 System Description
The Inventory Management System is a web-based application built on the Django framework (version 5.x), utilizing a relational database for data persistence. The frontend employs Bootstrap 5 for responsive design and DataTables for interactive, server-sourced data grids that support searching, filtering, and pagination. Key architectural components include:

- **Backend**: Django views handle HTTP requests, model forms manage data validation, and JSON endpoints power dynamic UI updates. Authentication integrates Django's built-in auth system with a legacy custom Users model for backward compatibility.
- **Database Models**: Core entities include Users, Products, Categories, Brands, Suppliers, Branches, StockLevel (unique per branch-product pair), and StockMovement (transaction logs with balance tracking).
- **Frontend**: HTML templates with jQuery and custom JavaScript (e.g., tables.js) enable modal-based CRUD operations. Static assets include CSS, fonts, and vendor libraries for a polished user experience.
- **Security**: Role-based access controls restrict features by user type; however, the system currently employs plain-text password storage in the legacy model (a known security caveat requiring migration to hashed passwords).
- **Deployment**: Configured for development with SQLite; production-ready with PostgreSQL support, environment variable configuration, and static file collection.

The application runs on Python 3.10+ and is accessible via standard web browsers, with no client-side installation required.

### 2.2 Business Purpose of the System
The Inventory Management System addresses the critical need for accurate, centralized inventory control in multi-branch retail operations, particularly those dealing with diverse product catalogs such as paint supplies. Its primary business objectives include:

- Minimizing stock discrepancies through real-time tracking and movement logging.
- Enhancing operational efficiency by providing branch managers with tools for immediate stock adjustments and reporting.
- Supporting data-driven decision-making via dashboard analytics and historical transaction records.
- Reducing manual errors in inventory counts and supplier management through automated validation and role-based workflows.
- Facilitating scalability for growing retail networks by maintaining per-branch stock isolation while enabling cross-branch visibility for administrators.

By digitizing inventory processes, the system helps businesses maintain optimal stock levels, prevent stockouts or overstocking, and improve overall supply chain visibility.

### 2.3 Key Benefits
The system delivers several operational and strategic advantages:

- **Centralized Control**: Administrators gain a unified view of inventory across all branches, enabling proactive management and resource allocation.
- **Real-Time Accuracy**: Stock levels update instantly with each movement, providing current data for decision-making and reducing audit discrepancies.
- **Role-Based Efficiency**: Tailored access ensures users see only relevant features, streamlining workflows and enhancing security.
- **User-Friendly Interface**: Responsive design and interactive tables accommodate various devices and user skill levels, reducing training time.
- **Scalability and Flexibility**: Support for multiple branches, extensible product categorization, and database options allow adaptation to business growth.
- **Audit Trail**: Comprehensive stock movement logs with handler attribution support compliance and troubleshooting.
- **Cost Optimization**: Low-stock alerts and movement tracking help prevent lost sales and excess inventory carrying costs.

### 2.4 System Limitations
While robust for core inventory tasks, the system has several constraints and known issues:

- **Security Vulnerabilities**: The legacy Users model stores passwords in plain text, posing risks until migrated to Django's hashed authentication system.
- **Authentication Integration**: Partial reliance on a custom user model may cause inconsistencies; full adoption of Django auth is recommended for production.
- **Database Defaults**: SQLite is suitable for development but may not scale for high-volume transactions; PostgreSQL is advised for enterprise use.
- **Feature Scope**: Lacks advanced analytics, automated alerts, or integrations with external systems (e.g., POS or accounting software).
- **Minor Bugs**: Potential issues in stock level string representations and view variable naming may affect display accuracy.
- **Browser Dependencies**: Relies on JavaScript for dynamic features; users with disabled scripts may experience degraded functionality.
- **Production Readiness**: Requires configuration of environment variables, static file serving, and web server setup for live deployment.

Users should monitor for updates addressing these limitations and avoid storing sensitive data until security enhancements are implemented.

## 3. Getting Started

### 3.1 Logging In
1. Open your web browser and navigate to the application URL.
2. Enter your username/email and password.
3. Click the "Login" button.
4. Upon successful login, you will be redirected to the dashboard or product catalog.

[Screenshot: Login Page]

### 3.2 Navigation
The application uses a sidebar menu for navigation. Key sections include:
- Dashboard: Overview of system statistics.
- Product Catalogue: Manage products, categories, brands, and suppliers.
- Manage Stocks: View and update stock levels and movements.
- Manage Users: (Admin only) Add, edit, or delete users.
- Stock History: View transaction logs.
- Account: Update your profile and password.

[Screenshot: Sidebar Navigation]

### 3.3 User Roles
- **Admin**: Full access to all features, including user management.
- **Branch Manager**: Access to stock management for assigned branches.
- **User**: Basic access to view and limited editing of inventory data.

## 4. Core Modules

### 4.1 Product Catalog
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

### 4.2 Stock Management
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

### 4.3 User Management (Admin Only)
Manage system users.

#### Adding a User
1. Navigate to Manage Users.
2. Click "Add User".
3. Enter details: Username, Email, Role, etc.
4. Save the user.

[Screenshot: Add User Form]

### 4.4 Reporting
View reports and history.

#### Dashboard
- Overview counts: Products, Categories, Branches, etc.
- Low stock alerts.

[Screenshot: Dashboard]

#### Stock History
- Filter transactions by branch, product, type, date.
- View detailed logs.

[Screenshot: Stock History Page]

## 5. Workflows

### 5.1 Adding a New Product
1. Log in as Admin or authorized user.
2. Navigate to Product Catalogue.
3. Click "Add Product".
4. Fill in all required fields.
5. Save and verify in the list.

### 5.2 Managing Stock for a Branch
1. Go to Manage Stocks.
2. Select branch.
3. For each product, record IN/OUT movements as needed.
4. Check updated stock levels.

### 5.3 Viewing Reports
1. Access Dashboard for summaries.
2. Use Stock History for detailed transaction views.
3. Export or print as needed.

## 6. Troubleshooting

### 6.1 Common Issues
- **Login Problems**: Ensure correct credentials; contact admin if locked out.
- **Data Not Saving**: Check required fields; refresh page if needed.
- **Slow Loading**: Clear browser cache or check internet connection.

### 6.2 FAQs
- Q: How to reset password? A: Use the Account page or contact admin.
- Q: Can I edit stock without permission? A: Only authorized roles can modify stock.

## 7. Appendices

### 7.1 User Roles and Permissions
- Admin: All access.
- Branch Manager: Stock and branch-specific data.
- User: Read-only mostly.

### 7.2 Glossary
- Stock Movement: IN (adding stock) or OUT (removing stock).
- Branch: Physical location for inventory.

### 7.3 Contact Information
For support, contact the system administrator at [email] or [phone].