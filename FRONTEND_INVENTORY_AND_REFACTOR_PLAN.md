## Frontend Architecture Inventory & Refactor Plan (Feature-Preserving)

Date: 2025-12-18

### Why this document exists
This project started as a Django + HTMX app, but the current UI behaves like a small “desktop app in the browser” (floating editor panel, multi-job workspace tabs, drafts, rich calendar). That’s a valid product direction, but it requires **explicit architecture**, otherwise complexity accumulates in a few huge files.

This doc captures:
- **What we have** (inventory: features, files, dependencies, contracts)
- **What must not regress** (feature checklist)
- **How we can clean it up without losing features** (phased refactor plan)

---

### Guiding principles (non-negotiable)
- **No feature loss**: keep current calendar UX, panel behavior, workspace tabs, drafts, printing, call reminders, recurrence, etc.
- **Refactor in place**: preserve existing URLs/HTML contracts until we migrate them deliberately.
- **Make contracts explicit**: identify the cross-file assumptions and centralize them.
- **Delete dead paths**: remove duplicate/unused logic once verified by tests.

---

### Current high-level architecture
**Server-rendered Django** + **global JS app-shell** + **FullCalendar**.

- Django renders full pages and panel partials.
- `base.html` globally injects:
  - HTMX
  - FullCalendar + Flatpickr
  - Global toast + CSRF helpers
  - **Job Panel** (floating editor) + JS driver
  - **Job Workspace bar** (bottom tabs) + JS driver
- Calendar page (`calendar.html`) renders the calendar shell and injects `window.calendarConfig`.
- `job_calendar.js` owns the FullCalendar instance and most calendar UX.

---

## Feature inventory (do not regress)

### Calendar UX
- **Four-week “month sliding week” view** (4-week window, scroll wheel navigates by week)
- **Multi-calendar selection** (checkbox popover + “select all” + default calendar)
- **Filters persisted** (localStorage + URL params)
- **Search panel** (collapsible, 50vh; runs job search and shows results)
- **Today sidebar**
  - hide/show toggle (persisted)
  - resizable width (persisted)
  - date picker + prev/next/today buttons
  - click item opens corresponding job
- **Tooltips**
  - delayed hover on calendar events
  - delayed hover on today sidebar items
  - delayed hover on workspace tabs (reuse tooltip renderer)
- **Recurring “virtual” occurrences**
  - events feed includes virtual items for forever series
  - clicking virtual occurrence materializes it via API then opens the new job
- **Call reminders**
  - show reminders as events
  - complete/update/delete reminder from UI

### Job editing UX
- **Floating job panel**
  - draggable
  - resizable
  - dock/undock (if enabled)
  - close on outside click
- **Autosave-style flows when switching jobs**
  - when changing selection while panel has changes: save (or draft) then switch
- **Workspace tabs**
  - open multiple jobs
  - minimize current job into tab bar
  - switch between tabs
  - drafts survive reload (localStorage)
- **Draft restore**
  - store form HTML + restore (with sanitization)
  - promote draft → real job after successful save
- **Printing**
  - print work orders / invoices from within the panel using iframe flow

---

## Component inventory

### 1) Global app shell

**Primary files**
- `rental_scheduler/templates/base.html`
- `rental_scheduler/static/rental_scheduler/js/config.js`
- `rental_scheduler/static/rental_scheduler/js/panel.js`
- `rental_scheduler/static/rental_scheduler/js/workspace.js`

**What it loads globally**
- `htmx.min.js` (global)
- `fullcalendar.min.js` + `flatpickr.min.js` (global)
- `config.js` (“RentalConfig”) (global)
- Inline: `window.showToast`, `window.getCookie`, and HTMX CSRF wiring
- Includes + scripts:
  - `includes/panel.html` + `panel.js`
  - `includes/workspace_bar.html` + `workspace.js`

**Global JS objects that other code assumes**
- `window.showToast(message, type, duration)` (defined in `base.html`)
- `window.getCookie(name)` (defined in `base.html`)
- `window.RentalConfig` (defined in `config.js`)
- `window.JobPanel` (defined in `panel.js`)
- `window.JobWorkspace` (defined in `workspace.js`)

**Key architectural note**
Because panel + workspace are global, *every page* shares state and side-effects. This is powerful, but it also means:
- any JS bug can affect unrelated pages
- performance cost exists everywhere
- hidden coupling grows unless we enforce contracts

---

### 2) Calendar page (FullCalendar + custom UX)

**Primary files**
- `rental_scheduler/templates/rental_scheduler/calendar.html`
- `rental_scheduler/static/rental_scheduler/js/job_calendar.js`
- CSS (referenced by template):
  - `rental_scheduler/static/rental_scheduler/css/job_calendar.css`
  - `rental_scheduler/static/rental_scheduler/css/calendar.css`

**Responsibilities**
- Create FullCalendar instance and fully customize UI
- Manage filters (selected calendars, status, search) and persistence
- Fetch event feed (`eventsUrl`) with stale-while-revalidate localStorage caching
- Open jobs and reminders in the Job Panel / Workspace
- Maintain Today sidebar UI
- Render hover tooltips
- Materialize virtual recurring events

