## Phase 1 Execution Plan — Extract inline JS out of templates (no behavior changes) ✅ COMPLETED

This plan is **Phase 1 only** from `FRONTEND_INVENTORY_AND_REFACTOR_PLAN.md`.

### Phase 1 goal / definition of done
- **Goal**: Make frontend code movable/testable by **removing large inline JS** from templates and placing it into dedicated static files.
- **Definition of Done**:
  - `rental_scheduler/templates/rental_scheduler/calendar.html` keeps only **`window.calendarConfig = {...}`** inline.
  - `rental_scheduler/templates/rental_scheduler/jobs/job_list.html` has **no inline `<script>`** (or at most a tiny config object).
  - `rental_scheduler/templates/rental_scheduler/jobs/_job_form_partial.html` has **no large inline `<script>`** and no inline `hx-on::...` orchestration string.
  - No duplicate handlers after repeated open/close/swap actions (idempotent init).

### Constraints (Phase 1)
- **No behavior changes** (UI/UX and persistence must remain identical).
- **No refactors** inside `rental_scheduler/static/rental_scheduler/js/job_calendar.js` beyond what is strictly required to wire extracted code.
- **Keep contracts stable**:
  - Keep existing DOM IDs/classes that other code relies on.
  - Keep existing localStorage keys: `gts-sidebar-width`, `job-list-filters`, `gts-panel-width`, `gts-panel-height`.
  - Keep existing globals used elsewhere: `window.JobPanel`, `window.JobWorkspace`, `window.jobCalendar`, `window.calendarConfig`, `window.showToast`, `window.getCookie`.

---

## 0) Audit notes (ground truth from current code)

### Inline JS sources to extract (actual file locations)
- **Calendar page**: `rental_scheduler/templates/rental_scheduler/calendar.html`
  - Inline `<script>` starts at ~L1356.
  - Contains:
    - `window.calendarConfig = {...}` (**keep inline**)
    - Sidebar resize → `gts-sidebar-width`
    - Scroll prevention + `.fc-popover` wheel handling + popover reposition observer
    - Search panel behaviors (dropdown, submit, fetch `/jobs/?...`, DOMParser `#job-table-container`, keyboard nav, row click → `JobPanel.load(...)`)
- **Jobs list page**: `rental_scheduler/templates/rental_scheduler/jobs/job_list.html`
  - Inline `<script>` starts at ~L246.
  - Contains:
    - Calendar dropdown open/close + selection label
    - Date filter radios + show/hide `#custom-date-range`
    - Persist to `job-list-filters` localStorage
    - Search input Enter behavior (submit once, then cycle highlighted rows)
    - Per-row click/hover handlers on `.job-row` using `data-job-id`
- **Job form partial**: `rental_scheduler/templates/rental_scheduler/jobs/_job_form_partial.html`
  - Form has a large `hx-on::after-request="..."` orchestration string (must be externalized).
  - Inline `<script>` starts at ~L1031.
  - Contains:
    - Calendar `<select>` cloning into `#panel-calendar-selector` (note: `panel.js` already implements this as `initPanelCalendarSelector()`)
    - Toggle wiring (call reminder, recurrence, recurrence end mode)
    - Print handler (delegated) and save-then-print
    - Status update + delete fetch helpers and button handlers
    - Unsaved change tracking init (note: `panel.js` already tracks)
    - HTMX required-field validation interceptor
- **Panel shell** (optional but recommended): `rental_scheduler/templates/rental_scheduler/includes/panel.html`
  - Inline `<script>` starts at ~L387.
  - Contains:
    - `htmx:load` “refresh” binding for `#job-panel .panel-body`
    - Resize handles + persistence to `gts-panel-width` / `gts-panel-height`

