## Phase 6 Execution Plan — Replace HTML scraping with partial endpoints (keep UX identical)

Date: 2025-12-22

### Phase 6 goal
Remove the “fetch full HTML page + `DOMParser` + scrape fragment” pattern used by the calendar search panel.

Instead, the calendar search panel should request a **purpose-built partial endpoint** that returns the job table fragment directly.

### Phase 6 definition of done
- Calendar search results are fetched from a dedicated **job table partial endpoint** (no HTML scraping).
- The rendered search results HTML/UX is **identical** to today (same table markup, same row click behavior).
- No remaining `fetch(GTS.urls.jobList + ...) + DOMParser(...)` patterns for search results.

### Constraints
- **Keep UX identical** (no redesign, no behavior changes).
- **Minimize surface area**: change only what’s needed to remove HTML scraping.
- Maintain existing contracts:
  - `window.GTS.urls`
  - `window.JobPanel`
  - `window.jobCalendar`

---

## 0) Current state (ground truth)

### Where the HTML scraping happens today
- `rental_scheduler/static/rental_scheduler/js/entrypoints/calendar_page.js`
  - On calendar search submit:
    - Builds query params
    - `fetch(GTS.urls.jobList + '?' + params.toString())`
    - Parses HTML with `DOMParser()`
    - Extracts `#job-table-container` and injects its `innerHTML` into `#search-results`

### The “job table fragment” already exists as a template partial
- `rental_scheduler/templates/rental_scheduler/jobs/job_list.html`
  - Wraps the table in:
    - `<div id="job-table-container"> ... </div>`
  - Includes:
    - `rental_scheduler/templates/rental_scheduler/partials/job_list_table.html`

So the fragment we want to return from a new endpoint is effectively the rendered output of:
- `rental_scheduler/templates/rental_scheduler/partials/job_list_table.html`

### Filtering/sorting/pagination logic lives in one place
- `rental_scheduler/views.py` → `JobListView.get_queryset()` + `JobListView.get_context_data()`
  - Handles: `search`, `calendars[]`, `date_filter`, `start_date`, `end_date`, sorting, and pagination.

---

## 1) Phase 6 approach (what we will build)

### 1A) Add a job table fragment endpoint
Add a new GET endpoint that:
- Accepts the **same query params** as `JobListView` (`search`, `calendars`, `date_filter`, etc.)
- Reuses **the exact same filtering/sorting/pagination logic** as `JobListView`
- Returns **only** the rendered job list table fragment (`job_list_table.html`)

Recommended URL + name:
- `GET /jobs/partial/table/` → `name='job_list_table_partial'`

### 1B) Point calendar search at the new endpoint
Update the calendar search submit handler to:
- Fetch `GTS.urls.jobListTablePartial + '?' + params.toString()`
- Inject the response HTML directly into `#search-results`
- Remove `DOMParser` usage entirely for search results

---

## 2) Work breakdown (prioritized, shippable increments)

### 6A) P0 — Backend: implement the job list table partial endpoint

#### Files
- **Update** `rental_scheduler/views.py`
- **Update** `rental_scheduler/urls.py`

#### Tasks
- `rental_scheduler/views.py`
  - Add a new view that **reuses** `JobListView` logic:
    - Preferred: `class JobListTablePartialView(JobListView)` near `JobListView`
    - Set `template_name = 'rental_scheduler/partials/job_list_table.html'`
    - Keep `paginate_by = 25` (or inherit) so `jobs` stays a Django `Page` object (template expects `has_other_pages`, etc.)
  - Optional (only if we want to reduce extra context work):
    - Override `get_context_data()` to avoid loading `calendars` since the table partial doesn’t use it.
    - Keep the fields that the partial *does* require:
      - `jobs`, `current_sort`, `current_direction`, `search_query`, `selected_calendars`, `date_filter`, `start_date`, `end_date`, `search_widened`

- `rental_scheduler/urls.py`
  - Add a new route:
    - `path('jobs/partial/table/', JobListTablePartialView.as_view(), name='job_list_table_partial')`

#### Acceptance checks
- The endpoint returns **200** with valid HTML for the table (no surrounding base layout).
- It responds correctly to existing query params (smoke-check: `search`, `date_filter`, `calendars`).

---

### 6B) P0 — Frontend config: expose the new endpoint in `window.GTS.urls`

#### Files
- **Update** `rental_scheduler/templates/base.html`

#### Tasks
- Add a new Django-injected URL to the global URL map:
  - `GTS.urls.jobListTablePartial = "{% url 'rental_scheduler:job_list_table_partial' %}";`

#### Acceptance checks
- On any page, `window.GTS.urls.jobListTablePartial` exists and is non-empty.

---

### 6C) P0 — Frontend: remove HTML scraping from calendar search

#### Files
- **Update** `rental_scheduler/static/rental_scheduler/js/entrypoints/calendar_page.js`

#### Tasks
- In the search submit handler:
  - Keep query param construction as-is (it correctly emits repeated `calendars=` keys).
  - Replace:
    - `fetch(GTS.urls.jobList + '?' + params.toString())` + `DOMParser()` extraction
  - With:
    - `fetch(GTS.urls.jobListTablePartial + '?' + params.toString())`
    - `searchResults.innerHTML = html;`
- Keep existing behaviors unchanged:
  - Loading state (“Searching…”)
  - Keyboard navigation (`updateJobRows()`)
  - Event delegation (`bindSearchResultsHandlers()`)
  - Focus return to the search input

#### Acceptance checks
- Search still renders the same table markup and row click opens the job panel.
- Browser devtools network shows search requests hitting the new `/jobs/partial/table/` endpoint.
- No remaining `DOMParser` usage for search results.

---

### 6D) P0 — Tests / regression protection

#### Files
- **Add** `rental_scheduler/tests/test_job_list_table_partial.py` (or similar)
- **Update (optional)** `tests/e2e/test_calendar_smoke.py`

#### Tasks
- Add a Django test for the new endpoint:
  - Smoke: `reverse('rental_scheduler:job_list_table_partial')` returns 200
  - Assert the response contains expected table structure (e.g., `<table`, `.job-row`, `job-row-<id>`)
  - Assert the response does **not** contain a full document wrapper (e.g., no `<html`, no `<body`), to enforce “partial only”
  - Behavior parity: confirm the same query params filter results as expected (reuse patterns from `test_job_list_view_filters.py`)

- Optional Playwright guard (recommended if search is business-critical):
  - Add a small assertion that search results populate on the calendar page and a row click opens the panel.

#### Acceptance checks
- `pytest` passes for the new unit test(s).
- Existing tests remain green:
  - `tests/test_no_hardcoded_urls.py`
  - `tests/e2e/test_calendar_smoke.py` (if included in your local run set)

---

## 3) Optional follow-ups (P1, not required for Phase 6 DoD)

### 3A) Make sort/pagination links in the embedded table “safe” on the calendar page
Today, `job_list_table.html` uses relative `href="?sort=..."` links. When embedded into `/calendar/`, those links navigate to `/calendar/?sort=...` (not `/jobs/?...`).

If we decide to fix this (it *does* change behavior), pick one:
- **Option A (minimal / navigates to Jobs page):**
  - Update `job_list_table.html` to build links against `reverse('rental_scheduler:job_list')` as the base.
- **Option B (best UX / stays inside calendar search):**
  - Intercept clicks on header/pagination `<a>` tags in `calendar_page.js`
  - Prevent navigation and re-run the search fetch with the updated query params

### 3B) Add lightweight caching headers (only if needed)
If the endpoint becomes high-traffic, consider server-side caching keyed by query params (but only after measuring).