**Inputs / data dependencies**
- `window.calendarConfig` injected by `calendar.html`, including:
  - `eventsUrl` (expected: `/api/job-calendar-data/`)
  - `jobCreateUrl` (expected: `/jobs/new/partial/`)
  - `guardrails` (server constants for panel validation)
  - `calendars` list (id, name, color)
  - `statusChoices`

**DOM dependencies (critical IDs)**
- `#calendar` (FullCalendar mount)
- `#calendar-search-panel`, `#calendar-search-form`, `#calendar-search-input`, `#search-results`
- `#calendar-shell`, `#calendar-wrap`
- `#todaySidebar`, `#todayList`, `#todayDatePicker`, `#prevDayBtn`, `#nextDayBtn`, `#todayBtn`, `#sidebarResizeHandle`
- `#calendar-loading`, `#calendar-no-calendars`, `#calendar-select-all-btn`

**LocalStorage keys used**
- UI state:
  - `gts-calendar-search-open`
  - `gts-calendar-today-sidebar-open`
  - `gts-sidebar-width` (set by inline JS in `calendar.html`, not `job_calendar.js`)
- Navigation:
  - `gts-calendar-current-date`
- Filters:
  - `gts-calendar-filters`
  - `gts-selected-calendars`
  - `gts-default-calendar`
- Client event cache:
  - `cal-events-cache:<start>:<end>:<calendarIds>:<status>:<search>` (5-minute TTL, keep last ~5 keys)

**Endpoints touched**
- Events feed:
  - `GET window.calendarConfig.eventsUrl` → `/api/job-calendar-data/`
- Panel partials:
  - `GET /jobs/new/partial/?date=YYYY-MM-DD` (new job)
  - `GET /jobs/new/partial/?edit=<jobId>` (edit)
  - `GET /call-reminders/new/partial/?date=YYYY-MM-DD` (new reminder)
- Recurrence:
  - `POST /api/recurrence/materialize/` (virtual occurrence → real job)
- Call reminders:
  - `POST /api/jobs/<jobId>/mark-call-reminder-complete/`
  - `POST /jobs/<jobId>/call-reminder/update/`
  - `POST /call-reminders/<reminderId>/update/`
  - `POST /call-reminders/<reminderId>/delete/`
- Navigation:
  - `/jobs/`, `/calendars/`

**Known drift / cleanup targets (calendar)**
- **Inline JS in `calendar.html` duplicates responsibilities** (sidebar resize, scroll prevention, search panel fetch/DOMParser flow). Move to a single owner.
- **Duplicate FullCalendar config keys** (e.g. `datesSet` is declared twice in `job_calendar.js`, so one overrides the other).
- **Dead/unused methods** exist (e.g. `showJobRowTooltip()` appears defined but not wired).
- **Hard-coded URL bug risk**: `updateJobStatus()` uses `/rental_scheduler/api/...` even though the app is mounted at `/` (should rely on `calendarConfig.jobUpdateUrl` or `urls.py`-derived path).

---

### 3) Floating Job Panel

**Primary files**
- `rental_scheduler/templates/rental_scheduler/includes/panel.html`
- `rental_scheduler/static/rental_scheduler/js/panel.js`

**Responsibilities**
- Own the floating panel container UI
- Load partials into panel body via HTMX (`htmx.ajax('GET', url, ...)`)
- Track unsaved changes and coordinate with workspace switching/minimizing
- Serialize/sanitize form HTML for draft restore
- Guardrails-based date validation and one-time warnings

**DOM dependencies (critical IDs)**
- `#job-panel`
- `#job-panel-title`
- `#job-panel .panel-body`
- Buttons:
  - `.btn-close`
  - `#panel-delete-btn`
  - `#panel-workspace-minimize-btn`
  - `#panel-calendar-container`, `#panel-calendar-selector` (populated by job form partial)

**LocalStorage keys used**
- Panel position/state:
  - `jobPanelState` (from `panel.js`)
- Panel resize state (note: implemented in *template inline script*, separate from `jobPanelState`):
  - `gts-panel-width`
  - `gts-panel-height`
- One-time warnings per job:
  - `gts-job-initial-save-attempted:job:<id>`
  - `gts-job-initial-save-attempted:temp:<random>` (migrated to job:<id> after save)

**Public API exposed (contract)**
`panel.js` exposes a stable facade:
- `window.JobPanel.open()`
- `window.JobPanel.close(skipUnsavedCheck)`
- `window.JobPanel.load(url)`
- `window.JobPanel.showContent(html)`
- `window.JobPanel.setTitle(title)`
- `window.JobPanel.setCurrentJobId(jobId)`
- `window.JobPanel.saveForm(callback)` (supports options + callback)
- `window.JobPanel.hasUnsavedChanges()`
- `window.JobPanel.clearUnsavedChanges()`
- `window.JobPanel.updateMinimizeButton()`
- State flags:
  - `window.JobPanel.currentDraftId`
  - `window.JobPanel.isSwitchingJobs` (used by job form validation to skip “human submit” checks)

