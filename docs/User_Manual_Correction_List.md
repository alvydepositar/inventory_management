# User Guide and Manual Correction List

Source document: `docs/User Guide and Manual.pdf` (January 2026)

This file gives exact correction text for the current manual so it matches the running system.

## 1) Table of contents fixes

Page 3, Step-by-Step Procedures list:

- Add missing entry:
  - `bb. Searching Records ...................................................... 50`
- Keep existing `cc. Exporting Stock History .................................... 51`

## 2) User Guide role fixes

Replace the role section on pages 4 to 5 with this text:

`3. User Roles and Responsibilities`

`Access to system features is controlled through assigned user roles. The system currently defines Admin, User, and Branch Manager roles. Available actions may still vary based on deployment settings.`

`3.1 Administrator`

- Manage user accounts and user roles.
- Maintain product records, categories, brands, suppliers, and branches.
- Oversee stock records and report-level data quality.
- Review low stock items and branch-level inventory health.

`3.2 User`

- Record stock actions: Receive, Release, and Transfer to Branch.
- Review stocks on hand and transaction history.
- Use filters and exports for operational reporting.
- Keep inventory records accurate and updated after each movement.

`3.3 Branch Manager`

- Monitor branch-level stock balances and low stock alerts.
- Review branch daily sales and transfer history.
- Verify branch transactions before and after posting.
- Coordinate stock movement between branches when needed.

## 3) Feature description fixes

Page 10, section `d. Stock Management`:

- Replace "Stock In/Stock Out only" wording with:
  - `Record stock actions: Receive Stock, Release Stock, and Transfer to Branch.`
  - `Review quantity changes using before and ending balance fields.`

Page 11, section title:

- Change `e. Stock History` to `e. Transaction Log`.

Page 11, section body:

- Replace "Stock-in and Stock-out transactions" wording with:
  - `This page records Receive, Release, and Transfer actions across branches.`
- Replace "Type (Stock In or Stock Out)" references with:
  - `Action (Receive Stock, Release Stock, Transfer to Branch).`

## 4) Step-by-step procedure fixes

Page 16, `a. Accessing the System`:

- Replace hard-coded URL text with:
  - `Open your assigned system URL in Google Chrome or Microsoft Edge.`
  - `If you are using a local setup, use the local address provided by your administrator.`

Page 17, `c. Logging Out`:

- Replace `Select Logout.` with `Select Log Out.`

Pages 24 to 29, button label consistency:

- Standardize all occurrences to `Click the "Submit" button`.
- Remove lowercase `submit` variants.

Pages 39 to 40, `v. Deleting a Branch`:

- Replace incorrect product wording with:
  - `Deleting a branch permanently removes the branch record.`
  - `This action cannot be undone. Ensure the branch is no longer needed before deleting.`
  - `Once confirmed, the branch will be removed from the branch list.`

Page 41 and related stock action steps:

- Replace `Type of Transaction: Stock In or Stock Out` with:
  - `Choose Action: Receive Stock, Release Stock, or Transfer to Branch.`

Page 47, `z. Viewing Stock History`:

- Rename section to `z. Viewing Transaction Log`.
- Keep route/menu instructions aligned to `Stock History` menu if that label remains, but explain page title as `Transaction Log`.

Page 49, `aa. Filtering Stock History Records`:

- Replace type filter text with:
  - `Select an Action (Receive Stock, Release Stock, Transfer to Branch), or leave as All.`

Page 50, `bb. Searching Records`:

- Reformat as separate lines:
  - `bb. Searching Records`
  - `i. Use the Search field above the table.`
  - `ii. Enter keywords such as product name, branch, or transaction ID. Matching records will be displayed.`

Page 51, `cc. Exporting Stock History`:

- Keep export formats as `CSV/Excel`, `PDF`, and `Copy`.
- Add note:
  - `Apply filters first before exporting to avoid unnecessary records.`

## 5) New content that should be added

Add missing procedures for features already in the system:

- Open branch workspace from Stocks.
- Record `Transfer to Branch` action.
- Use `Low Stocks` tab in branch workspace.
- Use `Daily Sales` tab in branch workspace.
- Use `Branch Transfers` tab in branch workspace.
- Use `All Branches View` for cross-branch reports.

## 6) Global style and terminology rules

Apply these terms consistently across the manual:

- Use `Transaction Log` for the history page title.
- Use `Receive Stock`, `Release Stock`, and `Transfer to Branch` for actions.
- Use `Log Out` (not `Logout`) to match current UI.
- Use `Submit` (capital S) for button text.
- Use `Add Category` and `Edit Category` with consistent capitalization.

