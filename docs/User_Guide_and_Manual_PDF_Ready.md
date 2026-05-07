<!-- COVER PAGE -->
# Color Smile Inventory Management System
## User Guide and User Manual

Document version: 1.2  
Document date: May 2, 2026

---


\newpage

<!-- TABLE OF CONTENTS -->
## Table of Contents

1. Part A: User Guide
2. 1. Overview
3. 2. Scope and Key Capabilities
4. 3. Roles and Responsibilities
5. 4. Access Matrix (Recommended)
6. 5. Navigation Overview
7. 6. General Usage Guidelines
8. Part B: User Manual
9. 1. Access and Authentication
10. 2. Dashboard
11. 3. Account Management
12. 3.1 Update Profile
13. 3.2 Change Password
14. 4. User Management (Admin)
15. 5. Inventory Master Data
16. 5.1 Product Catalog
17. 5.2 Product Management (Categories and Brands)
18. 5.3 Supplier Management
19. 5.4 Branch Management
20. 6. Stocks Workspace (Branch-Level)
21. 6.1 Stocks On Hand
22. 6.2 Low Stocks
23. 6.3 Daily Sales
24. 6.4 Branch Transfers
25. 6.5 Transaction Log
26. 7. All Branches Workspace
27. 7.1 Stocks on Hand (All Branches)
28. 7.2 Daily Sales (All Branches)
29. 7.3 Branch Transfers (All Branches)
30. 8. Reports and Export
31. 9. Data Field Glossary
32. 10. Troubleshooting
33. 10.1 Invalid Credentials
34. 10.2 Password Change Failed
35. 10.3 Forgot Password Link
36. 10.4 Cannot Submit Stock Action
37. 10.5 Missing Records in Table
38. 10.6 Export Option Not Producing Expected Data
39. 11. Security and Data Quality Notes
40. 12. Appendix A: Route Index
41. 13. Appendix B: Quick Daily Checklist

\newpage

## Revision History

| Version | Date | Summary |
| --- | --- | --- |
| 1.0 | April 22, 2026 | Full rewrite aligned to current application UI and workflows |
| 1.1 | April 27, 2026 | Language updated to be more user-friendly and less technical |
| 1.2 | May 2, 2026 | Role permissions and branch-based access updated and enforced |

---

\newpage

## Part A: User Guide

## 1. Overview

The Color Smile Inventory Management System is a web-based platform used to manage products, suppliers, branches, stock balances, and stock movements.

The system is designed to:

1. Keep inventory records accurate and up to date.
2. Track stock movement by branch.
3. Reduce manual errors in stock recording.
4. Provide branch-level and all-branch reporting.

## 2. Scope and Key Capabilities

The system supports the following operational areas:

1. User account management.
2. Product master data maintenance.
3. Category and brand maintenance.
4. Supplier maintenance.
5. Branch maintenance.
6. Branch-level stock operations.
7. Branch-level low stock monitoring.
8. Daily sales and transfer reporting.
9. Transaction log filtering and export.

## 3. Roles and Responsibilities

The system currently uses three roles:

1. Admin
2. User
3. Branch Manager

### 3.1 Administrator

Primary responsibilities:

1. Maintain user accounts and user roles.
2. Maintain products, categories, brands, suppliers, and branches.
3. Review stock records and reports for data quality.
4. Monitor low stock alerts and inventory health.

### 3.2 User

Primary responsibilities:

1. Record stock actions accurately.
2. Review stock balances for the assigned branch.
3. Use filters and exports for daily operations.
4. Verify product, branch, and quantity before submission.

### 3.3 Branch Manager

Primary responsibilities:

1. Monitor stock balances and alerts for the assigned branch.
2. Review branch daily sales and branch transfers.
3. Maintain product, category, brand, and supplier records (add/edit).
4. Correct stock transactions for the assigned branch when needed.

### 3.4 Branch Assignment Rules

1. `User` and `Branch Manager` accounts must be assigned to one branch.
2. Non-admin accounts can only access their assigned branch data.
3. `Admin` accounts are not branch-limited and can access all branches.