**Known drift / cleanup targets (panel)**
- `panel.js` contains both a **vanilla implementation** and an **Alpine-compatible mode** (it checks for `typeof Alpine !== 'undefined'`).
  - Alpine attributes exist in some templates (`x-data=...`) but Alpine is not loaded in `base.html`.
  - Decide whether Alpine is actually part of the app. If not, remove the Alpine branch.
- Panel resize is implemented twice:
  - Inline script in `includes/panel.html` stores `gts-panel-width/height`
  - Panel state in `panel.js` stores `jobPanelState`
  - Consolidate into one source of truth.

---

### 4) Job Workspace (bottom tab bar)

**Primary files**
- `rental_scheduler/templates/rental_scheduler/includes/workspace_bar.html`
- `rental_scheduler/static/rental_scheduler/js/workspace.js`

**Responsibilities**
- Maintain a list of open jobs (tabs)
- Persist open jobs + drafts to localStorage
- Handle switching jobs (including “unsaved changes” handoff)
- Provide tooltip hover (fetch job details and reuse calendar tooltip renderer)

**LocalStorage keys used**
- Workspace state:
  - `gts-job-workspace`
- Draft IDs are of form:
  - `draft-<timestamp>-<random>`

**Backend endpoints used**
- Tooltip fetch:
  - `GET /api/jobs/<jobId>/detail/`

**Known drift / cleanup targets (workspace)**
- Draft HTML sanitization exists here and in `panel.js` (duplication).
- Workspace relies on `window.jobCalendar.showEventTooltip(...)` for tooltip UI, which is a tight coupling.
  - Either keep this as an explicit contract or move tooltip renderer to a shared module.

---

### 5) Job form partial (loaded inside panel)

**Primary files**
- `rental_scheduler/views.py`: `job_create_partial`, `job_create_submit`
- `rental_scheduler/templates/rental_scheduler/jobs/_job_form_partial.html`
- Supporting JS:
  - `rental_scheduler/static/rental_scheduler/js/all_day_toggle.js`
  - `rental_scheduler/static/rental_scheduler/js/phone_mask.js`
  - `rental_scheduler/static/rental_scheduler/js/schedule_picker.js`

**Important HTMX contract**
- The form uses:
  - `hx-post="/jobs/new/submit/"`
  - `hx-swap="none"`
  - a large `hx-on::after-request="..."` handler

That `after-request` handler currently does cross-component orchestration:
- clears unsaved tracking in JobPanel
- closes panel or closes workspace tab depending on context
- refetches calendar events

**Header calendar selector cloning**
The partial clones the hidden calendar `<select>` into the panel header:
- Original (for submission): `#calendar-field-container select[name="calendar"]` (hidden)
- Clone (visual, no name): `#calendar-header-select` inserted into `#panel-calendar-selector`

**Printing flows**
The partial includes a substantial inline printing system:
- save job (HTMX or fetch fallback)
- open print URL in hidden iframe
- trigger print

**Client-side validation contract**
The partial intercepts `htmx:beforeRequest` to enforce required fields for user-initiated saves, but **skips validation when** `window.JobPanel.isSwitchingJobs` is set (programmatic saves).

**Known drift / cleanup targets (job form partial)**
- Large inline JS should be moved into a dedicated file (or merged into `panel.js`) to avoid redefinition and to enable testing.
- Required-field validation is duplicated with similar logic in `panel.js` (`getRequiredMissing`).

---

### 6) Job list page (and calendar search results reuse)

**Primary files**
- `rental_scheduler/templates/rental_scheduler/jobs/job_list.html`
- `rental_scheduler/templates/rental_scheduler/partials/job_list_table.html`
- `rental_scheduler/templates/rental_scheduler/partials/job_row.html`

**Current behavior**
- The job list page contains large inline JS for:
  - calendar dropdown
  - date filter radios
  - keyboard navigation
  - click-to-open JobPanel
- The calendar search panel (`calendar.html`) performs a `fetch('/jobs/?...')`, then DOM-parses the HTML and extracts `#job-table-container`.

**Cleanup direction (without feature loss)**
- Replace “fetch + DOMParser + extract” with a dedicated partial endpoint (server returns the table fragment directly).
- Share one implementation of dropdown + keyboard navigation between job list and calendar search.

---

## Cross-component contracts (make these explicit)

### A) `window.calendarConfig` schema (calendar.html → JS)
Minimal expected fields:
- `eventsUrl: string`
- `jobCreateUrl: string`
- `guardrails: { minValidYear, maxValidYear, warnDaysInFuture, warnJobSpanDays, ... }`
- `calendars: Array<{ id: number, name: string, color: string }>`

### B) Events feed schema (backend → FullCalendar)
FullCalendar expects `events` array with fields like:
- `id`, `title`, `start`, `end`, `allDay`
- `backgroundColor`, `borderColor`
- `extendedProps` must include enough for click/tooltip logic, commonly:
  - `type` (e.g. `job`, `virtual_job`, `call_reminder`, `virtual_call_reminder`, `standalone_call_reminder`)
  - `job_id` (for job events)
  - `status`, `calendar_color`, `calendar_name`

