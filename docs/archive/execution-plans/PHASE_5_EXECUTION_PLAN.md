## Phase 5 Execution Plan — Make URL usage consistent (stop hard-coded endpoints)

Date: 2025-12-19

### Phase 5 goal
Make frontend URL usage **consistent and prefix-safe** by eliminating hard-coded app routes inside JS.

- **Calendar-related URLs** should come from Django-injected `window.calendarConfig`.
- **Non-calendar pages** should use either:
  - small `data-*` URL attributes, or
  - a single global Django-injected `window.GTS.urls` (preferred for globally-loaded scripts).

### Phase 5 definition of done
- **No hard-coded app URLs in JS** for the refactored frontend surfaces (calendar/panel/workspace/job form):
  - No `'/rental_scheduler/...'` (app-prefix drift)
  - No direct `'/api/...'`, `'/jobs/...'`, `'/call-reminders/...'`, `'/calendars/...'` literals in the runtime codepaths
  - Instead: all URLs are sourced from `window.calendarConfig.urls` and/or `window.GTS.urls` (or page-local `data-*` attributes).
- Calendar, panel, workspace, and job form flows behave identically (no UX change).

### Constraints
- **No backend contract changes** (Phase 6 handles endpoint changes / partial endpoints).
- **No behavior/UX changes**; this phase is “wiring-only”.
- Keep existing global contracts stable:
  - `window.jobCalendar`
  - `window.JobPanel`
  - `window.JobWorkspace`
  - `window.calendarConfig`

---

## 0) Current state (ground truth)

### Django URL topology
Project URLs mount `rental_scheduler` at root:
- `gts_django/urls.py`: `path('', include('rental_scheduler.urls'))`

So a JS string like `'/rental_scheduler/api/...'` is **incorrect today**, and any root-relative strings like `'/api/...'` only work as long as the app remains mounted at `/`.

### Known hard-coded URL occurrences (Phase 5 scope)
These are the places that must be migrated to config-driven URLs:

#### Calendar modules (`rental_scheduler/static/rental_scheduler/js/calendar/*`)
- `calendar/core.js`
  - Navigations: `window.location.href = '/jobs/'`, `'/calendars/'`
- `calendar/events.js`
  - Fallback: `... || '/api/job-calendar-data/'`
- `calendar/job_actions.js`
  - Open edit: `window.JobPanel.load('/jobs/new/partial/?edit=' + jobId)`
  - Status update: `fetch('/rental_scheduler/api/jobs/' + jobId + '/update-status/', ...)` (bad prefix)
- `calendar/tooltips.js`
  - Job detail tooltip: `fetch('/api/jobs/' + jobId + '/detail/')`
- `calendar/day_interactions.js`
  - Create call reminder: `'/call-reminders/new/partial/?date=...'`
  - Create job: `'/jobs/new/partial/?date=...'`
- `calendar/recurrence_virtual.js`
  - Materialize: `fetch('/api/recurrence/materialize/', ...)`
  - Open edit: `window.JobPanel.load('/jobs/new/partial/?edit=' + jobId)`
- `calendar/call_reminders.js`
  - Mark complete: `fetch('/api/jobs/' + jobId + '/mark-call-reminder-complete/', ...)`
  - Update job reminder notes: `fetch('/jobs/' + jobId + '/call-reminder/update/', ...)`
  - Open edit: `window.JobPanel.load('/jobs/new/partial/?edit=' + jobId)`
  - Update/delete standalone reminders: `'/call-reminders/<pk>/update/'`, `'/call-reminders/<pk>/delete/'`

#### Globally-loaded scripts
Loaded in `base.html`, so they must not depend on “page-specific” config existing.

- `workspace.js`
  - Open edit: `window.JobPanel.load('/jobs/new/partial/?edit=...')`, `'/jobs/new/partial/'`
  - Tooltip fetch: `fetch('/api/jobs/<id>/detail/')`
- `entrypoints/job_form_partial.js`
  - Print URLs: `'/jobs/<id>/print/<type>/'`
  - Status update: `'/api/jobs/<id>/update-status/'`
  - Delete: `'/api/jobs/<id>/delete/'`

