# Work Order Revamp (WeasyPrint + ClassicAccounting) — Execution Plan

Last updated: 2026-01-27

## Goal

Replace the current “print work order” flow with a **Work Order object** that is **created/edited on a dedicated page**, **pulls customers/items from Classic Accounting**, and **renders a PDF via WeasyPrint**.

This is a **major refactor**: we will delete/retire large chunks of the existing Work Order + “job print” codepaths and replace them with a new data model + UI flow.

## Target UX (what the user sees)

### Job Panel buttons (job form partial)

- If **no Work Order exists for the job**:
  - Show **Create WO**
  - Replace **Save & Print WO** with **Save & Create WO**
- If a **Work Order exists**:
  - Show **Edit WO**
  - Show **Print WO** (PDF via WeasyPrint)
- Remove (job-based printing):
  - **Print WO** (old job-print button)
  - **Print Customer WO**

### Work Order page (new / revamped)

Header section (compact, Tailwind-styled):

- **Customer**: selector backed by Classic Accounting customers, plus “Create new customer” (writes to Classic, stores orgid locally)
- **Work Order #**: auto-incrementing; starting number configurable in settings
- **Job By**: dropdown populated from an “Employees” setting list (name only)
- **Notes**: prefilled from Job’s `repair_notes`
- **Make / Model & Color / Serial Number**: prefilled from Job:
  - Make/Model: `trailer_details`
  - Color: `trailer_color`
  - Serial: `trailer_serial`

Line items:

- Table with **Quantity**, **Part Number**, **Item Description**, **Price**, **Amount**
- Items must come from Classic Accounting items (`itm_items`)
  - Part Number ↔ `itemnumber`
  - Item Description ↔ `salesdesc`
  - Price default ↔ `itm_items.price` (editable per line)
  - Amount = `qty * price` (computed)

Totals:

- Subtotal
- Discount
- Total

Print:

- Save + Print produces a **single** **PDF** (WeasyPrint) matching the provided layout (start with rough draft, iterate).

## Current state inventory (what exists today)

### Job print (Job-based, not WorkOrder-based)

- **Buttons** in `rental_scheduler/templates/rental_scheduler/jobs/_job_form_partial.html`
  - `Print WO`, `Print Customer WO`, `Print Invoice`, `Save & Print WO`
- **JS print orchestration** in `rental_scheduler/static/rental_scheduler/js/entrypoints/job_form_partial.js`
  - Uses `GTS.urls.jobPrint(jobId, printType)` and prints via hidden iframe.
- **Views**:
  - `JobPrintWOView`, `JobPrintWOCustomerView` in `rental_scheduler/views.py`
- **Templates**:
  - `rental_scheduler/templates/rental_scheduler/jobs/job_print_wo.html`
  - `rental_scheduler/templates/rental_scheduler/jobs/job_print_wo_customer.html`

### WorkOrder (separate CRUD pages + browser-print HTML)

- **Models**:
  - `WorkOrder`, `WorkOrderLine` in `rental_scheduler/models.py`
- **Views/URLs**:
  - `WorkOrder*View` (list/detail/create/update/delete/print) in `rental_scheduler/views.py`
  - Routes in `rental_scheduler/urls.py` under `/workorders/...`
  - `POST /api/workorders/<pk>/add-line/` (`workorder_add_line_api`)
- **Templates** (browser print, not PDF):
  - `rental_scheduler/templates/rental_scheduler/workorders/workorder_print.html`
  - `rental_scheduler/templates/rental_scheduler/workorders/workorder_customer_print.html`
  - plus list/detail/form templates

### WeasyPrint

- `weasyprint` is already in `requirements.txt`, but is **not currently used** in app code.

## Constraints / repo rules we must follow

- **No hard-coded app URLs in JS**. Use `window.GTS.urls` + `rental_scheduler/static/rental_scheduler/js/shared/urls.js`.
  - Canonical doc: `docs/reference/urls-and-routing.md`
  - Guard test: `tests/test_no_hardcoded_urls.py`
- Any new HTMX-swap initialization must be **idempotent** (avoid double-binding; prefer delegation).