### C) HTMX save contract (job_create_submit → panel/workspace)
`job_create_submit` returns:
- an `HX-Trigger` header: `{ "jobSaved": { "jobId": <id> } }`

`panel.js` and `workspace.js` depend on this to:
- capture job ID after save
- promote drafts

### D) `window.JobPanel` API stability
Many pages call `JobPanel.setTitle(...)` and `JobPanel.load(...)` directly (calendar, job list, etc.).
We should preserve the facade even if we refactor the internals.

### E) `window.JobWorkspace` API stability
Key calls used by other code:
- `openJob(jobId, meta)`
- `addJobMinimized(jobId, meta)`
- `switchToJob(jobId)`
- `minimizeJob(jobId)`
- `closeJob(jobId)`
- `createDraft(...)`, `promoteDraft(draftId, realJobId, meta)`

---

## Key tech-debt hotspots (what makes the code hard)

### 1) Multiple sources of truth
- Panel sizing/position stored under multiple keys (`jobPanelState` vs `gts-panel-width/height`).
- Calendar layout hacks exist in both template CSS and runtime JS (`forceEqualWeekHeights`).

### 2) Duplicated utilities
- Multiple CSRF strategies (`base.html`, `config.js`, `job_calendar.js`, `panel.js`).
- Multiple toast systems (`window.showToast` vs local toasts).
- Duplicate HTML sanitization/serialization logic across panel/workspace.

### 3) Inline JS in templates
Inline scripts in `calendar.html`, `_job_form_partial.html`, `job_list.html` are large and re-executed on swaps, making it easy to double-bind events and hard to refactor.

### 4) Hidden coupling via globals
`job_calendar.js`, `panel.js`, `workspace.js`, and `_job_form_partial.html` coordinate via shared globals and flags (`isSwitchingJobs`, `currentJobId`, etc.). This is workable, but it must be documented and stabilized.

### 5) Likely dead paths
- Alpine compatibility code is present, but Alpine is not loaded globally.
- Some helper methods appear defined but not wired.

---

## Refactor plan (feature-preserving)

### Phase 0 — Baseline + safety net (before touching code)
**Goal**: be able to refactor aggressively without fear.

- Document the **manual smoke flows** (calendar load, open job, edit, minimize, switch tabs, restore draft, print, call reminder update, virtual occurrence materialize).
- Run existing Playwright smoke tests:
  - `tests/e2e/test_calendar_smoke.py`
- Add/extend Playwright coverage for:
  - minimize → tab appears → restore
  - draft creation and restore after page reload
  - materialize virtual job
  - call reminder complete/update/delete

Definition of Done:
- CI/local run can tell us “refactor didn’t break core UX.”

---

#### Manual Smoke Checklist (Phase 0)

Use this checklist before any significant refactor to verify core UX flows still work. Run against a local dev server (`python manage.py runserver`).

##### 1. Calendar Load
- [ ] Navigate to `/` (calendar page)
- [ ] **Expected**: 4-week month view is visible, no blocking JS errors in console
- [ ] **Expected**: FullCalendar toolbar with navigation buttons is visible
- [ ] **Expected**: Events (if any) render without errors

##### 2. Search Panel
- [ ] Click the search toggle button (magnifying glass or search icon in toolbar)
- [ ] **Expected**: Search panel slides open (top area, ~50vh)
- [ ] Reload the page
- [ ] **Expected**: Search panel state persists (open if it was open)
- [ ] Type a search query and press Enter
- [ ] **Expected**: Results appear in the panel (or "no results" message)
- [ ] Click a result row
- [ ] **Expected**: Job opens in the floating job panel

##### 3. Today Sidebar
- [ ] Click the Today sidebar toggle (if closed)
- [ ] **Expected**: Sidebar slides open on the right side
- [ ] Drag the resize handle to change sidebar width
- [ ] **Expected**: Width changes and is persisted after reload
- [ ] Click an item in the Today list
- [ ] **Expected**: Corresponding job opens in the job panel
- [ ] Toggle sidebar closed, then reload
- [ ] **Expected**: Sidebar stays closed (state persisted)

##### 4. Job Panel (Floating Editor)
- [ ] Click the "Add Job" button in the calendar toolbar
- [ ] **Expected**: Floating job panel opens with a new job form
- [ ] Drag the panel title bar
- [ ] **Expected**: Panel moves with the cursor
- [ ] Drag the panel resize handles (corners/edges)
- [ ] **Expected**: Panel resizes; dimensions persist after reload
- [ ] Click outside the panel (on the calendar background)
- [ ] **Expected**: Panel closes (if no unsaved changes)

##### 5. Workspace Tabs
- [ ] Open a job in the panel (from calendar event or search)
- [ ] Click the minimize button (↓ icon in panel header)
- [ ] **Expected**: Job panel closes; a tab appears in the workspace bar at the bottom
- [ ] Open another job (click different calendar event)
- [ ] Minimize that job too
- [ ] **Expected**: Two tabs visible in workspace bar
- [ ] Click the first tab
- [ ] **Expected**: First job reopens in the panel
- [ ] Close a tab (X button on tab)
- [ ] **Expected**: Tab disappears; if it was the active job, panel closes