### Existing JS that Phase 1 should reuse (to avoid duplication)
- `rental_scheduler/static/rental_scheduler/js/panel.js` already provides:
  - `window.initPanelCalendarSelector(panelBody)` (calendar select cloning)
  - `window.initJobFormToggleUI(rootEl)` (call reminder + recurrence show/hide)
  - HTMX date guardrails validation via `htmx:beforeRequest`
  - JobPanel load/showContent hooks + unsaved tracking
- `rental_scheduler/static/rental_scheduler/js/job_calendar.js` already provides:
  - `window.jobCalendar.toggleSearchPanel()`
  - `window.jobCalendar.selectAllCalendars()`
  - `window.jobCalendar.forceEqualWeekHeights()`

---

## 1) Work breakdown (prioritized, shippable increments)

### 1A) Establish a standard idempotent init pattern (required first)

**Why**: Phase 1 is mostly “move code” work; regressions happen when code binds multiple times (page navigation + HTMX swaps + partial reloads).

**Deliverable**: a tiny helper used by each extracted entrypoint.

**Files / tasks**
- [x] **Add** `rental_scheduler/static/rental_scheduler/js/gts_init.js` ✅
  - Implement **`initOnce(key, fn)`** using a global map (e.g. `window.__gtsInitOnce = {}`)
  - Implement **element-level guards** (e.g. `markElInitialized(el, key)` + `isElInitialized(el, key)` using `data-*`)
  - Implement **DOM + HTMX hooks**:
    - `onDomReady(fn)` (runs immediately if already ready)
    - `onHtmxLoad(fn)` (wraps `document.body.addEventListener('htmx:load', ...)`)
    - `onHtmxAfterSwap(fn)` (wraps `document.body.addEventListener('htmx:afterSwap', ...)`)
  - Keep this helper intentionally small; Phase 2 will introduce a fuller `shared/` module system.
- [x] **Update** `rental_scheduler/templates/base.html` ✅
  - Load `gts_init.js` globally (before page entrypoints that depend on it).

**Acceptance checks**
- Running any initializer multiple times is a no-op (no extra listeners, no duplicated effects).

---

### 1B) Extract `calendar.html` inline JS (keep `window.calendarConfig` inline)

**Target**: `rental_scheduler/templates/rental_scheduler/calendar.html`

**New module**: `rental_scheduler/static/rental_scheduler/js/entrypoints/calendar_page.js`

**Files / tasks**
- [x] **Add directory** `rental_scheduler/static/rental_scheduler/js/entrypoints/` ✅
- [x] **Add** `rental_scheduler/static/rental_scheduler/js/entrypoints/calendar_page.js` ✅
  - Export one initializer (choose one, but keep consistent across Phase 1):
    - `window.GTS.initCalendarPage()` OR
    - `initOnce('calendar_page', () => { ... })`
  - Move these behaviors from inline script:
    - **Sidebar resize**
      - Elements: `#todaySidebar`, `#sidebarResizeHandle`
      - Storage: `gts-sidebar-width`
      - On mouseup: if `window.jobCalendar?.calendar`, call `updateSize()` and `forceEqualWeekHeights()`
      - Idempotency: bind `document` mousemove/mouseup once.
    - **Scroll prevention / wheel routing**
      - Allow wheel scroll inside `#todayList` and `#search-results-container`
      - Prevent wheel scroll in `#calendar-wrap` and `#calendarPage` except:
        - when inside `#todaySidebar`
        - when inside `.fc-popover .fc-popover-body`
      - MutationObserver on `#calendar-wrap` to detect `.fc-popover` insertion:
        - stop propagation on popover body wheel
        - reposition popover to fit viewport (same logic as current inline)
    - **Search panel behaviors** (the search panel open/close button itself lives in `job_calendar.js`; keep using it)
      - Calendar dropdown:
        - `#search-calendar-dropdown-btn`, `#search-calendar-dropdown`, `.search-calendar-checkbox`, `#search-calendar-all-checkbox`, `#search-calendar-selected-text`
        - Default selection: URL `?calendars=` params or else all checked
        - Ensure outside-click closes dropdown
      - Enter-key behavior in `#calendar-search-input`:
        - first Enter submits search
        - subsequent Enters cycle highlight through `.job-row`
      - Clear button `#calendar-clear-search-btn` resets UI + results text
      - Close search button `#calendar-close-search-btn` calls `window.jobCalendar.toggleSearchPanel()`
      - No-calendars overlay button `#calendar-select-all-btn` calls `window.jobCalendar.selectAllCalendars()`
      - Search submit:
        - fetch `GET /jobs/?...` with `X-Requested-With: XMLHttpRequest`
        - DOMParser extract `#job-table-container` (contract with job list view)
        - Insert into `#search-results`
        - Row click opens panel:
          - Use `window.calendarConfig.jobCreateUrl + '?edit=' + jobId`
          - Prefer event delegation on `#search-results` to avoid per-row listener churn