## Decisions (locked)

1. **Print variants**
   - Single Work Order PDF only (**no** customer copy).
2. **WO number format**
   - Work Order numbers are **integers only** (auto-incrementing; start number configurable).
3. **Line item pricing**
   - Work Order line items include **Price** and **Amount** (not just 3 columns).
4. **Discount semantics**
   - Discount can be either **$** (fixed amount) or **%** (percentage).
   - UI must be extremely user-friendly (see “Discount UI” in Phase 4).
5. **Customer editing**
   - Customer data is **editable** and is written back to Classic Accounting (source of truth).
6. **Navigation behavior**
   - Create/Edit/Print Work Order opens in the **same tab**.
7. **Work order list page**
   - Remove `/workorders/` list/browse UI; WOs are accessed from the Job Panel.

## Assumptions (we will implement unless proven wrong)

- **Tax**: Work Orders do **not** compute sales tax; totals are subtotal − discount. (Invoices handle tax separately.)
- **Line price default**: default line price is Classic `itm_items.price` at selection time, but can be overridden per line.
- **Classic customer mapping**:
  - `Org.orgname` ← Name
  - `Org.phone1` ← Phone #
  - `Org.contact1` ← Contact
  - `Org.email` ← Email
  - `OrgAddress` (`addresstype='BILLTO'`) ← Address/City/State/ZIP
- **Post-save UX**: after saving, redirect to the Work Order edit page; Print navigates to an inline PDF endpoint with a “Back to Work Order” link.

## Implementation plan (phased, step-by-step)

### Phase 0 — Lock contracts + deletion list

- Convert the above decisions into concrete contracts:
  - final field list + validation rules
  - final URL map (including `window.GTS.urls` injections for any JS-called endpoints)
  - explicit deletion list (what is removed, and when)

Deliverables:
- Finalized data model outline (fields + validations)
- Finalized URL map (new endpoints + injected `window.GTS.urls` keys)
- Final “delete list” with owner file paths (views/templates/JS)

Status: ✅ Completed (2026-01-27)

#### Contracts: data model (scheduler DB)

**WorkOrderCompanyProfile (singleton)**

- **Purpose**: Render company header block on the PDF and editor page.
- **Fields**:
  - `name` (required)
  - `slogan` (blank)
  - `address_line1`, `address_line2`, `city`, `state`, `zip` (blank)
  - `tel`, `fax`, `email` (blank)

**WorkOrderEmployee**

- **Purpose**: Source for “Job By” dropdown.
- **Fields**:
  - `name` (required, unique)
  - `is_active` (default true)

**WorkOrderNumberSequence (singleton)**

- **Purpose**: Concurrency-safe allocator for integer work order numbers.
- **Fields**:
  - `start_number` (PositiveInteger, configurable)
  - `next_number` (PositiveInteger, allocated via transaction)
- **Allocator contract**:
  - `allocate_work_order_number()` uses `select_for_update()` in a transaction, returns current `next_number`, then increments by 1.
  - No duplicates under concurrent requests.

**WorkOrder**

- **Relationship**:
  - `job`: OneToOne → `Job` (required, unique; accessed from job panel as `job.work_order`)
- **Header fields**:
  - `number`: PositiveInteger (required, unique) — “Work Order #”
  - `customer_orgid`: PositiveInteger (nullable) — Classic `Org.orgid`
  - `job_by`: FK → `WorkOrderEmployee` (nullable)
  - `notes`: Text (blank; default from `Job.repair_notes`)
  - `trailer_make_model`: Text (blank; default from `Job.trailer_details`)
  - `trailer_color`: Char (blank; default from `Job.trailer_color`)
  - `trailer_serial`: Char (blank; default from `Job.trailer_serial`)
- **Totals / discount** (no tax):
  - `discount_type`: choices `amount` / `percent` (default `amount`)
  - `discount_value`: Decimal(12,2) (default 0)
  - `subtotal`: Decimal(12,2) (computed, stored)
  - `discount_amount`: Decimal(12,2) (computed, stored)
  - `total`: Decimal(12,2) (computed, stored) where `total = subtotal - discount_amount`
