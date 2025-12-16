## Context

Goal: **port only the valuable changes** from the archived WIP branch `origin/wip/steph-pre-sync-2025-12-16` (tip commit `834babd`) onto the now-updated `master`, without rebasing/merging huge rewritten UI files.

Working branch: `port/wip-2025-12-16` (tracks `origin/port/wip-2025-12-16`).

Guiding principles:
- Keep the WIP branch immutable (time capsule / rollback point)
- Port in small, reviewable slices (one “intent” per commit)
- Re-implement intent on top of today’s architecture instead of copying entire large files
- Don’t rewrite historical migrations; express schema/data intent as *new* migrations when needed

## Phase 0 (baseline) — status

- ✅ Created/checked out `port/wip-2025-12-16` from updated `master` (currently `17bd7f2`)
- ⏳ Baseline “green” verification (tests) should be re-run on this branch if not already captured

## Phase 1 (inventory) — results

### 1) What the WIP branch contains

- WIP head commit: `834babd` (“WIP: snapshot local changes before syncing with origin/master”)
- Common ancestor with updated master (merge-base): `35b4b55` (“Last updates”)
- The WIP branch is **exactly 1 commit** on top of the merge-base.

This matters because a naive `master..wip` diff includes lots of unrelated churn caused by master moving forward after `35b4b55`. The items below are the *WIP-only* changes we should evaluate for porting.

### 2) WIP-only changed files (35b4b55..834babd)

**Docs deleted (likely not valuable to re-apply):**
- `BUG_FIX_SUMMARY.md`
- `JSON_EXPORT_IMPORT_GUIDE.md`
- `JSON_EXPORT_IMPORT_IMPLEMENTATION_SUMMARY.md`
- `SERVER_FIX_CALL_REMINDERS.md`

**Whitespace/no-op changes (ignore):**
- `rental_scheduler/management/commands/fix_call_reminder_dates.py` (trailing newlines only)
- `rental_scheduler/migrations/0029_fix_call_reminder_dates.py` (trailing newlines only)
- `rental_scheduler/migrations/0030_add_callreminder_model.py` (trailing newlines only)
- `rental_scheduler/migrations/0034_alter_job_quote_to_charfield.py` (trailing newlines only)
- `rental_scheduler/migrations/0035_alter_job_quote_add_default.py` (trailing newlines only)
- `rental_scheduler/templates/rental_scheduler/jobs/job_import_json.html` (trailing newlines only)

**Already integrated upstream (no port needed):**
- `rental_scheduler/templates/rental_scheduler/jobs/_job_form_partial.html`: correct datetime formatting (`Y-m-d\\TH:i`) for non-all-day edits is already present on updated master.
- `rental_scheduler/templates/rental_scheduler/calendar.html`: search input padding fix is already present (inline `padding-left: 36px;`).

**Meaningful changes (candidate “must keep”):**
- `rental_scheduler/utils/recurrence.py`
  - Monthly recurrence should preserve the same weekday occurrence (e.g., “3rd Friday” stays “3rd Friday”)
  - Yearly recurrence should preserve the same ISO week + weekday
  - Recurring instances should copy call reminder flags and create `CallReminder` rows for each instance
- `rental_scheduler/models.py`
  - Add `daily` + `weekly` to `REPEAT_CHOICES` (aligns with existing migration choices)
  - Make `create_recurrence_rule()` accept `until_date` as date/datetime/ISO string and store a date-only value
- `rental_scheduler/views.py`
  - Add `date_filter=two_years` to `JobListView`
  - Make job search match phone numbers by **digits** (so searching `6208887050` matches `(620) 888-7050`)
  - Improve sorting robustness (handle `-field` and set default sort for the 2-year filter)
  - Validate/parses recurrence inputs in `job_create_submit` (interval/count/until date)
- `rental_scheduler/static/rental_scheduler/js/job_calendar.js` + `rental_scheduler/templates/rental_scheduler/calendar.html`
  - Add a “Today sidebar” toggle button with persisted state
  - Add “Events within 2 years” option in calendar search
  - Add “Close Search” button
  - Add delayed tooltips on search-result rows (same UX as calendar event tooltips)
- `rental_scheduler/static/rental_scheduler/js/workspace.js`
  - Add delayed tooltips on workspace tabs by fetching job details and reusing `jobCalendar.showEventTooltip()`

**Probably don’t port as-is:**
- `rental_scheduler/templates/rental_scheduler/partials/job_row.html`: WIP added many `data-*` attributes, but references old/removed fields (`job.business`, `job.contact`, `job.trailer`). If we want row tooltips, we should implement them by fetching `/api/jobs/<id>/detail/` (or adapt attributes to current model).

### 3) Phase 1 “must keep” candidates (shortlist)

