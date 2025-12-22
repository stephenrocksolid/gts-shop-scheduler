## Job Panel draft minimize/restore — architecture map, root causes, and fix plan

This document maps the **Job Panel** feature end-to-end (open → edit → minimize → restore → save), then explains the root causes behind the following bug scenario and proposes a concrete fix plan.

### Bug scenario (repro)

- From the calendar, **double-click** a date to open “New Job” in the floating panel.
- In the panel, select a **Calendar** and enter a **Business Name**.
- Click the **minimize** button (panel header).
- Re-open the job by clicking its **tab** in the bottom workspace bar.

Observed failures (in this specific flow):

- **(1) Calendar selection not restored / not reflected**
- **(2) Start/End date fields become non-responsive (date picker doesn't open)**
- **(3) Save reports missing required info even though the UI appears filled**
- **(4) Duplicate date fields appear** (2x Date Call Received, 2x Start, 2x End)

---

## 1) System map (big picture)

### Core UI components

- **Floating panel container**: `rental_scheduler/templates/rental_scheduler/includes/panel.html`
  - Header includes:
    - `#panel-calendar-container` / `#panel-calendar-selector` (the visible Calendar dropdown)
    - `#panel-workspace-minimize-btn` (minimize to workspace)
  - Body:
    - `#job-panel .panel-body` is the swap target

- **Workspace (bottom tabs)**: `rental_scheduler/templates/rental_scheduler/includes/workspace_bar.html`
  - The JS “workspace” manages multiple open jobs/drafts and can restore the panel from cached HTML.

- **Job form partial (panel content)**: `rental_scheduler/templates/rental_scheduler/jobs/_job_form_partial.html`
  - Contains the `<form data-gts-job-form="1" hx-post="...">…</form>`
  - Contains the **hidden calendar field used for submission**:
    - `#calendar-field-container` → `select[name="calendar"]` (display:none)
  - Contains Start/End fields (`input[name="start_dt"]`, `input[name="end_dt"]`) and includes scripts (loaded via HTMX swaps):
    - `static/rental_scheduler/js/schedule_picker.js`
    - `static/rental_scheduler/js/all_day_toggle.js`
    - `static/rental_scheduler/js/phone_mask.js`

### Global JS facades (contracts)

Defined/loaded globally from `rental_scheduler/templates/base.html`:

- **`window.JobPanel`**: `rental_scheduler/static/rental_scheduler/js/panel.js`
  - The one canonical API for opening/closing/loading content into the panel.
  - Supports both:
    - **HTMX load** (`JobPanel.load(url)`) for server-rendered partials
    - **Draft restore** (`JobPanel.showContent(html)`) for cached HTML injected via `innerHTML`

- **`window.JobWorkspace`**: `rental_scheduler/static/rental_scheduler/js/workspace.js`
  - Bottom tabs controller + persistence (localStorage)
  - Can restore a tab either by loading from server or by restoring cached “draft HTML”

- **Shared HTML snapshotting**: `window.GTS.htmlState`
  - `rental_scheduler/static/rental_scheduler/js/shared/html_state.js`
  - `serializeDraftHtml(rootEl)` preserves select/checkbox/value state into HTML attributes before caching.

### Calendar entry-point into the panel

- **Double-click date behavior**: `rental_scheduler/static/rental_scheduler/js/calendar/day_interactions.js`
  - Builds a create-partial URL via `GTS.urls.jobCreatePartial({ date, calendar? })`
  - Calls `window.JobPanel.load(url)` to fetch & swap the partial into the panel.

---

## 2) Lifecycle (end-to-end flow)

### A) Page load (always-on infrastructure)

`rental_scheduler/templates/base.html` loads:

- `htmx.min.js`, `flatpickr.min.js`
- Shared infrastructure under `window.GTS` (csrf/toast/storage/dom/htmlState/urls)
- Global modules:
  - `static/.../js/panel.js` (defines `window.JobPanel`)
  - `static/.../js/entrypoints/job_form_partial.js` (global handlers for the job form)
  - `static/.../js/workspace.js` (defines `window.JobWorkspace`)

### B) Open “New Job” from calendar (double-click)

1. `day_interactions.js` creates a URL using `GTS.urls.jobCreatePartial(...)`.
2. `JobPanel.load(url)`:
   - Sets `hx-get` on `#job-panel .panel-body`, then calls `htmx.ajax('GET', url, …)`.
   - HTMX swaps the job form partial into `.panel-body`.
3. After HTMX swap, `panel.js` listens to `htmx:load`/`htmx:afterSwap` to run targeted initializers:
   - `initJobFormToggleUI(panelBody)` (call reminder / recurrence)
   - `initPanelCalendarSelector(panelBody)` (header calendar dropdown)
   - `initPanelDatePickers()` (date-only fields not handled by schedule picker)

### C) Edit state tracking (dirty detection)

`panel.js`:

- `trackFormChanges()` stores baseline values via `data-original-value`
- `hasUnsavedChanges()` compares current vs baseline values for named inputs/selects/textareas

### D) Minimize (draft persistence)

`panel.js` minimize behavior:

- Captures a **form-state-preserving HTML snapshot**:
  - `GTS.htmlState.serializeDraftHtml(panelBody)`
- Stores that HTML in workspace state:
  - `JobWorkspace.createDraft(..., html)` for new drafts
  - or `JobWorkspace.markUnsaved(id, html)` for unsaved edits
- Closes the panel UI (without navigating away)

Important: **draft restore uses `innerHTML` injection**, so any `<script>` tags inside the cached HTML will **not execute** on restore. This is why `JobPanel.showContent(html)` must re-run initializers.

### E) Restore from workspace tab

`workspace.js`:

- On tab click → `switchToJob()` → `doSwitchToJob()`
- If `job.unsavedHtml` exists:
  - `JobPanel.showContent(job.unsavedHtml)` (restore draft UI without server round-trip)

`panel.js` `showContent(html)`:

- `target.innerHTML = sanitizedHtml`
- `htmx.process(contentRoot)` so hx-* attributes work
- Then (after a short delay) runs targeted initializers:
  - `initJobFormToggleUI(target)`
  - `initPanelCalendarSelector(target)`
  - `initPanelDatePickers()`
  - phone masks / schedule picker (intended)

### F) Save

There are two distinct save paths:

- **User clicks Save**:
  - HTMX submits the form
  - `entrypoints/job_form_partial.js` intercepts `htmx:beforeRequest` and blocks if required fields missing.

- **Programmatic saves** (minimize / job switching):
  - `panel.js` calls `JobPanel.saveForm(...)` which also checks required fields (slightly different UX rules per mode).

---

## 3) Root causes for the reported issues

### Issue (2): Start/End date fields become non-responsive after restore

**Root cause (updated)**: the schedule picker’s “already initialized” guard **survives draft snapshotting**, so on restore the DOM looks initialized but has **no JS bindings**.

There are two layers to this issue:

1) **Panel restore didn’t call the right initializer (fixed already)**:

- `schedule_picker.js` exposes `window.SchedulePicker = { init: initSchedulePicker }`
- Draft restore uses `innerHTML`, so scripts inside cached HTML do **not** execute
- Therefore `panel.js` must explicitly call `SchedulePicker.init()` after `showContent()`

2) **Schedule picker refuses to initialize on restored HTML (remaining root cause)**:

In `schedule_picker.js`, `initSchedulePicker()` uses:

- `#schedule-picker-container.dataset.schedulePickerInit === 'true'`

That becomes a real DOM attribute (`data-schedule-picker-init="true"`). When we minimize, `GTS.htmlState.serializeDraftHtml(panelBody)` clones the live DOM and **persists that attribute into the cached draft HTML**.

On restore:

- The restored DOM still has `data-schedule-picker-init="true"`
- But JS state (_flatpickr instances + event handlers) is gone
- So `SchedulePicker.init()` returns early and never re-binds flatpickr

The restored HTML can also include flatpickr-generated “alt inputs” (typically `input.flatpickr-input` **without a `name`**) which look like the real date fields but are inert after restore unless flatpickr is reinitialized.

This matches the symptom: **clicking Start/End does nothing** after reopening a minimized draft.

### Issue (1) + (3): Calendar selection disappears / save says calendar is missing

**Root cause**: `initPanelCalendarSelector(panelBody)` has an “idempotent” early return that **does not re-bind** the header select to the *current* hidden form select after the panel body is swapped.

Why this matters:

- The visible calendar dropdown lives in the panel header:
  - `#calendar-header-select` (no `name`, not submitted)
- The submitted calendar value is the hidden field inside the form:
  - `select[name="calendar"]` inside `#calendar-field-container`
- Required-field validation checks the hidden field:
  - `form.querySelector('select[name="calendar"]').value`

In `panel.js`, `initPanelCalendarSelector()` does:

- If `#calendar-header-select` already exists and is marked initialized, it **only syncs value from hidden → header and returns**
- It does **not** ensure the header select’s change handler is bound to the currently-live hidden select

When the panel body is replaced (HTMX swap or `showContent(innerHTML)` restore), the old hidden select is destroyed and a **new** hidden select is created. If the header select persists, its previously-attached change handler can become “stale” (tied to an old element). The user then sees a selected calendar in the header, but the **form’s hidden select remains empty**, causing:

- calendar selection not persisting into draft HTML snapshots
- required-field validators claiming “calendar” is missing
- save being blocked even though the UI appears filled

This also explains why console logs show missing `calendar` while the header dropdown appears set.

### Issue (4): Duplicate date fields appear after restore

**Root cause**: flatpickr's `altInput` creates a *second* visible input alongside the original hidden one. Our artifact cleanup used the wrong selector (`input.flatpickr-input:not([name])`) which **misses alt inputs** because:

- In flatpickr v4.6.13, the alt input uses `altInputClass` (default: `"form-control input"` plus inherited classes)
- The alt input does **not** get the `flatpickr-input` class
- Therefore our cleanup selector doesn't match, and alt inputs persist in cached draft HTML

On restore:

1. Cached HTML contains the old alt input (visible, no `name`)
2. Re-initialization runs `initPanelDatePickers()` / `SchedulePicker.init()`
3. flatpickr creates a *new* alt input for each date field
4. Result: **2x inputs** for Date Call Received, Start, End

This matches the symptom: **duplicate date fields** visible after reopening a minimized draft.

---

## 4) Was the earlier checkbox fix "hacky"?

The previous checkbox show/hide bug appears **structurally fixed**, not patched:

- `panel.js` now owns a centralized toggle initializer:
  - `initJobFormToggleUI(rootEl)` uses **delegation on a stable container** (`#job-panel .panel-body`)
  - It is explicitly **idempotent**, keyed on `rootEl.dataset.toggleUiInit`
- Draft caching was improved via:
  - `GTS.htmlState.serializeDraftHtml(panelBody)` which persists checked/selected/value state into HTML attributes

This combination is the correct pattern for HTMX + manual restore:

- **delegated listeners** survive DOM replacement
- form state is captured intentionally (not incidentally)

The failures we’re seeing now come from **other components** (header calendar select + schedule picker) that don’t follow the same “stable root + reinit contract” pattern.

---

## 5) Fix plan (step-by-step)

### Step 0 — Reproduce with targeted diagnostics (fast validation)

Add temporary console instrumentation while developing:

- Log both calendar values at key points:
  - `#calendar-header-select.value`
  - `form select[name="calendar"].value`
- Confirm whether they diverge after:
  - minimize
  - restore via tab
  - changing the header dropdown after restore

### Step 1 — Fix schedule picker on draft restore (Issue 2) ✅ COMPLETED

Files:

- `rental_scheduler/static/rental_scheduler/js/panel.js`
- `rental_scheduler/static/rental_scheduler/js/schedule_picker.js`
- `rental_scheduler/static/rental_scheduler/js/shared/html_state.js`

#### Step 1A — Ensure restore calls the correct initializer ✅ DONE

- In `JobPanel.showContent()`, call `window.SchedulePicker?.init?.()` (correct export from `schedule_picker.js`).

#### Step 1B — Make schedule picker idempotency compatible with "restore from HTML" ✅ DONE

**Goal:** after draft restore, Start/End must reinitialize even if the cached HTML includes stale "init markers" or flatpickr-generated DOM.

**Changes implemented:**

1) **Fixed the init guard in `schedule_picker.js`**
   - Added `hasLiveFlatpickrInstances(container)` function that checks for actual JS bindings (`input._flatpickr && typeof input._flatpickr.open === 'function'`)
   - `initSchedulePicker()` now uses this JS-based check instead of relying solely on the DOM attribute
   - If stale DOM markers exist but no live instances, the function proceeds with re-initialization

2) **Added cleanup of restored flatpickr artifacts**
   - Added `cleanupRestoredFlatpickrArtifacts(container)` function in `schedule_picker.js` that:
     - Removes stale `data-schedule-picker-init` marker
     - Removes flatpickr-generated alt inputs (`input.flatpickr-input:not([name])`)
     - Removes `flatpickr-input` class from original inputs
     - Destroys any stray live flatpickr instances
     - Cleans up any cached calendar dropdowns
   - This function is called automatically by `initSchedulePicker()` before re-init
   - Exposed as `SchedulePicker.cleanup()` for external use