- **Validation rules**:
  - `number > 0` and unique
  - if `customer_orgid` is set, it must exist in Classic (validated via the accounting DB when configured)
  - discount:
    - percent: 0–100
    - amount: 0–subtotal
  - totals are always recomputed server-side from lines + discount; client-provided totals are ignored

**WorkOrderLine**

- **Fields**:
  - `work_order`: FK → `WorkOrder` (required)
  - `itemid`: PositiveInteger (required) — Classic `ItmItems.itemid`
  - `itemnumber_snapshot`: Char(blank) — Classic `itemnumber` at selection time
  - `description_snapshot`: Char(blank) — Classic `salesdesc` at selection time
  - `qty`: Decimal(10,2) (> 0)
  - `price`: Decimal(12,2) (>= 0)
  - `amount`: Decimal(12,2) (computed, stored), where `amount = qty * price`
- **Validation rules**:
  - `itemid` must exist in Classic (validated via accounting DB when configured)
  - `amount` is always recomputed server-side as `qty * price`

#### Contracts: URL map + `window.GTS.urls` keys

**New Work Order routes (Django, scheduler DB)** — implemented in `rental_scheduler/urls.py`

- `workorder_new`: `GET|POST /workorders/new/`
  - `GET` expects query `job=<job_id>` for prefill/create-from-job UX
- `workorder_edit`: `GET|POST /workorders/<int:pk>/edit/`
- `workorder_pdf`: `GET /workorders/<int:pk>/pdf/` (returns `application/pdf`, inline)

**Accounting-backed API routes** — implemented in `rental_scheduler/urls.py`

- `accounting_customers_search`: `GET /api/accounting/customers/search/` (`?q=...`)
- `accounting_customers_create`: `POST /api/accounting/customers/create/`
- `accounting_customers_update`: `POST /api/accounting/customers/<int:orgid>/update/`
- `accounting_items_search`: `GET /api/accounting/items/search/` (`?q=...`)
- (optional) `accounting_items_detail`: `GET /api/accounting/items/<int:itemid>/`

**Injected into `window.GTS.urls` in `rental_scheduler/templates/base.html`**

- `GTS.urls.workOrderNewBase`
- `GTS.urls.workOrderEditTemplate`
- `GTS.urls.workOrderPdfTemplate`
- `GTS.urls.accountingCustomerSearch`
- `GTS.urls.accountingCustomerCreate`
- `GTS.urls.accountingCustomerUpdateTemplate`
- `GTS.urls.accountingItemSearch`
- `GTS.urls.accountingItemDetailTemplate` (optional)

**JS helper wrappers in `static/rental_scheduler/js/shared/urls.js`**

- `GTS.urls.workOrderNew(queryParams)` (uses `withQuery()` on `workOrderNewBase`)
- `GTS.urls.workOrderEdit(pk)` (interpolates `workOrderEditTemplate`)
- `GTS.urls.workOrderPdf(pk)` (interpolates `workOrderPdfTemplate`)
- `GTS.urls.accountingCustomerUpdate(orgid)` (interpolates `accountingCustomerUpdateTemplate`)
- `GTS.urls.accountingItemDetail(itemid)` (optional)

#### Deletion list (Phase 7)

**Job-based WO printing (remove)**

- **Views**: `rental_scheduler/views.py`
  - `JobPrintWOView`
  - `JobPrintWOCustomerView`
- **URLs**: `rental_scheduler/urls.py`
  - `job_print_wo`
  - `job_print_wo_customer`
- **Templates**:
  - `rental_scheduler/templates/rental_scheduler/jobs/job_print_wo.html`
  - `rental_scheduler/templates/rental_scheduler/jobs/job_print_wo_customer.html`
- **Job panel buttons**: `rental_scheduler/templates/rental_scheduler/jobs/_job_form_partial.html`
  - “Print WO”
  - “Print Customer WO”
  - “Save & Print WO”
- **Frontend print wiring**: `rental_scheduler/static/rental_scheduler/js/entrypoints/job_form_partial.js`
  - print types `wo` / `wo-customer`