## 4. Access Matrix (Recommended)

| Function | Admin | User | Branch Manager |
| --- | --- | --- | --- |
| Manage users | Yes | No | No |
| Maintain products, categories, brands, suppliers | Yes (Add/Edit/Delete) | No | Yes (Add/Edit only) |
| Maintain branch records | Yes | No | No |
| Record stock actions | Yes | Yes | Yes |
| Correct/delete stock actions | Yes | No | Yes (Assigned branch only) |
| View branch reports | Yes | Yes (Assigned branch only) | Yes (Assigned branch only) |
| View all-branch reports | Yes | No | No |
| Export reports | Yes | Yes | Yes |

Note: Exports for non-admin accounts only include records within the assigned branch scope.

## 5. Navigation Overview

Main menu groups:

1. Dashboard
2. Administrator
3. Stocks
4. Inventory Management
5. Profile

Core workflow pattern:

1. Select workspace from menu.
2. Filter to the right branch, product, action, and date.
3. Perform action or review records.
4. Export only after filters are finalized.

## 6. General Usage Guidelines

1. Confirm the branch and product before saving stock actions.
2. Verify quantity before submitting release or transfer actions.
3. Use remarks for traceability, especially for unusual transactions.
4. Review transaction log after important inventory updates.
5. Reconcile system records with physical counts regularly.

---

\newpage

## Part B: User Manual

## 1. Access and Authentication

### 1.1 Open the System

1. Open Google Chrome or Microsoft Edge.
2. Go to your assigned system URL.

### 1.2 Sign In

1. Enter your Email or Username.
2. Enter your Password.
3. Optional: enable Remember Me.
4. Click Sign in.

### 1.3 Invalid Login

If credentials are invalid, the system shows an error message.

Action:

1. Re-enter credentials carefully.
2. If still blocked, contact your administrator.

### 1.4 Log Out

1. Open the Profile menu.
2. Click Log Out.

## 2. Dashboard

Dashboard cards and meaning:

1. Branches: total number of branches.
2. Products: total number of products.
3. Tracked Stock: number of tracked stock records.
4. On Hand: total quantity currently on hand.
5. Branches With Alerts: branches with low stock items.
6. Low Stock Items: total low stock records.

Per-Branch Summary:

1. Shows branch name and location.
2. Shows product count, low stock count, and quantity on hand.
3. Includes quick links to branch Stocks and Low Stock view.

## 3. Account Management

## 3.1 Update Profile

1. Open Profile then Account.
2. Update Email, First name, and Last name.
3. Click Save Changes.

## 3.2 Change Password

1. Open Profile then Account.
2. Go to Change Password panel.
3. Enter Current password.
4. Enter New password.
5. Enter Confirm new password.
6. Click Change Password.
7. Sign in again using the new password.

## 4. User Management (Admin)

### 4.1 Open Manage Users

1. Go to Administrator.
2. Click Manage Users.

### 4.2 Add New User

1. Click Add New Record.
2. Enter First Name and Last Name.
3. Enter User Name and Email.
4. Enter Password.
5. Select Role.
6. If role is `User` or `Branch Manager`, select Assigned Branch.
7. Click Submit.

### 4.3 Edit User

1. Find the user row.
2. Click the Edit icon.
3. Update fields.
4. Click Submit.

### 4.4 Delete User

1. Find the user row.
2. Open Actions menu.
3. Click Delete.
4. Confirm deletion.

## 5. Inventory Master Data

## 5.1 Product Catalog

Menu path:

1. Inventory Management
2. Product Catalog

### View and Filter

1. Use Search and table controls to find products.
2. Adjust table page size as needed.

### Add Product

1. Click Add New Record.
2. Enter Product ID.
3. Enter Product Name.
4. Select Category.
5. Select Brand.
6. Enter Unit Price.
7. Enter Low Stock Limit.
8. Select Supplier.
9. Click Submit.

### Edit Product

1. Locate the product.
2. Click Edit icon.
3. Update fields.
4. Click Submit.

### Delete Product

1. Locate the product.
2. Open Actions menu.
3. Click Delete.
4. Confirm deletion.