- [x] **Update** `rental_scheduler/templates/rental_scheduler/calendar.html` ✅
  - Keep only the `window.calendarConfig = {...}` inline section.
  - Remove the inline implementations for:
    - sidebar resize
    - scroll prevention
    - search panel behavior
  - In `{% block extra_js %}`:
    - keep existing `job_calendar.js` include
    - add `entrypoints/calendar_page.js` (loaded after `job_calendar.js`)

**Acceptance checks**
- Sidebar width persists (`gts-sidebar-width`) and resizing triggers calendar resize.
- Search results still load, highlight cycles on Enter, and clicking a row opens the panel.
- No duplicate handlers after running multiple searches / opening/closing search panel repeatedly.

---

### 1C) Extract `jobs/job_list.html` inline JS

**Target**: `rental_scheduler/templates/rental_scheduler/jobs/job_list.html`

**New module**: `rental_scheduler/static/rental_scheduler/js/entrypoints/jobs_list_page.js`

**Files / tasks**
- [x] **Add** `rental_scheduler/static/rental_scheduler/js/entrypoints/jobs_list_page.js` ✅
  - Initialize on DOM ready using `gts_init.js` helpers
  - Re-implement current behaviors:
    - Calendar dropdown:
      - `#calendar-dropdown-btn`, `#calendar-dropdown`, `.calendar-checkbox`, `#calendar-selected-text`
      - Close on outside click
      - Update label: `All Calendars` vs `N calendar(s) selected`
    - Date filter radios:
      - `.date-filter-radio`, `#custom-date-range`
      - Toggle visibility when `custom` selected
    - Persist to localStorage:
      - key: `job-list-filters`
      - shape: `{ calendars: [..], dateFilter: 'all'|'future'|'past'|'custom'|'two_years' }`
      - preserve current “only apply saved filters when no active filters” behavior
    - Keyboard navigation in search input:
      - `#search-input` Enter submits once, then cycles highlights on `.job-row`
    - Row click-to-open panel:
      - Delegated click handler rooted at `#job-table-container`
      - Ignore clicks on `a`, `button`, or elements inside them
      - Use `data-job-id` and open via `window.JobPanel.load(...)`
    - Hover feedback:
      - Prefer CSS; if JS is required, use delegated `mouseover/mouseout` (since `mouseenter` doesn’t bubble)

- [x] **Update** `rental_scheduler/templates/rental_scheduler/jobs/job_list.html` ✅
  - Remove the inline `<script>...</script>` block at the bottom.
  - Provide the only needed server URL to JS (choose one approach):
    - **Option A (tiny config)**: inline `window.jobListConfig = { jobCreateUrl: "{% url 'rental_scheduler:job_create_partial' %}" }` ← USED
    - **Option B (data attribute)**: add `data-job-create-url="{% url 'rental_scheduler:job_create_partial' %}"` on `#job-table-container`
  - In `{% block extra_js %}` add `entrypoints/jobs_list_page.js`