- **URL injection / helper mapping**:
  - `rental_scheduler/templates/base.html`: `GTS.urls.jobPrintWoTemplate`, `GTS.urls.jobPrintWoCustomerTemplate`
  - `rental_scheduler/static/rental_scheduler/js/shared/urls.js`: `GTS.urls.jobPrint()` mapping

**Legacy WorkOrder CRUD/list + browser-print HTML (remove/retire)**

- **Views / API**: `rental_scheduler/views.py`
  - `WorkOrderListView`, `WorkOrderDetailView`, `WorkOrderCreateView`, `WorkOrderUpdateView`, `WorkOrderDeleteView`
  - `WorkOrderPrintView`, `WorkOrderCustomerPrintView`
  - `workorder_add_line_api`
- **URLs**: `rental_scheduler/urls.py`
  - `workorder_list`, `workorder_create`, `workorder_detail`, `workorder_update`, `workorder_delete`
  - `workorder_print`, `workorder_customer_print`
  - `workorder_add_line_api`
- **Templates**:
  - `rental_scheduler/templates/rental_scheduler/workorders/workorder_list.html`
  - `rental_scheduler/templates/rental_scheduler/workorders/workorder_detail.html`
  - `rental_scheduler/templates/rental_scheduler/workorders/workorder_form.html`
  - `rental_scheduler/templates/rental_scheduler/workorders/workorder_print.html`
  - `rental_scheduler/templates/rental_scheduler/workorders/workorder_customer_print.html`
  - `rental_scheduler/templates/rental_scheduler/workorders/workorder_confirm_delete.html`
  - `rental_scheduler/templates/rental_scheduler/partials/workorder_line_row.html`

---

### Phase 1 — Classic Accounting integration (bring in proven module)

Goal: Add a **read/write** Classic Accounting integration to this repo, using the existing implementation from:
`/home/joshua/Documents/Py Projects/gts-rental-scheduler/accounting_integration/`.

Steps:

- Add a new Django app in this repo: `accounting_integration/` (vendored copy, trimmed if desired).
- Configure multi-database support in `gts_django/settings.py`:
  - Add `DATABASES['accounting']` using env vars:
    - `ACCOUNTING_DB_NAME`, `ACCOUNTING_DB_USER`, `ACCOUNTING_DB_PASSWORD`, `ACCOUNTING_DB_HOST`, `ACCOUNTING_DB_PORT`
- Add database router (`AccountingRouter`) and configure `DATABASE_ROUTERS`.
- Add smoke checks:
  - A small management command or Django check to verify we can query `Org` and `ItmItems` via the accounting DB.

Deliverables:
- Accounting DB connection works locally
- `Org` (customers) + `ItmItems` (items) queryable

Status: ✅ Completed (2026-01-27)

Notes:
- Added Django app `accounting_integration/` (router + unmanaged models: `Org`, `ItmItems`).
- Updated `gts_django/settings.py` with `DATABASES['accounting']` + `DATABASE_ROUTERS`.
- Added smoke-check command: `python manage.py validate_accounting`.
- Added tests:
  - `rental_scheduler/tests/test_accounting_integration_setup.py`
  - `rental_scheduler/tests/test_validate_accounting_command.py`

---

### Phase 2 — New Work Order settings models (scheduler DB)

Goal: Add settings data that is **owned by this app** (not Classic):

- Company info:
  - name, slogan, address, tel, fax, email
- Employees:
  - name only
- Work order numbering:
  - configurable “start number” + a concurrency-safe allocator

Steps:

- Add models (names TBD):
  - `WorkOrderCompanyProfile` (singleton)
  - `WorkOrderEmployee`
  - `WorkOrderNumberSequence` (or embed sequence fields in a singleton settings row)
- Add admin integration and/or a Tailwind settings page.
  - If we want non-admin users to edit these, create explicit settings pages and routes.

Deliverables:
- Settings can be edited
- WO number allocation logic is reliable (transactional, no duplicates)

Status: ✅ Completed (2026-01-27)