1. **Recurrence correctness**: monthly/yearly patterns should stay aligned to “Nth weekday” and ISO-week rules.
2. **Call reminders for recurring instances**: recurring generation should propagate reminder settings and create per-instance `CallReminder` rows.
3. **Calendar search “within 2 years”**: add UI option + backend filter support.
4. **Phone digit search**: searching digits should match formatted phone numbers.
5. **Recurrence validation in form submit**: prevent bad interval/count/until input and avoid passing raw strings into model methods.
6. **Today sidebar toggle**: make Today column hide/show, persisted in `localStorage`.
7. **Tooltips**: optional but nice—job row hover tooltip + workspace tab hover tooltip.

## Concrete port plan (Phase 2+) — recommended commit order

Each item below should be a **separate commit** on `port/wip-2025-12-16` with a message like: `Port: <intent> (from 834babd)`.

### Commit A — Models: recurrence rule parsing + repeat choices

Files:
- `rental_scheduler/models.py`

Changes:
- Add `('daily', 'Daily')` and `('weekly', 'Weekly')` to `REPEAT_CHOICES` (align with migration `0023_*` choices).
- Update `create_recurrence_rule(..., until_date=...)` to accept:
  - `date`
  - `datetime`
  - ISO-8601 string (e.g., `YYYY-MM-DD` or full datetime)
  and store `recurrence_rule['until_date']` as a **date-only `YYYY-MM-DD` string**.

Tests:
- Add a small unit test that `create_recurrence_rule(until_date="2026-01-15")` succeeds and stores `"2026-01-15"`.

### Commit B — Recurrence engine: monthly/yearly correctness + call reminders for instances

Files:
- `rental_scheduler/utils/recurrence.py`

Changes:
- Monthly: preserve “Nth weekday” (e.g., 3rd Friday → 3rd Friday next month).
- Yearly: preserve ISO week + weekday in the target year.
- When generating instances:
  - copy `has_call_reminder` and `call_reminder_weeks_prior`
  - reset `call_reminder_completed=False`
  - create a `CallReminder` row for each saved instance (using `get_call_reminder_sunday`)

Tests:
- Monthly Nth-weekday test (e.g., known 3rd-Friday date → next month’s 3rd Friday).
- Call reminder propagation test: generating instances with call reminders creates corresponding `CallReminder` rows.

### Commit C — Views: validate recurring inputs on `job_create_submit`

Files:
- `rental_scheduler/views.py`

Changes:
- Validate `recurrence_interval` and `recurrence_count` are integers, `>= 1`, and `count <= 500`.
- Parse `recurrence_until` from `YYYY-MM-DD` into a `date` (show a friendly message on parse failure).

### Commit D — Job list + calendar search: two-year filter + phone digit search + sorting robustness

Files:
- `rental_scheduler/views.py`

Changes:
- Add `date_filter == 'two_years'` support in `JobListView` (now → now + 730 days).
- Implement phone digit search by annotating a `phone_digits` field and matching `icontains` against the digit-only input.
- Sorting: accept sort keys with leading `-`, and default to ascending for the `two_years` view unless explicitly overridden.

### Commit E — Calendar UI: two-year option + close search + Today sidebar toggle + search-row tooltips

Files:
- `rental_scheduler/templates/rental_scheduler/calendar.html`
- `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

Changes:
- Add “Events within 2 years” radio option in the calendar search panel.
- Add “Close Search” button (calls existing `toggleSearchPanel()`).
- Add Today sidebar toggle button (persisted in `localStorage`) and hide/show `#todaySidebar`.
- Add delayed hover tooltips for search-result job rows.
  - Recommended implementation: fetch `/api/jobs/<id>/detail/` (row already has `data-job-id`) to avoid stuffing large notes into `data-*` attributes.

Optional:
- Extend `job_detail_api` to include `calendar_name` so tooltips can show it.

### Commit F — Workspace UI: tab hover tooltip

Files:
- `rental_scheduler/static/rental_scheduler/js/workspace.js`

Changes:
- Add 500ms delayed hover tooltip for workspace tabs by fetching `/api/jobs/<id>/detail/` and calling `jobCalendar.showEventTooltip()`.

## Validation checklist (after each commit + at the end)

- Run targeted tests for the touched area (then full suite at the end).
- Manual smoke:
  - calendar loads, Today sidebar toggle persists across refresh
  - calendar search “within 2 years” returns results
  - searching digits finds formatted phone numbers
  - creating a recurring job with a call reminder produces instance call reminders
  - recurrence “until date” does not crash and validates properly

## Merge path

- Open PR: `port/wip-2025-12-16` → `master`
- PR description should include:
  - list of ported intents (Commits A–F)
  - note that `origin/wip/steph-pre-sync-2025-12-16` remains untouched as archival reference