**Phase-1-consistent stretch (optional but recommended)**
- [ ] **Update** `rental_scheduler/templates/rental_scheduler/partials/job_row.html`
  - Remove inline `onclick="...JobPanel.load(...)"` from the edit button.
  - Replace with data attributes/classes (e.g. `data-action="edit" data-job-id="..."`) and handle via delegated JS.
  - Rationale: the same rows are injected into calendar search results; removing inline handlers reduces hidden coupling.

**Acceptance checks**
- Dropdown works and closes on outside click.
- `job-list-filters` persists and restores as before.
- Enter behavior matches current behavior.
- Clicking a row opens the JobPanel edit partial.

---

### 1D) Extract `jobs/_job_form_partial.html` inline JS (most sensitive)

**Target**: `rental_scheduler/templates/rental_scheduler/jobs/_job_form_partial.html`

**New module**: `rental_scheduler/static/rental_scheduler/js/entrypoints/job_form_partial.js`

**Key risk**: the form’s current `hx-on::after-request="..."` string controls panel/workspace behavior after saves. This must be reproduced exactly.

**Files / tasks**
- [x] **Add** `rental_scheduler/static/rental_scheduler/js/entrypoints/job_form_partial.js` ✅
  - Provide `initJobFormPartial(rootEl)` that can be called for:
    - HTMX-inserted partial loads (`htmx:load`, `htmx:afterSwap`)
    - Draft restore paths (`JobPanel.showContent()` in `panel.js`)
  - Implement (or reuse) these behaviors:
    - **After-request orchestration (replaces inline `hx-on::after-request`)**
      - Bind `htmx:afterRequest` on the job form element (scoped; guard with `data-*`).
      - On `event.detail.successful`:
        - `JobPanel.clearUnsavedChanges()`
        - If `!JobPanel.isSwitchingJobs`:
          - If current job is in workspace, `JobWorkspace.closeJob(currentJobId)`
          - Else `JobPanel.close(true)`
        - If `window.jobCalendar?.calendar`, `window.jobCalendar.calendar.refetchEvents()`
    - **Required-field interceptor (keeps current behavior)**
      - On `htmx:beforeRequest`:
        - Only for the job form submit request (`hx-post` to `job_create_submit`)
        - Skip if `window.JobPanel?.isSwitchingJobs` is true
        - Block request if missing required fields: `business_name`, `start_dt`, `end_dt`, `calendar`
        - Use `window.showToast(..., 'warning')` and focus first missing field
        - For calendar: focus `#calendar-header-select` if present; else call `window.initPanelCalendarSelector(panelBody)` then focus
    - **Recurrence end-mode toggle**
      - Elements: `#recurrence-end-mode`, `#recurrence-count-container`, `#recurrence-until-container`, `#recurrence-count`, `#recurrence-until`
      - Preserve current behavior:
        - `never` hides both + clears values
        - `after_count` shows count + sets default if empty
        - `on_date` shows until date + clears count
    - **Print flow (save-then-print + iframe)**
      - Move existing delegated handler for `.print-btn` into this module.
      - Keep existing URL patterns: `/jobs/<jobId>/print/<type>/` for `wo`, `wo-customer`, `invoice`.
      - Ensure handler binds exactly once globally.
    - **Status update / delete actions**
      - Implement delegated click handlers:
        - `.complete-btn` → `POST /api/jobs/<id>/update-status/` with `{status: 'completed'}`
        - `.uncomplete-btn` → `POST /api/jobs/<id>/update-status/` with `{status: 'uncompleted'}`
        - `.delete-btn` → confirm → `POST /api/jobs/<id>/delete/`
      - Preserve “save first if unsaved changes” behavior using `JobPanel.saveForm()` when needed.
      - Use `window.getCookie('csrftoken')` for CSRF.

- [x] **Update** `rental_scheduler/templates/rental_scheduler/jobs/_job_form_partial.html` ✅
  - Remove the inline `hx-on::after-request="..."` attribute.
    - Added marker `data-gts-job-form="1"` for scoping.
  - Remove the large inline `<script>...</script>` block.
  - Keep existing external script tags if needed for Phase 1 stability:
    - `all_day_toggle.js`, `phone_mask.js`, `schedule_picker.js`