Notes:
- Added scheduler-owned settings models:
  - `WorkOrderCompanyProfile` (singleton)
  - `WorkOrderEmployee`
  - `WorkOrderNumberSequence` (singleton) with `allocate_work_order_number()` using `transaction.atomic()` + `select_for_update()`
- Added admin integration for all three models in `rental_scheduler/admin.py`.
- Added migration `rental_scheduler/migrations/0039_add_work_order_settings_models.py`.
- Added tests `rental_scheduler/tests/test_work_order_settings_models.py`.

---

### Phase 3 — Revise Work Order domain model (scheduler DB)

Goal: Replace the current `WorkOrder` / `WorkOrderLine` schema with a schema that supports:

- Link to Job (still effectively 1:1)
- Customer link to Classic (`orgid` stored as integer)
- Job By employee
- Notes + trailer fields snapshot (optional; can also pull live from Job)
- Line items linked to Classic items (`itemid` and/or `itemnumber`), plus qty, price, amount
- Discount + totals

Steps:

- Decide migration strategy:
  - **Option A (clean break)**: create new tables (`WorkOrderV2`, etc), migrate UI to them, then delete old later.
  - **Option B (in-place)**: evolve `WorkOrder` / `WorkOrderLine` with migrations, keeping table names.
- Implement server-side validation:
  - Customer orgid must exist in Classic (or be blank until created)
  - Items must exist in Classic
  - Totals recomputed server-side (do not trust client)

Deliverables:
- New models + migrations
- Admin shows new fields correctly

Status: ✅ Completed (2026-01-27)

Notes:
- Chose **Option A (clean break)**: added parallel models (`WorkOrderV2`, `WorkOrderLineV2`) so legacy WorkOrder CRUD/print can stay in place until Phase 7 cleanup.
- Added pricing/totals utility + unit tests:
  - `rental_scheduler/utils/work_orders.py`
  - `rental_scheduler/tests/test_work_order_pricing.py`
- Added new WO v2 models + migrations + tests:
  - `rental_scheduler/models.py`: `WorkOrderV2`, `WorkOrderLineV2` (stores Classic customer ID as `customer_org_id` = `Org.org_id`)
  - `rental_scheduler/migrations/0040_add_work_order_v2_models.py`
  - `rental_scheduler/tests/test_work_order_v2_models.py`
- Added admin integration:
  - `rental_scheduler/admin.py`: `WorkOrderV2Admin`, `WorkOrderLineV2Admin`
- Server-side validation:
  - totals are recomputed server-side (line `amount`, WO `subtotal/discount_amount/total`)
  - Classic existence checks run **only when** the accounting DB is configured (PostgreSQL) to avoid breaking local/test environments without Classic.

---

### Phase 4 — Work Order editor page (Tailwind UI)

Goal: A new “Create/Edit Work Order” page that matches app styling and supports:

- Prefill from Job
- Customer search/select + create-new-customer flow
- Item search/select + line item table editing
- Subtotal/discount/total calculation
- Discount UI:
  - clearly shows “Discount: $ / %” (segmented control or dropdown)
  - shows the computed discount amount in dollars when using %
  - prevents invalid discounts (e.g., % > 100, $ > subtotal)

Backend pieces:

- New Django views/routes for:
  - `GET workorders/new/?job=<job_id>` (create)
  - `GET workorders/<id>/edit/` (edit)
  - `POST workorders/...` (save)
  - `GET workorders/<id>/pdf/` (single PDF print)
- New accounting-backed API endpoints:
  - `GET api/accounting/customers/search?q=...`
  - `POST api/accounting/customers/create` (creates Org + BILLTO address; returns orgid)
  - `POST api/accounting/customers/<orgid>/update` (updates Org + BILLTO address; returns orgid)
  - `GET api/accounting/items/search?q=...`
  - (optional) `GET api/accounting/items/<itemid>` for precise fetch

Frontend pieces:

- New JS module (entrypoint) for Work Order page:
  - Debounced search for customers/items
  - Adds/removes lines idempotently
  - Uses **only** `GTS.urls.*` (no hard-coded URLs)

