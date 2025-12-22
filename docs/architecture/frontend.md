# Frontend Architecture

Last updated: 2025-12-22

This document explains how the **browser UI** is assembled and which contracts must remain stable.

## High-level model

This app is **server-rendered Django** + a **global JS app shell** + **FullCalendar** on the calendar page.

- Django renders full pages and partials.
- `rental_scheduler/templates/base.html` loads the global JS/CSS and injects URL config into `window.GTS.urls`.
- The floating **Job Panel** and bottom **Workspace tabs** are global UI, present on *every page*.

## Where the frontend code lives

### Templates

- **Base shell**: `rental_scheduler/templates/base.html`
  - Loads core libraries (HTMX, FullCalendar, Flatpickr)
  - Loads shared JS modules (`static/.../js/shared/*`)
  - Injects `window.GTS.urls` (Django-reversed URLs)
  - Includes panel + workspace templates and loads their JS
- **Calendar page**: `rental_scheduler/templates/rental_scheduler/calendar.html`
  - Injects `window.calendarConfig` (guardrails + calendars + status choices)
  - Loads calendar entrypoint via `{% block extra_js %}`
- **Jobs list page**: `rental_scheduler/templates/rental_scheduler/jobs/job_list.html`
  - Loads list entrypoint via `{% block extra_js %}`

### JavaScript

All JS is under `rental_scheduler/static/rental_scheduler/js/`.

- **Shared modules (preferred utilities)**: `shared/`
  - `csrf.js`, `toast.js`, `storage.js`, `dom.js`, `html_state.js`, `urls.js`
- **Page/feature entrypoints**: `entrypoints/`
  - `calendar_page.js`: calendar search panel, sidebar resize, keyboard nav, etc.
  - `jobs_list_page.js`: job list dropdowns/filters, row click behaviors
  - `job_form_partial.js`: job form partial orchestration (runs globally)
- **Calendar modules**: `calendar/`
  - Feature implementation modules mixed into the `JobCalendar` instance
- **Global facades**:
  - `panel.js` → `window.JobPanel`
  - `workspace.js` → `window.JobWorkspace`
  - `job_calendar.js` → `window.jobCalendar` (calendar pages only)

## Runtime contracts (do not break)

### URL registry

- **Contract**: all JS obtains server routes from `window.GTS.urls` (injected by Django).
- **Rule**: never hard-code app URLs in JS (`/api/...`, `/jobs/...`, etc).
- **Reference**: `docs/reference/urls-and-routing.md`

### Global UI facades

These are intentionally global and used across scripts/templates:

- `window.JobPanel` (panel open/load/save/unsaved tracking)
- `window.JobWorkspace` (workspace tabs + draft persistence)
- `window.jobCalendar` (calendar instance and tooltip renderer)

**Reference**: `docs/reference/frontend-globals.md`

### Calendar config injection

The calendar template injects `window.calendarConfig` for server-derived constants and initial lists. URLs should come from `window.GTS.urls` instead.

## Initialization + idempotency

Because the panel loads/swaps HTML fragments, frontend code must be **idempotent**:

- Prefer event delegation for swapped DOM.
- Use `rental_scheduler/static/rental_scheduler/js/gts_init.js` helpers (e.g. “init once” patterns) where needed.
- Avoid binding duplicate handlers on `htmx:load` / `htmx:afterSwap`.

## Guardrails against drift

- **Hard-coded URL guard**: `tests/test_no_hardcoded_urls.py`
- **E2E smoke**: `tests/e2e/test_calendar_smoke.py` (runs against a running dev server)