#### Calendar page entrypoint
- `entrypoints/calendar_page.js`
  - Search results fetch: `fetch('/jobs/?' + params.toString(), ...)`
  - Row click open edit: `window.JobPanel.load(window.calendarConfig.jobCreateUrl + '?edit=' + jobId)`

#### Jobs list page entrypoint
- `entrypoints/jobs_list_page.js`
  - Has a fallback `'/jobs/new/partial/'` if config not found.

---

## 1) Phase 5 approach (URL policy + API surface)

### Policy (what we standardize)
- **No JS should “know” route strings.**
- **Templates are the source of truth** via `{% url %}`.
- JS code consumes URLs via:
  - `window.calendarConfig.urls` (calendar page)
  - `window.GTS.urls` (global)
  - optional `data-*` URL attributes when the URL is inherently element-specific

### Recommended implementation strategy
Implement a single, reusable “URL templates + interpolation” helper.

#### 1A) Add a small shared helper (Phase 5)
Add a new module:
- `rental_scheduler/static/rental_scheduler/js/shared/urls.js`

Responsibilities:
- **`GTS.urls.interpolate(template, params)`**
  - Supports `{job_id}`, `{pk}`, etc.
  - Throws (or `console.error`) on missing params so failures are loud.
- **Optional convenience wrappers** (reduce repeated param names):
  - `GTS.urls.jobUpdateStatus(jobId)`
  - `GTS.urls.jobDelete(jobId)`
  - `GTS.urls.jobDetailApi(jobId)`
  - `GTS.urls.jobCreatePartial(params?)`
  - `GTS.urls.callReminderUpdate(pk)`
  - etc.

#### 1B) Create one global Django-injected URL map
In `rental_scheduler/templates/base.html`, inject a config object **before** globally-loaded scripts run.

Recommended shape:
- `window.GTS.urls = { ... }`

Include:
- **Page routes**
  - jobs list (`job_list`)
  - calendars list (`calendar_list`)
- **Job partial routes**
  - job create/edit partial (`job_create_partial`)
- **Job API routes**
  - job detail (`job_detail_api`, template with `{job_id}`)
  - job update status (`update_job_status`, template with `{job_id}`)
  - job delete (`delete_job_api`, template with `{job_id}`)
- **Recurrence**
  - materialize occurrence (`materialize_occurrence_api`)
- **Call reminders**
  - create partial (`call_reminder_create_partial`)
  - update (`call_reminder_update`, template with `{pk}`)
  - delete (`call_reminder_delete`, template with `{pk}`)
  - job call reminder update (`job_call_reminder_update`, template with `{job_id}`)
  - mark call reminder complete (`mark_call_reminder_complete`, template with `{job_id}`)
- **Print URLs** (choose one)
  - Option A (explicit): inject 3 templates:
    - `job_print_wo`, `job_print_wo_customer`, `job_print_invoice`
  - Option B (single base): inject a `{job_id}` + `{print_type}` template (only if you add a matching backend route; otherwise keep Option A)

Implementation note:
- Use Django reverse with a placeholder id and convert it into a `{job_id}` template in the template layer:
  - Example concept (not exact code): reverse with `0`, then replace `'/0/'` with `'/{job_id}/'`.

#### 1C) Calendar page should expose URLs via `window.calendarConfig.urls`
In `rental_scheduler/templates/rental_scheduler/calendar.html`:
- Keep `window.calendarConfig` as the calendar-specific config.
- Add `calendarConfig.urls` as the canonical place for all URLs used on calendar.
- Prefer **no URL fallback literals** in calendar modules (they hide missing config problems).

Two acceptable options:
- **Option 1 (no duplication)**: `calendarConfig.urls = window.GTS.urls` (requires `GTS.urls` to exist before this inline script executes).
- **Option 2 (explicit)**: define `calendarConfig.urls` inline using `{% url %}` (most explicit, avoids timing concerns).

---

## 2) Work breakdown (prioritized, shippable increments)

### 5A) P0 — Introduce the canonical URL sources (template + shared helper)