Deliverables:
- Fully functional WO editor page
- Works with real Classic data (customers/items)

Status: ✅ Completed (2026-01-27)

Notes:
- Added Work Order v2 editor routes + views:
  - `GET|POST /workorders/new/?job=<job_id>` → `workorder_new`
  - `GET|POST /workorders/<id>/edit/` → `workorder_edit`
- Added accounting-backed APIs:
  - `GET /api/accounting/customers/search/`
  - `POST /api/accounting/customers/create/`
  - `POST /api/accounting/customers/<orgid>/update/`
  - `GET /api/accounting/items/search/`
- Added new template `rental_scheduler/templates/rental_scheduler/workorders_v2/workorder_form.html`
  - Job prefill (notes + trailer fields)
  - Customer search/select + create/edit modal
  - Line items with item search + add/remove
  - Client-side subtotal/discount/total preview (server is source of truth)
- Added JS entrypoint `static/rental_scheduler/js/entrypoints/work_order_page.js`
  - Debounced customer/item search
  - Idempotent add/remove line rows
  - Uses `GTS.urls.*` only (no hard-coded URLs)
- Injected new URL keys in `base.html` and helpers in `shared/urls.js`
- Updated URL guard test to forbid `/workorders/` + `/api/accounting/` hard-coded URLs
- Added tests:
  - `rental_scheduler/tests/test_work_order_editor_v2.py`
  - `rental_scheduler/tests/test_work_order_urls_injected.py`
  - `tests/test_no_hardcoded_urls.py` updated guardrails
- Expanded `accounting_integration.models` with `OrgAddress` + required Org fields for create/update flows.

---

### Phase 5 — PDF generation with WeasyPrint

Goal: Print button produces a **PDF response** rendered via WeasyPrint.

Steps:

- Add a new template dedicated to PDF rendering (no `base.html`), with print CSS.
- Implement a `WorkOrderPdfView` that:
  - fetches WorkOrder + lines
  - fetches customer + items (as needed) from Classic using stored IDs
  - renders HTML → PDF via WeasyPrint
  - returns `application/pdf` with `Content-Disposition: inline`
- Ensure assets (logo, fonts) resolve correctly in WeasyPrint (STATIC/MEDIA base URL handling).

Deliverables:
- PDF roughly matches the provided layout
- Stable rendering on server

Status: ✅ Completed (2026-01-27)