## 5.2 Product Management (Categories and Brands)

Menu path:

1. Inventory Management
2. Product Management

### Category Management

Add Category:

1. Click Add New Record in Category Catalog.
2. Enter Category Name.
3. Click Submit.

Edit Category:

1. Locate category row.
2. Click Edit icon.
3. Update name.
4. Click Submit.

Delete Category:

1. Locate category row.
2. Open Actions menu.
3. Click Delete.
4. Confirm deletion.

### Brand Management

Add Brand:

1. Click Add New Record in Brand Catalog.
2. Enter Brand Name.
3. Click Submit.

Edit Brand:

1. Locate brand row.
2. Click Edit icon.
3. Update name.
4. Click Submit.

Delete Brand:

1. Locate brand row.
2. Open Actions menu.
3. Click Delete.
4. Confirm deletion.

## 5.3 Supplier Management

Menu path:

1. Inventory Management
2. Supplier Management

### Add Supplier

1. Click Add New Record.
2. Enter Supplier Name.
3. Enter Contact Person.
4. Enter Contact Number.
5. Enter Email.
6. Enter Address.
7. Click Submit.

### Edit Supplier

1. Locate supplier row.
2. Click Edit icon.
3. Update supplier details.
4. Click Submit.

### Delete Supplier

1. Locate supplier row.
2. Open Actions menu.
3. Click Delete.
4. Confirm deletion.

## 5.4 Branch Management

Role scope: Admin only.

Menu path:

1. Inventory Management
2. Branch Management

### Add Branch

1. Click Add New Record.
2. Enter Branch Name.
3. Enter Location.
4. Click Submit.

### Edit Branch

1. Locate branch row.
2. Click Edit icon.
3. Update branch details.
4. Click Submit.

### View Branch Details

1. Locate branch row.
2. Open Actions menu.
3. Click Details.

### Delete Branch

1. Locate branch row.
2. Open Actions menu.
3. Click Delete.
4. Confirm deletion.

### Open Branch Stocks Workspace

1. Locate branch row.
2. Click the package icon.
3. The system opens the selected branch Stocks workspace.

## 6. Stocks Workspace (Branch-Level)

Entry:

1. Open Stocks.
2. Select a branch workspace.

Main branch workspace tabs:

1. Stocks On Hand
2. Daily Sales
3. Branch Transfers
4. Low Stocks
5. Transaction Log (opened by history links or full-tab link)

Access notes:

1. Non-admin users are limited to their assigned branch workspace.
2. Admin can open all branch workspaces.

## 6.1 Stocks On Hand

Use this tab to:

1. Review current quantity by product.
2. Filter by product.
3. Use Record Action or View Log actions.

### Record stock action from Stocks On Hand

1. Click Record Action or Record Stock Action.
2. In Choose Action, select one action type.
3. Action type options are Receive Stock, Release Stock, and Transfer to Branch.
4. Select Product.
5. Select Branch.
6. If Transfer to Branch is selected, select To Branch.
7. Enter Quantity.
8. Optional: enter Notes.
9. Click Receive Stock, Release Stock, or Transfer Stock.

Validation rules:

1. Transfer destination must be different from source branch.
2. Release and transfer quantities cannot exceed available balance.

## 6.2 Low Stocks

Use this tab to:

1. View products at or below low stock limit.
2. Filter by product.
3. Perform quick refill or view log.

Quick refill flow:

1. Click Refill Stock.
2. Review prefilled product and branch.
3. Enter quantity.
4. Click Receive Stock.

## 6.3 Daily Sales

Use this tab to:

1. Review released items for a branch.
2. Filter by product and date or date range.
3. Review cards for Transactions, Items Released, Estimated Value, and Products.

## 6.4 Branch Transfers

Use this tab to:

1. Review transfer records from one branch to another.
2. Filter by product and date range.
3. Review transfer metrics and transfer list.

## 6.5 Transaction Log

Use this view to:

1. Review transaction history with Before and Ending Balance values.
2. Filter by product, action, and date range.
3. Export filtered results.