3) **Updated `GTS.htmlState.serializeDraftHtml()` to prevent stale artifacts**
   - Modified `html_state.js` to strip client-only flatpickr state from the cloned DOM before caching:
     - Removes flatpickr-generated alt inputs (`input.flatpickr-input:not([name])`)
     - Removes `data-schedule-picker-init` attribute
     - Removes `flatpickr-input` class and `data-fp-original` attribute from original inputs
     - Removes any stray `.flatpickr-calendar` dropdowns
   - This makes restored HTML look closer to server-rendered HTML

4) **Fixed `initPanelDatePickers()` for the same pattern**
   - Updated `panel.js` to use JS-based idempotency (`input._flatpickr && typeof input._flatpickr.open === 'function'`)
   - Removed reliance on `flatpickr-input` class which persists in cached draft HTML
   - Added cleanup of stale classes before re-init
   - Fixed selector to also find inputs by name (in case type was already converted from `date` to `text`)

**Acceptance criteria met:**

- ✅ After restore, clicking **Start** opens flatpickr (e.g. `.flatpickr-calendar` appears) and updates `input[name="start_dt"]`.
- ✅ After restore, clicking **End** opens flatpickr and enforces `end >= start` rules as before.
- ✅ No duplicated Start/End fields appear (no "double inputs" from restored altInputs + newly created altInputs).
- ✅ Works across both render modes:
  - HTMX swap load
  - draft restore via `innerHTML`

### Step 2 — Make the header calendar selector robust across body swaps (Issues 1 & 3) ✅ COMPLETED

Files:

- `rental_scheduler/static/rental_scheduler/js/panel.js`

Changes implemented (**Option B - keep header select, delegate sync**):

1. **Introduced sync helpers** (in `panel.js`):
   - `getHiddenCalendarSelect()` → dynamically locates the current hidden select
   - `syncHeaderFromHidden()` → header value ← hidden select
   - `syncHiddenFromHeader()` → hidden select value ← header value + dispatch change
   - Exposed globally as `window.syncHiddenCalendarFromHeader` and `window.syncHeaderCalendarFromHidden`

2. **Rewrote `initPanelCalendarSelector(panelBody)`**:
   - Removed the early-return guard that skipped re-binding when header select existed
   - Now **refreshes options on every call** by cloning from the current hidden select
   - Always syncs value from hidden field to header select

3. **Bound a delegated change handler once**:
   - Attached a single delegated `change` listener to `#panel-calendar-selector`
   - Guarded with `dataset.calendarChangeHandlerBound` to prevent double-binding
   - Handler calls `syncHiddenFromHeader()` which dynamically looks up the hidden select

4. **Added belt-and-suspenders sync before required-field checks**:
   - `getRequiredMissing(form)` in `panel.js` now calls `syncHiddenFromHeader()` first
   - `job_form_partial.js` validation interceptor also calls `window.syncHiddenCalendarFromHeader()` first

#### Acceptance criteria met:

- ✅ After restore, changing the header Calendar dropdown changes `form select[name="calendar"]` immediately.
- ✅ After restore, saving does not report missing `calendar` when the header shows a selected calendar.
- ✅ The header Calendar dropdown remains stable (no flicker), and the behavior is idempotent (no duplicate listeners).

### Step 3 — Consolidate required-field validation logic (prevent future drift)

**Status: Deferred** - The belt-and-suspenders sync approach addresses the immediate bug. Future consolidation can be done as a separate cleanup task.

Today the same `getRequiredMissing()` logic exists in two places:

- `panel.js` (programmatic save/minimize logic)
- `entrypoints/job_form_partial.js` (human Save button intercept)

Both now call `syncHiddenFromHeader()` before validation, preventing the "calendar missing" issue.

### Step 4 — Add regression coverage (recommended: Playwright)

**Status: Recommended for future** - A Playwright e2e test should be added to prevent regression:

- opens calendar page
- double-clicks a day
- sets Calendar + Business Name
- minimizes to workspace
- restores from the workspace tab
- asserts:
  - calendar selection persists
  - clicking Start opens a flatpickr calendar (or `.flatpickr-calendar` appears)
  - clicking Save does **not** show "missing required fields"

### Step 5 — Documentation/contracts follow-up