##### 6. Drafts (Unsaved Changes Persistence)
- [ ] Click "Add Job" to create a new job
- [ ] Fill in **only** `contact_name` (leave required fields like `business_name` empty)
- [ ] Click the minimize button
- [ ] **Expected**: A tab appears with an "unsaved dot" indicator
- [ ] Reload the page
- [ ] **Expected**: Draft tab persists in the workspace bar
- [ ] Click the draft tab
- [ ] **Expected**: Panel opens with the previously entered `contact_name` restored

##### 7. Printing (Save-then-Print)
- [ ] Open an existing job in the panel
- [ ] Click one of the print buttons (Work Order, Customer WO, or Invoice)
- [ ] **Expected**: Job is saved (if needed), then print dialog/preview appears
- [ ] Cancel the print dialog
- [ ] **Expected**: No errors; calendar remains functional

##### 8. Recurring Virtual Occurrence (Materialize)
- [ ] Create a job with recurrence enabled (weekly, end mode "never")
- [ ] Save the job and close the panel
- [ ] Navigate to a future date where a virtual occurrence should appear
- [ ] **Expected**: Virtual occurrence event is visible (may have distinct styling)
- [ ] Click the virtual occurrence
- [ ] **Expected**: Loading indicator appears briefly
- [ ] **Expected**: Job panel opens with the materialized job (now a real job with its own ID)
- [ ] Close the panel and verify the event is now a regular job event

##### 9. Call Reminders (Standalone)
- [ ] Double-click a **Sunday** cell on the calendar
- [ ] **Expected**: Call reminder creation form opens (not job form)
- [ ] Fill in short notes and click "Create Call Reminder"
- [ ] **Expected**: Reminder event appears on the calendar for that date
- [ ] Click the reminder event
- [ ] **Expected**: Call reminder panel opens with notes textarea and action buttons
- [ ] Edit the notes and click "Save & Close"
- [ ] Click the reminder event again
- [ ] **Expected**: Updated notes are visible
- [ ] Click "Complete" button
- [ ] **Expected**: Reminder marked complete (may show checkmark or styling change)
- [ ] Click "Delete" button (if available) and confirm
- [ ] **Expected**: Reminder event disappears from calendar

---

### Phase 1 — Extract inline JS out of templates (no behavior changes) ✅ COMPLETED

**Goal**: make code movable and testable.

**Status**: ✅ **COMPLETED** (2025-12-18)

**What was done**:

1. **Created `gts_init.js`** - Idempotent initialization helpers
   - `GTS.initOnce(key, fn)` - Run once globally
   - `GTS.markElInitialized(el, key)` / `GTS.isElInitialized(el, key)` - Element-level guards
   - `GTS.onDomReady(fn)`, `GTS.onHtmxLoad(fn)`, `GTS.onHtmxAfterSwap(fn)` - DOM/HTMX hooks
   - `GTS.getCookie()`, `GTS.showToast()` - Convenience wrappers

2. **Created `entrypoints/calendar_page.js`** - Extracted from `calendar.html`
   - Sidebar resize with localStorage persistence
   - Scroll prevention and wheel routing
   - Search panel behaviors (dropdown, form submit, keyboard navigation, row click)
   - Popover repositioning

3. **Created `entrypoints/jobs_list_page.js`** - Extracted from `job_list.html`
   - Calendar dropdown with selection label
   - Date filter radios with custom range visibility
   - localStorage persistence (`job-list-filters`)
   - Search navigation (Enter submits once, then cycles highlights)
   - Event-delegated row click/hover handlers

4. **Created `entrypoints/job_form_partial.js`** - Extracted from `_job_form_partial.html`
   - After-request orchestration (replaced inline `hx-on::after-request`)
   - Required-field validation interceptor
   - Print flow (save-then-print + iframe)
   - Status update / delete actions via event delegation
   - Recurrence end-mode toggle

5. **Created `entrypoints/panel_shell.js`** - Extracted from `includes/panel.html`
   - Panel resize handles (right, bottom, corner)
   - Persistence to localStorage (`gts-panel-width`, `gts-panel-height`)
   - HTMX refresh binding

**Template changes**:
- `calendar.html`: Keeps only `window.calendarConfig = {...}` inline
- `job_list.html`: Has only tiny config object (`window.jobListConfig`)
- `_job_form_partial.html`: Uses `data-gts-job-form="1"` marker, minimal inline init
- `includes/panel.html`: No inline JS

**Files created**:
- `rental_scheduler/static/rental_scheduler/js/gts_init.js`
- `rental_scheduler/static/rental_scheduler/js/entrypoints/calendar_page.js`
- `rental_scheduler/static/rental_scheduler/js/entrypoints/jobs_list_page.js`
- `rental_scheduler/static/rental_scheduler/js/entrypoints/job_form_partial.js`
- `rental_scheduler/static/rental_scheduler/js/entrypoints/panel_shell.js`

