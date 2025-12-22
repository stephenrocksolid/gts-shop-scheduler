# Data Model Overview

Last updated: 2025-12-22

This document is a **high-level map** of the core Django models and relationships.
For full details, see `rental_scheduler/models.py`.

## Core scheduling models

### Calendar

File: `rental_scheduler/models.py` (`class Calendar`)

- Represents a logical calendar (e.g. “Shop”, “Mobile Unit A”).
- Key fields:
  - `name` (unique)
  - `color` (hex string)
  - `call_reminder_color` (hex string)
  - `is_active` (bool)

### Job

File: `rental_scheduler/models.py` (`class Job`)

This is the central record that appears on the calendar and is edited in the floating panel.

- Key fields (selected):
  - `calendar` → FK to `Calendar`
  - `start_dt`, `end_dt`, `all_day`
  - `status` (choices include `pending`, `uncompleted`, `completed`, `canceled`)
  - customer/contact fields (business name, phone, address, notes, etc.)
- Call reminder flags (job-linked reminders):
  - `has_call_reminder`
  - `call_reminder_weeks_prior`
  - `call_reminder_completed`

## Recurring events (Google Calendar-like)

File: `rental_scheduler/models.py` (`Job` recurrence fields + helpers)

Recurring series are represented by a **parent job** plus **instance jobs**:

- `recurrence_rule` (JSON): `{ type, interval, count?, until_date? }`
- `recurrence_parent` (FK to self): set on instance jobs
- `recurrence_original_start` (datetime): which occurrence an instance represents
- `end_recurrence_date` (date): stop generating beyond this date

The model also contains helper methods (names may be used by docs/tests):

- `create_recurrence_rule(...)`
- `generate_recurring_instances()`
- `update_recurring_instances(...)`
- `cancel_future_recurrences(...)`

## Call reminders (standalone + linked)

File: `rental_scheduler/models.py` (`class CallReminder`)

Call reminders can exist as:

- **Job-linked** (FK to `Job`)
- **Standalone reminders** (no job; still belong to a `Calendar`)

These reminders are rendered on the calendar and have their own update/delete endpoints.

## Work orders + invoices

### WorkOrder

File: `rental_scheduler/models.py` (`class WorkOrder`)

- `job` → OneToOne to `Job`
- Contains line items via `WorkOrderLine`.

### Invoice

File: `rental_scheduler/models.py` (`class Invoice`)

- `job` → FK to `Job`
- `work_order` → optional FK to `WorkOrder`
- Contains line items via `InvoiceLine`.


