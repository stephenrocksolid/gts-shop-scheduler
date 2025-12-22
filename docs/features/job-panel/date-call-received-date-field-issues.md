# Date fields in New Job panel: duplication + “Date Call Received” disappearing

## Context

The New Job panel enhances date inputs using **flatpickr** with `altInput:true` for a friendly display format (e.g., “Jan 5, 2026”) while submitting ISO values (`YYYY-MM-DD`).

This interacts with:

- **HTMX swaps/lifecycle events** (panel HTML is swapped in/out)
- **Draft minimize/restore** (panel HTML is serialized and later restored)

Related background doc: `docs/features/job-panel/draft-minimize-restore.md`

## Symptoms

- **Duplicate date inputs** were observed (2× “Date Call Received”, sometimes 2× Start/End)
- After changes meant to remove duplicates, **“Date Call Received” can appear missing**: the label renders but the input area is blank.

## Where the field is rendered

The Date Call Received input is rendered directly in the job form partial:

- Template: `rental_scheduler/templates/rental_scheduler/jobs/_job_form_partial.html`
  - Uses an `<input type="date" name="date_call_received" ...>` with inline styles.

The model field is a `DateTimeField` but the form accepts date-only input formats:

- Form: `rental_scheduler/forms.py` (`JobForm.date_call_received`)

## Root cause (why it duplicates, and why it can disappear)

### Flatpickr `altInput:true` creates **two** inputs

With `altInput:true`, flatpickr:

- Creates a **visible** “alt” input for display
- Hides the **original** input (typically `type="hidden"`) for submission

So the correct state is:

- Original input exists but may be hidden
- Alt input exists and is visible

### The bug: cleanup removed the visible alt input even when flatpickr was already live

`initPanelDatePickers()` in `rental_scheduler/static/rental_scheduler/js/panel.js` previously performed **alt-input cleanup unconditionally**, before checking whether the input already had a **live** `_flatpickr` instance.

This becomes a problem when `initPanelDatePickers()` runs more than once (which happens in practice due to:

- `htmx:afterSwap` handler calling `initPanelDatePickers()`
- `htmx:load` handler calling `initPanelDatePickers()`
- Any subsequent HTMX partial updates inside the panel
)

On the **second** run:

1. Cleanup removes `.gts-flatpickr-alt` (the visible input)
2. The function then detects a live `_flatpickr` instance and returns early
3. The original input is still hidden (because flatpickr expects its alt input to exist)
4. Result: the UI shows **no visible input** → “Date Call Received” appears to disappear

This also explains the “it duplicated, then one disappeared” progression:

- Duplication: restored/cached DOM included an old alt input and re-init created a new one
- Disappearance: later cleanup removed the alt input without re-creating it

## Fix implemented (idempotent init + self-heal)

`initPanelDatePickers()` was updated so that:

- It **does not remove** alt inputs when there is a **live** flatpickr instance with a connected alt input
- Cleanup of stale alt inputs only happens when we are about to **(re)initialize** an input
- If a live instance exists but its `altInput` is missing (detected via `alt.isConnected === false`), the code **destroys and re-initializes** flatpickr as a self-heal

Code: `rental_scheduler/static/rental_scheduler/js/panel.js` (`initPanelDatePickers()`)

## Regression test added

A Playwright E2E test now asserts that **Date Call Received stays visible** even if `htmx:load` fires again (simulating the “second init” scenario).

Test: `tests/e2e/test_calendar_smoke.py`

## Plan (bigger-picture, more robust approach)

The current approach works, but the surface area is large because we mix:

- DOM caching/restoration (draft HTML)
- third-party DOM mutation (flatpickr alt inputs)
- repeated initialization (HTMX lifecycle events)

If this continues to be a source of regressions, the most robust “think big” approach is:

1. **Stop storing draft state as raw HTML** (store JSON instead)
   - Store a minimal payload: `{fieldName: value}` (+ checkbox/select state)
   - On restore: fetch a fresh form partial (server-rendered), then apply values
   - Then run init routines once
2. Introduce a single **“panel controller”** (or small set of controllers) that owns:
   - Date input init
   - Schedule picker init
   - Cleanup on close/minimize
   - Idempotent re-init on HTMX swaps
3. Consolidate cleanup logic to a single “source of truth”
   - Prefer `window.GtsDateInputs.stripFlatpickrArtifacts()` for structural cleanup
   - Avoid ad-hoc “remove siblings” patterns except when narrowly scoped to one input

### Incremental rollout plan

- **Step 1**: Keep the current HTML-draft mechanism, but ensure all init routines are idempotent and never “half clean up” live widgets.
- **Step 2**: Add targeted E2E regression tests for:
  - Date Call Received visibility on open
  - Visibility after minimize → restore
  - No duplicate visible inputs after restore
- **Step 3**: (Optional) migrate draft persistence from HTML → JSON field-state; keep the UI identical.

## Questions (to confirm exact reproduction)

- Does “Date Call Received” disappear **immediately on panel open**, or only after **minimize/restore**, or after toggling **recurrence/call reminder**?
- Are you seeing this only on the calendar page, or also when opening the panel from other pages?
- Any browser-specific reports (Chrome vs Firefox), or is it consistent across browsers?