#### Files
- **Update** `rental_scheduler/templates/base.html`
- **Add** `rental_scheduler/static/rental_scheduler/js/shared/urls.js`
- **Update** `rental_scheduler/templates/rental_scheduler/calendar.html`

#### Tasks
- **Base template (`base.html`)**
  - Inject `window.GTS.urls = {...}` using `{% url %}` for all endpoints needed by globally-loaded scripts.
  - Load `shared/urls.js` in the shared load-order block (near the other `shared/*` scripts).
- **Shared helper (`shared/urls.js`)**
  - Implement `GTS.urls.interpolate(template, params)`.
  - Implement minimal convenience builders for the endpoints we actually use in Phase 5.
- **Calendar template (`calendar.html`)**
  - Replace the current partial URL fields (`jobUpdateUrl` weird replace, etc.) with a clear `calendarConfig.urls` object.
  - Ensure `calendarConfig` continues to provide:
    - `calendars`, `statusChoices`, `guardrails`, `currentFilters` (unchanged)

#### Acceptance checks
- All pages still load with **no console errors**.
- `window.GTS.urls` exists on every page.
- On calendar page: `window.calendarConfig.urls` exists and contains the required endpoints.

---

### 5B) P0 — Replace hard-coded URLs in calendar modules

#### Files
- **Update** `rental_scheduler/static/rental_scheduler/js/calendar/core.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/calendar/events.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/calendar/job_actions.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/calendar/tooltips.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/calendar/day_interactions.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/calendar/recurrence_virtual.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/calendar/call_reminders.js`

#### Tasks (per file)
- `calendar/core.js`
  - Replace `window.location.href = '/jobs/'` with `window.calendarConfig.urls.jobList` (or `GTS.urls.jobList`).
  - Replace `window.location.href = '/calendars/'` with `window.calendarConfig.urls.calendarList` (or `GTS.urls.calendarList`).
- `calendar/events.js`
  - Replace the literal fallback `'/api/job-calendar-data/'` with `window.calendarConfig.urls.calendarEvents`.
  - If `calendarConfig.urls.calendarEvents` is missing, fail loudly (console error) rather than silently using a fallback.
- `calendar/job_actions.js`
  - Replace `JobPanel.load('/jobs/new/partial/?edit=' + jobId)` with config-driven URL:
    - `GTS.urls.jobCreatePartial({ edit: jobId })` or string concat with config base.
  - Replace the incorrect `'/rental_scheduler/api/jobs/.../update-status/'` with `GTS.urls.jobUpdateStatus(jobId)`.
- `calendar/tooltips.js`
  - Replace `fetch('/api/jobs/' + jobId + '/detail/')` with `fetch(GTS.urls.jobDetailApi(jobId))`.
- `calendar/day_interactions.js`
  - Replace create URLs for jobs/reminders with config-based base URLs.
  - Keep query params identical (`?date=...&calendar=...`).
- `calendar/recurrence_virtual.js`
  - Replace `fetch('/api/recurrence/materialize/', ...)` with config (`GTS.urls.materializeOccurrence`).
  - Replace open-edit load URL with config-based job partial URL.
- `calendar/call_reminders.js`
  - Replace all call reminder endpoints with config-driven URLs:
    - mark complete
    - job reminder notes update
    - standalone reminder update
    - standalone reminder delete
  - Replace open-edit load URL with config-based job partial URL.

#### Acceptance checks
- Calendar loads, fetches events, and renders normally.
- Clicking a job event opens the edit form in the panel.
- Updating status from the calendar works.
- Call reminder flows (open/save/complete/delete) still work.
- Virtual recurrence materialize still works.

---

### 5C) P0 — Replace hard-coded URLs in globally loaded scripts

#### Files
- **Update** `rental_scheduler/static/rental_scheduler/js/workspace.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/entrypoints/job_form_partial.js`

#### Tasks
- `workspace.js`
  - Replace job detail fetch URL with `GTS.urls.jobDetailApi(jobId)`.
  - Replace job partial load URLs with `GTS.urls.jobCreatePartial({ edit: jobId })` / base + query.
