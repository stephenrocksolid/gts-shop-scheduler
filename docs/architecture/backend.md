# Backend Architecture (Django)

Last updated: 2025-12-22

This document explains the Django backend structure, routing, and the key contracts with the frontend.

## High-level layout

- **Django project**: `gts_django/`
  - Settings: `gts_django/settings.py`
  - Root URLConf: `gts_django/urls.py`
- **Main app**: `rental_scheduler/`
  - URLs: `rental_scheduler/urls.py`
  - Views: `rental_scheduler/views.py` and `rental_scheduler/views_recurring.py`
  - Models: `rental_scheduler/models.py`
  - Templates: `rental_scheduler/templates/`
  - Static: `rental_scheduler/static/`

## Routing

### Project routing

`gts_django/urls.py` mounts the app at the root:

- `path('', include('rental_scheduler.urls'))`

### App routing

`rental_scheduler/urls.py` contains:

- **Pages** (HTML)
  - Home/calendar: `''` and `'calendar/'`
  - Jobs list: `'jobs/'`
  - Calendars CRUD: `'calendars/...`
  - Work orders: `'workorders/...`
  - Invoices: `'invoices/...`
- **Partials** (HTML fragments, used by panel/search)
  - Job create/edit partial: `'jobs/new/partial/'`
  - Job list table partial: `'jobs/partial/table/'`
  - Call reminder create partial: `'call-reminders/new/partial/'`
- **APIs** (JSON)
  - Calendar feed: `'api/job-calendar-data/'`
  - Jobs create/update/detail/status/delete: `'api/jobs/...`
  - Recurrence: `'api/recurrence/materialize/'`

## Views organization

The code is split primarily by feature area:

- `rental_scheduler/views.py`
  - Core HTML pages (calendar, lists)
  - Panel partial endpoints (`job_create_partial`, `job_create_submit`, etc.)
  - Many non-recurring API endpoints
- `rental_scheduler/views_recurring.py`
  - Recurrence-aware API endpoints (create/update/cancel-future/delete-recurring/materialize)
- `rental_scheduler/error_views.py`
  - Custom error handlers + error reporting endpoint

## Key frontend ↔ backend contracts

### URL injection for JS (canonical)

The backend injects a URL registry into the frontend in `base.html`:

- `rental_scheduler/templates/base.html` defines `window.GTS.urls` from Django `{% url ... %}` tags.

This is the canonical way for JS to obtain app endpoints. See:

- `docs/reference/urls-and-routing.md`

### Calendar config injection

The calendar page injects `window.calendarConfig` (non-URL config) to support calendar UX:

- Guardrails (from `rental_scheduler/constants.py`)
- Calendars list + status choices

### Calendar events feed schema

The FullCalendar feed (`GET /api/job-calendar-data/`) returns an `events` array. Each event includes:

- Core fields: `id`, `title`, `start`, `end`, `allDay`
- Styling: `backgroundColor`, `borderColor`
- Behavior: `extendedProps` (must include enough data for click/tooltip flows)

## Tests

- **Unit/integration**: `pytest` (see `rental_scheduler/tests/` and `tests/`)
- **E2E**: `tests/e2e/` (Playwright; expects a running Django server)