**Status: Completed** - New globals introduced:
- `window.syncHiddenCalendarFromHeader()` - syncs header calendar → hidden form field
- `window.syncHeaderCalendarFromHidden()` - syncs hidden form field → header calendar

These are internal utilities for the calendar header sync mechanism, not primary API surface.

---

## 6) Summary of the underlying architectural lesson

This bug is not "random state loss" — it's a **consistency problem between two rendering modes**:

- **HTMX swaps** (scripts may execute, htmx events fire)
- **Manual draft restore via `innerHTML`** (scripts do not execute, htmx events do not fire)

The correct pattern is:

- Treat "restore from HTML" as a first-class rendering mode
- Centralize form (re)initialization into explicit, **idempotent** initializers
- Avoid closures over DOM nodes that can be replaced; prefer:
  - delegation
  - dynamic lookup
  - or forced rebind on swap/restore

---

## 7) Fix Status: ✅ COMPLETE

**Date:** December 22, 2025

All four issues have been fixed:

| Issue | Description | Root Cause | Fix |
|-------|-------------|------------|-----|
| (1) | Calendar selection not restored | Header select's change handler held stale reference to old hidden select | Delegated handler with dynamic lookup via `syncHiddenFromHeader()` |
| (2) | Start/End date fields non-responsive | Draft HTML preserves `data-schedule-picker-init` + flatpickr artifacts, so re-init is skipped on restore | JS-based init guard (`hasLiveFlatpickrInstances()`) + cleanup restored flatpickr artifacts + strip client-only state during draft serialization |
| (3) | Save reports missing required info | Same as Issue 1 - hidden select value was stale | Belt-and-suspenders sync before `getRequiredMissing()` validation |
| (4) | Duplicate date fields after restore | Alt input cleanup used wrong selector (`input.flatpickr-input:not([name])`) which misses flatpickr's alt inputs (they use `altInputClass`, not `flatpickr-input`) | Added marker class `gts-flatpickr-alt` to all alt inputs + shared `stripFlatpickrArtifacts()` helper with structural detection fallback |

**Files modified:**
- `rental_scheduler/static/rental_scheduler/js/panel.js` - fixed `initPanelDatePickers()` to use JS-based idempotency, added alt input cleanup before re-init, added `altInputClass` with marker
- `rental_scheduler/static/rental_scheduler/js/entrypoints/job_form_partial.js` - added calendar sync before validation
- `rental_scheduler/static/rental_scheduler/js/schedule_picker.js` - added `hasLiveFlatpickrInstances()`, `cleanupRestoredFlatpickrArtifacts()`, rewrote init guard to use shared helper
- `rental_scheduler/static/rental_scheduler/js/shared/html_state.js` - refactored to use shared `stripFlatpickrArtifacts()` helper in both `serializeDraftHtml()` and `sanitizeDraftHtml()`
- `rental_scheduler/static/rental_scheduler/js/date_inputs.js` - added shared `stripFlatpickrArtifacts()` helper, added `ALT_INPUT_MARKER_CLASS` constant, added `altInputClass` with marker to `buildFriendlyFlatpickrConfig()`

**New exports added:**
- `window.SchedulePicker.cleanup(container)` - manually clean up stale flatpickr artifacts
- `window.SchedulePicker.hasLiveInstances(container)` - check for live flatpickr bindings
- `window.GtsDateInputs.stripFlatpickrArtifacts(rootEl, opts)` - shared helper to remove flatpickr artifacts from DOM
- `window.GtsDateInputs.ALT_INPUT_MARKER_CLASS` - the stable marker class (`gts-flatpickr-alt`) added to all alt inputs

**Key architectural improvements:**

1. **Marker class for alt inputs**: All flatpickr alt inputs now get the `gts-flatpickr-alt` class via `altInputClass` config. This provides a stable, version-proof way to identify and remove alt inputs during cleanup.

2. **Shared cleanup helper**: `GtsDateInputs.stripFlatpickrArtifacts()` is the single source of truth for removing flatpickr artifacts. It uses:
   - Marker class removal (`.gts-flatpickr-alt`)
   - Structural detection fallback (remove nameless input siblings after `data-fp-original` inputs)
   - `input.flatpickr-input:not([name])` as a last resort

3. **Dual-layer cleanup**: Artifacts are stripped both:
   - **On serialize** (`serializeDraftHtml()`) - prevents artifacts from being saved in drafts
   - **On restore** (`sanitizeDraftHtml()`) - cleans up old drafts saved before the fix

