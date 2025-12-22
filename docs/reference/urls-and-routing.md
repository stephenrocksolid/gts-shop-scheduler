# URLs and Routing (Backend ↔ Frontend)

Last updated: 2025-12-22

This document defines the **single source of truth** for URLs used by JavaScript and how to safely add/change routes.

## Canonical rule: JS must not hard-code app URLs

**Do not** introduce hard-coded endpoints in JS (`/api/...`, `/jobs/...`, `/calendars/...`, etc).

Instead:

- Use **Django-reversed URLs injected into** `window.GTS.urls` in `rental_scheduler/templates/base.html`.
- Use `rental_scheduler/static/rental_scheduler/js/shared/urls.js` helpers to interpolate templates and build querystrings.

The repo enforces this with:

- `tests/test_no_hardcoded_urls.py`

## Where URLs come from

### Backend URL definitions

- `gts_django/urls.py` mounts the app at root (`include('rental_scheduler.urls')`).
- `rental_scheduler/urls.py` defines URL patterns and names.

### Frontend URL registry

`rental_scheduler/templates/base.html` injects a URL registry:

- `window.GTS.urls.jobList`, `calendarList`, `calendar`, `calendarEvents`, ...
- Template-style URLs:
  - `jobDetailApiTemplate` (expects `{job_id}`)
  - `jobUpdateStatusTemplate` (expects `{job_id}`)
  - `jobDeleteTemplate` (expects `{job_id}`)
  - call reminder templates, print templates, etc.

`shared/urls.js` wraps these into convenient functions, e.g.:

- `GTS.urls.jobCreatePartial({ edit: jobId })`
- `GTS.urls.jobDetailApi(jobId)`

## How to add a new backend endpoint that JS will call

1. **Add the route** in `rental_scheduler/urls.py` with a stable `name=...`.
2. **Inject it into `window.GTS.urls`** in `rental_scheduler/templates/base.html`.
   - Prefer adding either:
     - a direct URL (string), or
     - a template URL containing `{job_id}` / `{pk}` placeholders.
3. **Expose a convenience wrapper** in `rental_scheduler/static/rental_scheduler/js/shared/urls.js` if it will be used in multiple call-sites.
4. **Use the new URL from JS** via `GTS.urls.<name>` (or the wrapper).
5. **Keep the guard test green**:
   - If you must add an allowlist exception (rare), update `tests/test_no_hardcoded_urls.py`.

## Common patterns

- **Template URLs** (recommended for ids):
  - Inject a template with `{job_id}` or `{pk}` and interpolate via `GTS.urls.interpolate(...)`.
- **Querystring URLs**:
  - Inject a base URL and build query params via `GTS.urls.withQuery(...)`.