Definition of Done:
- ✅ Template scripts are tiny (mostly `window.calendarConfig = ...` only).
- ✅ No duplicate handlers after repeated open/close/swap actions (idempotent init).

---

### Phase 2 — Create a shared “frontend library” module folder
**Goal**: stop duplicating helpers.

Create shared modules (even without a bundler, we can do plain JS files loaded in order):
- `shared/csrf.js` (single CSRF getter)
- `shared/toast.js` (wrap `window.showToast`)
- `shared/storage.js` (namespaced localStorage helpers)
- `shared/dom.js` (safe event binding, delegation helpers)
- `shared/html_state.js` (serialize/sanitize draft HTML)

Definition of Done:
- Panel + workspace use the same serialize/sanitize code.
- Calendar/panel/workspace use the same CSRF/toast helpers.

---

### Phase 3 — Split `job_calendar.js` into logical modules (keep `window.jobCalendar`)
**Goal**: keep all features, but make the code navigable.

Target decomposition (example):
- `calendar/core.js` (FullCalendar init + event fetch)
- `calendar/toolbar.js` (custom toolbar controls)
- `calendar/today_sidebar.js`
- `calendar/tooltips.js`
- `calendar/search_panel.js`
- `calendar/recurrence_virtual.js`
- `calendar/call_reminders.js`

Keep a thin wrapper that constructs `window.jobCalendar = new JobCalendar()` so external callers don’t break.

Definition of Done:
- `job_calendar.js` is mostly glue; features live in modules.

---

### Phase 4 — Panel cleanup (choose one implementation)
**Goal**: one panel implementation, one state store.

- Decide whether Alpine is truly supported. If not:
  - remove Alpine compatibility paths from `panel.js`
  - remove leftover `x-data` usage or load Alpine intentionally
- Consolidate panel persistence:
  - pick **one**: `jobPanelState` OR `gts-panel-width/height` (prefer a single structured key)
  - move resize logic into `panel.js` (not in template)

Definition of Done:
- One codepath for panel behavior.
- One place to change panel persistence.

---

### Phase 5 — Make URL usage consistent (stop hard-coded endpoints)
**Goal**: URLs come from Django or one config object.

- Prefer Django-injected URLs in `window.calendarConfig` for calendar-related endpoints.
- For other pages, prefer adding small `data-*` attributes with URLs or injecting a `window.urls` object.
- Remove hard-coded `/rental_scheduler/...` style paths.

Definition of Done:
- No hard-coded app-prefix URLs in JS.

---

### Phase 6 — Replace HTML scraping with partial endpoints (keep UX identical)
**Goal**: remove `fetch('/jobs/?...') + DOMParser` patterns.

- Create/route a server endpoint that returns only the job table fragment.
- Calendar search panel should request that fragment directly.

Definition of Done:
- Search results are fetched as a purpose-built partial.

---

### Phase 7 — Tooling (format + lint + optional bundler)
**Goal**: prevent drift from reappearing.

- Add formatting (Prettier) and basic linting (ESLint) for `static/rental_scheduler/js/*`.
- Optional: move to Vite for module bundling once modules exist.

Definition of Done:
- Consistent formatting; PR diffs are readable.

---

## Suggested target file layout (incremental)

- `rental_scheduler/static/rental_scheduler/js/`
  - `shared/`
  - `calendar/`
  - `panel/`
  - `workspace/`
  - `entrypoints/`
    - `calendar_page.js` (loaded only by `calendar.html`)
    - `jobs_list_page.js` (loaded only by `job_list.html`)

Keep `panel.js` + `workspace.js` facades initially, then shrink them to wrappers after modules exist.

---

## Appendix A — LocalStorage key catalog

### Calendar
- `gts-calendar-search-open`
- `gts-calendar-today-sidebar-open`
- `gts-sidebar-width`
- `gts-calendar-current-date`
- `gts-calendar-filters`
- `gts-selected-calendars`
- `gts-default-calendar`
- `cal-events-cache:*` (per-view cached event payloads)

### Panel
- `jobPanelState`
- `gts-panel-width`
- `gts-panel-height`
- `gts-job-initial-save-attempted:*`

### Workspace
- `gts-job-workspace`

### Job list
- `job-list-filters`

---

## Appendix B — Key endpoints (frontend-relevant)

### Calendar
- `GET /api/job-calendar-data/`

### Job panel partials
- `GET /jobs/new/partial/` (supports `?date=` and `?edit=`)
- `POST /jobs/new/submit/`

### Job API
- `GET /api/jobs/<pk>/detail/`
- `POST /api/jobs/<job_id>/update-status/`
- `POST /api/jobs/<job_id>/delete/`

### Recurrence
- `POST /api/recurrence/materialize/`

### Call reminders
- `POST /api/jobs/<job_id>/mark-call-reminder-complete/`
- `POST /jobs/<job_id>/call-reminder/update/`
- `POST /call-reminders/<pk>/update/`
- `POST /call-reminders/<pk>/delete/`

---

## Appendix C — Existing test safety net
- Playwright smoke tests: `tests/e2e/test_calendar_smoke.py`