- `entrypoints/job_form_partial.js`
  - Replace status update URL with `GTS.urls.jobUpdateStatus(jobId)`.
  - Replace delete URL with `GTS.urls.jobDelete(jobId)`.
  - Replace print URL building:
    - Prefer config templates for each print type (`wo`, `wo-customer`, `invoice`).

#### Acceptance checks
- Status update + delete from within the job form still work.
- Save-then-print flow still works.
- Workspace tab tooltip still appears (API fetch still works).

---

### 5D) P1 — Replace hard-coded URLs in page entrypoints (calendar search + jobs list)

#### Files
- **Update** `rental_scheduler/static/rental_scheduler/js/entrypoints/calendar_page.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/entrypoints/jobs_list_page.js`

#### Tasks
- `entrypoints/calendar_page.js`
  - Replace `fetch('/jobs/?' + params...)` with config-driven job list URL.
  - Replace `JobPanel.load(window.calendarConfig.jobCreateUrl + '?edit=' + jobId)` with config-driven job partial URL.
- `entrypoints/jobs_list_page.js`
  - Remove the hard-coded fallback `'/jobs/new/partial/'`.
  - Use, in priority order:
    - `window.jobListConfig.jobCreateUrl` (already injected by `job_list.html`)
    - `data-job-create-url` on `#job-table-container`
    - `GTS.urls.jobCreatePartialBase` (global)

#### Acceptance checks
- Calendar search panel still populates results and row click opens job.
- Jobs list row click opens job without regressions.

---

### 5E) P1 — Add a lightweight “no hard-coded URLs” guard

#### Options
- **Option A (fastest)**: add a documented grep check to the manual checklist / PR template.
- **Option B (better)**: add a small pytest test that scans JS files and fails if forbidden patterns are present.

#### Recommended guard
Add a pytest test under `tests/` that scans:
- `rental_scheduler/static/rental_scheduler/js/calendar/**/*.js`
- `rental_scheduler/static/rental_scheduler/js/entrypoints/**/*.js`
- `rental_scheduler/static/rental_scheduler/js/workspace.js`

And fails on matches like:
- `'/rental_scheduler/'`
- `'/api/'`, `'/jobs/'`, `'/call-reminders/'`, `'/calendars/'`

Allowlist:
- `rental_scheduler/static/rental_scheduler/js/config.js` (explicitly out of Phase 5 scope)
- any static asset URLs (should not match if patterns are scoped carefully)

---

## 3) Suggested PR sequence (low-risk rollout)

1. **PR 1 (P0)**: Add `shared/urls.js` + inject `window.GTS.urls` (and `calendarConfig.urls`) — no callsite changes yet.
2. **PR 2 (P0)**: Migrate calendar modules (`calendar/*.js`) off hard-coded URLs.
3. **PR 3 (P0)**: Migrate globally-loaded scripts (`workspace.js`, `entrypoints/job_form_partial.js`).
4. **PR 4 (P1)**: Migrate entrypoints (`calendar_page.js`, `jobs_list_page.js`) + remove remaining fallbacks.
5. **PR 5 (P1)**: Add the “no hard-coded URLs” guard test / documented grep check.

---

## 4) Validation plan (Phase 5)

### Automated
- Run existing Playwright smoke:
  - `tests/e2e/test_calendar_smoke.py`

### Manual (high-signal)
- Calendar:
  - Calendar loads and fetches events.
  - Click event → panel opens edit form.
  - Update status → calendar refreshes.
  - Call reminder: open/save/complete/delete.
  - Virtual recurrence materialize works.
- Job list:
  - Click job row → panel opens edit form.
- Panel/job form:
  - Save job.
  - Delete job.
  - Save then print (WO / WO customer / invoice).
- Workspace:
  - Hover workspace tab → tooltip works.

### Static checks
- Run a repo-wide search to confirm removal of hard-coded route strings from the targeted JS files.

---

## 5) Explicit non-goals (Phase 5)
- Phase 6: replacing HTML scraping (`fetch('/jobs') + DOMParser`) with purpose-built partial endpoints.
- Phase 7: prettier/eslint/bundler changes.
- Refactoring unrelated `config.js` endpoints (that file is a separate legacy config surface and not required for the Phase 5 definition of done).