Notes:
- Added PDF template `rental_scheduler/templates/rental_scheduler/workorders_v2/workorder_pdf.html`.
- Added WeasyPrint-backed PDF view `workorder_pdf` (`GET /workorders/<id>/pdf/`).
- Added PDF tests:
  - `rental_scheduler/tests/test_work_order_pdf.py` (200 + `%PDF` + HTML contains WO #).
- Added “Print PDF” link on the Work Order edit page.

---

### Phase 6 — Job Panel integration (new buttons + flow)

Goal: Swap Job Panel actions to the new Work Order lifecycle.

Steps:

- Update `rental_scheduler/templates/rental_scheduler/jobs/_job_form_partial.html`:
  - Remove old print buttons
  - Add conditional Create/Edit/Print WO buttons based on `job.work_order` (or new relationship)
  - Replace Save & Print with Save & Create (save job → navigate to WO create page)
- Update `rental_scheduler/static/rental_scheduler/js/entrypoints/job_form_partial.js`:
  - Add handler for **Save & Create WO**
    - Save job via existing HTMX flow, then `window.location.href = <wo create url>` (**same tab**)
- Add new URL injections in `base.html` + helpers in `shared/urls.js` for any new JS-called endpoints.

Deliverables:
- Job Panel shows correct buttons
- “Save & Create WO” works for new + existing jobs

Status: ✅ Completed (2026-01-27)

Notes:
- Updated job form partial (`_job_form_partial.html`):
  - Removed legacy job-based WO print buttons.
  - Added conditional Create/Edit/Print WO buttons using `work_order_v2`.
  - Replaced “Save & Print WO” with “Save & Create WO”.
- Updated job form JS (`entrypoints/job_form_partial.js`):
  - Added “Save & Create WO” flow (save job → navigate to `/workorders/new/?job=...`).
  - Added Create/Edit/Print WO handlers (same-tab navigation).
  - Kept invoice print flow (job-based).
- Injected new URL template:
  - `GTS.urls.workOrderPdfTemplate` + helper `GTS.urls.workOrderPdf`.
- Added tests:
  - `rental_scheduler/tests/test_partials.py` (job panel buttons/legacy print removal).

---

### Phase 7 — Delete/retire old codepaths

Goal: Remove unused code cleanly once the new flow is working.

Candidates to remove/retire (final list depends on Phase 0 decisions):

- Job-based WO print routes/templates:
  - `job_print_wo`, `job_print_wo_customer`, related JS wiring
- Legacy WorkOrder CRUD and browser-print templates:
  - `workorders/workorder_print.html`, `workorder_customer_print.html`
  - `workorder_add_line_api` and related partial templates
- Work order list UI:
  - `WorkOrderListView`, `/workorders/` route, list/partial templates, and any related JS
- Any “print settings” bits that are obsolete after moving to new CompanyInfo settings.

Deliverables:
- Dead code removed
- URLs/JS helpers cleaned up
- Docs updated if any frontend/backend contract changes

Status: ✅ Completed (2026-01-27)

Notes:
- Removed legacy job-based WO print routes + templates:
  - `job_print_wo`, `job_print_wo_customer`
  - `job_print_wo.html`, `job_print_wo_customer.html`
- Removed legacy WorkOrder CRUD/list/print codepaths:
  - `WorkOrder*View` classes + `/workorders/` list/create/detail/print routes
  - `workorder_add_line_api`
  - legacy workorder templates + partials
- Cleaned URL injections / helpers:
  - removed `GTS.urls.jobPrintWoTemplate` and `GTS.urls.jobPrintWoCustomerTemplate`
  - trimmed `GTS.urls.jobPrint(...)` to invoice-only
- Updated template docs (`templates/README.md`) and invoice list to avoid legacy links.
- Added cleanup guard tests: `rental_scheduler/tests/test_work_order_cleanup.py`.

## Test plan

### Unit tests (fast, deterministic)

- **Pricing/totals**
  - subtotal = sum(qty * price)
  - discount calculations for both modes:
    - percent: `discount_amount = subtotal * (pct/100)`
    - dollars: `discount_amount = dollars`
  - clamp/validation:
    - percent \(0–100\)
    - dollars \(0–subtotal\)
  - total = subtotal − discount_amount
- **WO number allocator**
  - sequential allocation
  - transaction safety (no duplicates under concurrent requests)
- **Classic customer mapping**
  - org/address mapping utilities tested without requiring a real accounting DB.

### Django integration tests (scheduler DB)

- Add Django tests for:
  - Work Order create-from-job page:
    - prefill (repair notes + trailer fields)
    - save persists model + lines + totals
    - validates missing/invalid fields
  - Work Order edit page updates:
    - add/remove/update line items
    - discount mode/value changes recalc totals
  - PDF endpoint:
    - returns `200`
    - `Content-Type: application/pdf`
    - body starts with `%PDF` and is non-empty

### Accounting-integration tests (optional; require Classic DB)

- Add pytest marker `@pytest.mark.accounting` for tests that hit the real Classic DB:
  - customer search returns results
  - item search returns results
  - customer create/update roundtrip works
- Skip these tests by default unless accounting env vars are present.

### Guardrails

- Keep `tests/test_no_hardcoded_urls.py` green:
  - Any new JS must use `GTS.urls` helpers.

### E2E (Playwright)

- Add/extend E2E flows (using a test-safe accounting backend or skipping if Classic DB unavailable):
  - Create job → click “Save & Create WO” → WO page loads → add line → save → print PDF (assert PDF headers)
  - Edit customer inline → save → ensure Classic update endpoint called/returns success

## Rollout / migration notes

- If existing WorkOrders matter, prefer **Option A** (parallel v2 tables) to avoid destructive migrations.
- If this is a clean break, we can do **Option B** and remove old fields/templates more aggressively.