Recommended additions:
- “minimize → tab appears → restore → save”
- “draft persists across reload”
- “virtual occurrence materialize opens job”
- “call reminder update/delete reflected on calendar”



---

## Detailed execution plan — First implementation phase (Sprint 1): Phase 0 + Phase 1

This is the **first “do real work” phase** intended to be safe to ship incrementally. It combines:
- **Phase 0 (Safety net)**: make regressions obvious.
- **Phase 1 (Extract inline JS)**: remove the biggest “hidden coupling” vector (template scripts that re-run on swaps).

### Goals (Sprint 1)
- **Lock in a refactor safety net** (manual checklist + Playwright coverage) so later changes are lower risk.
- **Remove large inline JS from templates** and place it into dedicated static files, without changing UX.
- **Make initialization idempotent** so HTMX swaps don’t double-bind handlers.

### Non-goals (explicitly out of scope for Sprint 1)
- No new UI, no redesign, no “cleanups for style”.
- No refactor of `job_calendar.js` internals (that’s Phase 3).
- No consolidation of storage keys / state stores (that’s Phase 4).
- No deduping CSRF/toast/storage helpers (that’s Phase 2).
- No endpoint/contract changes (that’s Phase 6 / backend changes).

### Sprint 1 Definition of Done
- **Templates contain no large inline `<script>` blocks**:
  - `calendar.html` keeps only `window.calendarConfig = {...}` (and any other *tiny* JSON/config needed).
  - `jobs/job_list.html` keeps **zero** inline JS (or at most a tiny config object).
  - `jobs/_job_form_partial.html` keeps **zero** inline JS (or at most tiny config).
  - `includes/panel.html` keeps **zero** inline JS (recommended; see optional item below).
- **No duplicate event handlers** after:
  - opening/closing jobs repeatedly
  - switching workspace tabs repeatedly
  - swapping job form partial repeatedly via panel load
- **Playwright + manual smoke flows pass** (see below).

---

## Work breakdown (ordered, shippable increments)

### 0A) Phase 0 — Safety net (do this first)

- **0A.1: Write a manual smoke checklist** (keep it in this doc or a short separate note):
  - Calendar loads and renders 4-week view
  - Toggle Today sidebar open/close; width persists
  - Multi-calendar selection persists
  - Search panel open/close persists; search returns results
  - Click calendar event → opens job in panel; minimize → workspace tab appears; switch tabs
  - Unsaved changes: edit field → switch jobs → expected autosave/draft behavior
  - Draft survives reload; restore draft works
  - Print from panel works (save-then-print + iframe flow)
  - Call reminder: create/edit/delete/complete reflected in UI/calendar
  - Virtual recurring occurrence click materializes then opens job

- **0A.2: Ensure the existing Playwright smoke test runs locally**
  - Run `tests/e2e/test_calendar_smoke.py` before and after each extraction PR.

- **0A.3: Add 1–3 Playwright tests that specifically protect Phase 1 changes**
  - “job form partial swapped twice does not double-bind” (assert only one submit happens / only one toast / only one handler outcome).
  - “job list keyboard navigation still works” (Enter cycles highlights).
  - “search panel fetch still populates results and clicking row opens panel”.

Deliverable: we can say “green” with confidence before changing behavior in later phases.

---

### 1A) Establish a standard init pattern (prevents double-binding)

We need a consistent way to run code both:
- on full page load (`DOMContentLoaded`)
- after HTMX swaps (`htmx:load`, `htmx:afterSwap`)

Plan:
- **Create a tiny shared helper** (even before Phase 2) to support idempotent init:
  - `initOnce(key, fn)` (global map or `window.__gtsInitFlags`)
  - `markInitialized(el, attr = "data-gts-init")` and `isInitialized(el, ...)`
  - `onHtmxLoad(fn)` wrapper for `document.body.addEventListener('htmx:load', ...)`
- **Prefer event delegation** (`document.body.addEventListener('click', ...)`) for click/hover behaviors tied to swapped content.
- **When delegation isn’t feasible** (mouse drag resizers), use a single global binding guarded by `initOnce`.

Deliverable: a repeatable pattern we use for every extraction so future work doesn’t regress.

---

### 1B) Phase 1 — Extract `calendar.html` inline JS (keep `window.calendarConfig` inline)

Current inline responsibilities to extract:
- Sidebar resize (persist `gts-sidebar-width`)
- Search panel behaviors (open/close, form submit)
- Search results fetch + DOMParser extraction of `#job-table-container`
- Keyboard navigation + row click-to-open panel

Plan:
- **1B.1: Split config vs behavior**
  - Leave only `window.calendarConfig = {...}` inline in `calendar.html`.
  - Move everything else into a dedicated static file loaded by `calendar.html`.

- **1B.2: Create a page entrypoint script**
  - Suggested: `rental_scheduler/static/rental_scheduler/js/entrypoints/calendar_page.js`
  - Expose one callable initializer (e.g. `window.GTS.initCalendarPage()`), or run an IIFE guarded by `initOnce('calendar_page', ...)`.