Action meanings:

1. Received: stock added to branch.
2. Released: stock deducted from branch.
3. Transferred Out: stock moved out to another branch.
4. Transferred In: stock received from another branch.

Open methods:

1. Click View Log from Stocks or Low Stocks rows.
2. Click Open Full Tab from the history modal.

## 7. All Branches Workspace

Use this workspace for cross-branch analysis.

Entry:

1. Open Stocks.
2. Open All Branches View.

Note: This workspace is for `Admin` role only.

Main tabs:

1. Stocks on Hand
2. Daily Sales
3. Branch Transfers

## 7.1 Stocks on Hand (All Branches)

Capabilities:

1. Filter by branch.
2. View product stock list with status and value.
3. View totals by brand.
4. View totals by category.

Cards:

1. Products
2. Stocks On Hand
3. Low Stock Items
4. Estimated Stock Value

## 7.2 Daily Sales (All Branches)

Capabilities:

1. Filter by branch, product, and date or date range.
2. Review released quantity and estimated value.
3. Open related transaction history.

## 7.3 Branch Transfers (All Branches)

Capabilities:

1. Filter by branch, product, and date or date range.
2. Review routes and quantities moved.
3. Open related history trail.

## 8. Reports and Export

Export is available on major data tables.

Export formats:

1. CSV
2. Excel
3. PDF
4. Copy

Export best practices:

1. Apply branch, product, action, and date filters first.
2. Verify the table view matches your intended report scope.
3. Export only after confirming row set and date range.

## 9. Data Field Glossary

Transaction and stock terms:

1. Transaction ID: unique identifier of a stock action.
2. Action: type of stock movement.
3. Before: balance before the action.
4. Ending Balance: balance after the action.
5. Handled By: user who posted the action.
6. Remarks: free-text note for context.
7. Low Stock Limit: minimum quantity threshold defined per product.
8. Short By: quantity needed to reach low stock limit.

## 10. Troubleshooting

## 10.1 Invalid Credentials

1. Check email or username format.
2. Check password.
3. Retry with correct credentials.
4. Contact admin if access still fails.

## 10.2 Password Change Failed

1. Ensure current password is correct.
2. Ensure new and confirm password match.
3. Retry and re-login after success.

## 10.3 Forgot Password Link

1. The login page may show a Forgot Password link.
2. If password reset is not available in your deployment, contact your administrator.

## 10.4 Cannot Submit Stock Action

1. Confirm required fields are filled.
2. For transfer, choose a destination branch.
3. For release or transfer, reduce quantity if balance is insufficient.

## 10.5 Missing Records in Table

1. Check branch filter.
2. Check product filter.
3. Check action filter.
4. Check date range filter.
5. Clear filters and retry.

## 10.6 Export Option Not Producing Expected Data

1. Confirm current filters.
2. Confirm active table and tab.
3. Re-export after adjusting filters.

## 11. Security and Data Quality Notes

1. Do not share login credentials.
2. Log out when leaving shared devices.
3. Use remarks for exceptional transactions.
4. Reconcile system and physical counts on schedule.
5. Escalate discrepancies immediately.

\newpage

## 12. Appendix A: Route Index

| Screen | Route |
| --- | --- |
| Login | `/` |
| Dashboard | `/dashboard/` |
| Manage Users | `/manage-users/` |
| Product Catalog | `/product-catalogue/` |
| Product Management | `/product-details` |
| Supplier Management | `/suppliers/` |
| Branch Management | `/branches/` |
| Stocks Workspace | `/manage-stocks/` |
| Branch Stocks Workspace | `/manage-stocks/<branch_id>/` |
| Transaction Log redirect | `/stock-history/` |
| All Branches View | `/all-branches-view/` |
| Account | `/account/` |
| Log Out | `/logout/` |

\newpage

## 13. Appendix B: Quick Daily Checklist

1. Open Dashboard and review low stock cards.
2. Enter branch workspace and post stock actions.
3. Check Low Stocks tab and refill critical items.
4. Review Transaction Log for correctness.
5. Export required reports after applying filters.