- [x] **Update** `rental_scheduler/templates/base.html` (or another globally-loaded template) ✅
  - Ensure `entrypoints/job_form_partial.js` is loaded on all pages (the panel can open on any page).

- [x] **Update** `rental_scheduler/static/rental_scheduler/js/panel.js` ✅
  - panel.js already calls `initJobFormToggleUI` and `initPanelCalendarSelector` in showContent
  - job_form_partial.js exposes `window.initJobFormPartial()` and is called from HTMX events
  - Uses `GTS.initOnce` from `gts_init.js` to avoid duplicate listeners.

**Acceptance checks**
- Clicking **Save Job** performs the same post-save close behavior as today (panel/tab closes, calendar refreshes).
- Loading the job form multiple times does not create:
  - multiple print handlers
  - multiple validation interceptors
  - multiple status/delete handlers
- Minimize / outside-click flows still behave identically (especially around `JobPanel.isSwitchingJobs`).

---

### 1E) Recommended add-on (still Phase 1): extract `includes/panel.html` inline JS

**Target**: `rental_scheduler/templates/rental_scheduler/includes/panel.html`

**New module**: `rental_scheduler/static/rental_scheduler/js/entrypoints/panel_shell.js` (or fold into `panel.js` temporarily)

**Files / tasks**
- [x] **Add** `rental_scheduler/static/rental_scheduler/js/entrypoints/panel_shell.js` ✅
  - Move the current inline behaviors as-is:
    - `htmx:load` refresh binding for `#job-panel .panel-body`
    - panel resize handles logic + persistence (`gts-panel-width`, `gts-panel-height`)
  - Bind once globally via `GTS.initOnce('panel_shell_refresh', ...)` and `GTS.initOnce('panel_shell_resize', ...)`
- [x] **Update** `rental_scheduler/templates/rental_scheduler/includes/panel.html` ✅
  - Remove the inline `<script>...</script>` block.
- [x] **Update** `rental_scheduler/templates/base.html` ✅
  - Load `panel_shell.js` globally.

**Acceptance checks**
- Panel resize still works; `gts-panel-width/height` still persist.
- No duplicate refresh listeners after HTMX activity.

---

## 2) Suggested PR / delivery sequence (Phase 1)

Keep each change shippable and reversible.

1. **PR 1**: Add `gts_init.js` + load in `base.html` (no template behavior changes yet).
2. **PR 2**: Calendar extraction (`calendar.html` + `entrypoints/calendar_page.js`).
3. **PR 3**: Job list extraction (`job_list.html` + `entrypoints/jobs_list_page.js`) + optional `partials/job_row.html` cleanup.
4. **PR 4**: Job form partial extraction (`_job_form_partial.html` + `entrypoints/job_form_partial.js` + small `panel.js` hook).
5. **PR 5 (optional)**: Panel shell extraction (`includes/panel.html` + `entrypoints/panel_shell.js`).

---

## 3) Phase 1 validation checklist (quick, practical)

### Must-pass automated checks (already in repo)
- Run Playwright smoke suite: `tests/e2e/test_calendar_smoke.py`
  - This covers calendar load + job panel open + draft/workspace flows that Phase 1 can break.

### Manual checks (focus on idempotency)
- On calendar page:
  - Open/close search panel repeatedly; run multiple searches; ensure clicks/Enter cycling still work.
  - Resize Today sidebar repeatedly; ensure width persists and calendar stays aligned.
- Job form partial:
  - Open/edit a job; close; reopen; ensure print/status/delete handlers behave once.
  - Save a job; ensure post-save close behavior and calendar refetch still occur.
  - Trigger missing-required validation by clicking Save with empty required fields; ensure it blocks and focuses.