- **1B.3: Provide the minimum template-provided inputs**
  - If the extracted code needs URLs currently created via template tags, expose them via:
    - `window.calendarConfig` (preferred), or
    - `data-*` attributes on a known element (`#calendar-shell`)
  - Keep this tiny and explicit; don’t embed logic inline again.

- **1B.4: Idempotency requirements**
  - Drag handlers for sidebar resize must be bound exactly once.
  - Search “row click” must use delegation (or must rebind only after results are replaced).

Acceptance checks:
- Sidebar width persists across reload.
- Search results still load and remain clickable; keyboard navigation still works.
- No duplicate click handlers after running the search multiple times.

---

### 1C) Phase 1 — Extract `jobs/job_list.html` inline JS

Current inline responsibilities to extract:
- Calendar dropdown open/close; selected text updates
- Date filter radios + custom date range visibility
- Persist filters to `job-list-filters`
- Search input “Enter submits once, then cycles highlights”
- Row click-to-open JobPanel + hover feedback

Plan:
- **1C.1: Create a page entrypoint**
  - Suggested: `rental_scheduler/static/rental_scheduler/js/entrypoints/jobs_list_page.js`
  - Run on `DOMContentLoaded`, plus be resilient if job table is replaced (future Phase 6).

- **1C.2: Inject only the needed server URLs**
  - For “open job in panel”, the script needs `job_create_partial` URL.
  - Provide it via a tiny inline config (`window.jobListConfig = {...}`) or a `data-job-create-url` attribute.

- **1C.3: Switch to event delegation for row clicks/hover**
  - Avoid binding per-row listeners that become stale after future swaps.

Acceptance checks:
- Dropdown works; closes on outside click.
- Filters persist to localStorage.
- Enter behavior works exactly as before.
- Clicking a row opens panel for that job.

---

### 1D) Phase 1 — Extract `jobs/_job_form_partial.html` inline JS (most sensitive)

Current inline responsibilities to extract:
- Calendar select cloning into panel header and syncing values
- Toggle wiring (all-day, call reminder, recurrence, recurrence end mode)
- Print system (save-then-print + iframe)
- Status update/delete helpers + button handlers
- Form change tracking init
- HTMX required-field validation interceptor
- The `hx-on::after-request="..."` orchestration string on the `<form>`

Plan:
- **1D.1: Move behavior into a dedicated “partial controller” script**
  - Suggested: `rental_scheduler/static/rental_scheduler/js/entrypoints/job_form_partial.js`
  - This script should **not assume DOMContentLoaded**; it should initialize whenever the partial is swapped into the panel.

- **1D.2: Replace inline `hx-on::after-request="..."`**
  - Bind a scoped `htmx:afterRequest` handler that only runs for this form and only on successful submit.
  - Preserve the existing orchestration (clear unsaved, close panel/tab, refetch calendar).

- **1D.3: Initialization strategy**
  - Provide `initJobFormPartial(rootEl)` that:
    - clones/syncs the calendar selector
    - wires toggles
    - ensures required-field validation is bound once
    - ensures print handler is bound once globally (delegation)
    - re-invokes `JobPanel.trackFormChanges()` safely
  - Call it from:
    - `htmx:load` (when content is inserted), and/or
    - the panel loader hook in `panel.js` after it swaps content.

- **1D.4: Preserve existing behavior exactly**
  - Keep the same localStorage keys and global flags for now.
  - Keep the same skip-validation contract (`JobPanel.isSwitchingJobs`) for programmatic saves.

Acceptance checks:
- Opening job form multiple times does not create multiple print handlers or multiple validation interceptors.
- Save behavior unchanged; panel/workspace closes as before.
- Print flow still triggers print reliably.

---

### 1E) Recommended add-on: extract `includes/panel.html` inline JS (keeps templates “tiny”)

Even though Phase 4 will *consolidate* panel resize state, **we can still move the existing resize code out of the template now** with no behavioral change.

Current inline responsibilities to extract:
- `htmx:load` “refresh” binding for `.panel-body`
- Panel resize handles + persistence to `gts-panel-width` / `gts-panel-height`

Plan:
- Create `rental_scheduler/static/rental_scheduler/js/entrypoints/panel_shell.js` (or fold into `panel.js` temporarily).
- Keep storage keys exactly as-is for Sprint 1.
- Ensure it binds once globally (guarded by `initOnce`).

Acceptance checks:
- Panel resize still works; dimensions persist.
- No duplicate “refresh” listeners after HTMX activity.

---

## Rollout strategy (how we ship safely)

- **One template at a time**: land calendar extraction, then job list, then job form partial (largest risk).
- **Keep PRs small and reversible**:
  - each PR should be “move code + wire script tag/config + tests”
  - avoid “drive-by refactors” while moving code
- **Always verify idempotency** by manually doing the same action multiple times (open/close/swap/search).

---

## Phase 2+ follow-ups enabled by Sprint 1

Once Phase 1 is complete, we can:
- Create `shared/` helpers (CSRF/toast/storage/dom) and remove duplicates (Phase 2).
- Split `job_calendar.js` cleanly because calendar behaviors won’t be mixed with template scripts (Phase 3).
- Consolidate panel resize + state persistence (Phase 4).

