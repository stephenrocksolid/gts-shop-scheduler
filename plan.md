## Goal
Remove (or eliminate the need for) skipped tests by fixing underlying causes.

## Baseline
- Initial suite run showed **173 passed, 4 skipped**.
- A subsequent run with `-rs` showed **172 passed, 5 skipped** due to a flaky E2E test that sometimes self-skipped.

## What was skipped (from `pytest -rs`)
### `rental_scheduler/tests/test_partials.py`
- **`TestJobDetailPartial::test_job_detail_renders`**
  - Skip reason: `Template _job_detail_partial.html does not exist yet`
- **`TestJobCreateSubmitValidation::test_missing_business_name_returns_400`**
- **`TestJobCreateSubmitValidation::test_empty_business_name_returns_400`**
- **`TestJobCreateSubmitValidation::test_whitespace_only_business_name_returns_400`**
  - Skip reason (in-code): "Form validation works ... but pytest-django caching causes view test to fail"

### `tests/e2e/test_calendar_smoke.py`
- **`TestStandaloneCallReminderCRUD::test_create_call_reminder_on_sunday`**
  - Runtime skip reason: `Call reminder form not found - Sunday double-click may have opened job form`

## Findings / root causes
### 1) Missing template for `job_detail_partial`
- `rental_scheduler/views.py::job_detail_partial` renders `rental_scheduler/jobs/_job_detail_partial.html`.
- That template did not exist, so the render test was skipped.

**Fix**
- Created `rental_scheduler/templates/rental_scheduler/jobs/_job_detail_partial.html` (minimal, safe partial).
- Removed the `@pytest.mark.skip` from `TestJobDetailPartial::test_job_detail_renders`.

### 2) The “pytest-django caching” explanation was a red herring — `views.py` was using the *wrong* `JobForm`
- `rental_scheduler/views.py` imported `JobForm` from `.forms`, but later **defined another `class JobForm`** in the same module.
- That local `JobForm` definition **overrode the import**, so `job_create_partial` / `job_create_submit` were *not* using `rental_scheduler/forms.py::JobForm`.
- The `views.py` `JobForm` did **not** enforce `business_name` as required/whitespace-trimmed the same way as the canonical form.
  - Result: the view could accept missing/blank `business_name` and return success instead of `400`, which is why the view-level tests were skipped.

**Fix**
- Deleted the duplicate `class JobForm` from `rental_scheduler/views.py` so the module now correctly uses the imported `rental_scheduler/forms.py::JobForm`.
- Removed the 3 `@pytest.mark.skip` decorators in `TestJobCreateSubmitValidation`.

### 3) Follow-on issue discovered: the panel template does not submit `status`, but the canonical ModelForm would require it
- After switching the views to the canonical `forms.JobForm`, the E2E recurring-job test started failing to create a job (HTTP 400).
- Root cause: the model field `status` has `blank=False`, so the auto-generated ModelForm field would be required.
- The panel form template (`_job_form_partial.html`) **does not submit a `status` input** (status is changed via separate action buttons), so the view would now reject the submission.

**Fix**
- In `rental_scheduler/forms.py::JobForm`, explicitly defined `status` as **non-required** `HiddenInput` (keeping panel submits valid while preserving model defaults).

### 4) E2E Sunday double-click flakiness: timezone + double-click path + event-targeting
The E2E call reminder test was skipping because `#call-reminder-form` sometimes never appeared.

Contributing factors found:
- In `job_calendar.js`, the date used to build URLs used `date.toISOString().split('T')[0]` (UTC), which can shift dates by ±1 day depending on timezone.
- FullCalendar `dateClick` double-click detection passes `info.date` which can include a timezone-offset time component; using that Date directly makes `getDay()` unreliable for “all-day” semantics.
- The test double-click could accidentally target an **event element**, which the calendar explicitly ignores for “open create form” behavior.

**Fixes**
- In `job_calendar.js::openCreateFormForDate`, build date strings using **local** `YYYY-MM-DD` (avoid `toISOString()` UTC shift).
- In the FullCalendar `dateClick` double-click detection, use `info.dateStr` (date-only) to construct a local midnight `Date` before calling `openCreateFormForDate`.
- Updated the E2E call reminder test to be deterministic:
  - Wait for `window.JobPanel` + `window.jobCalendar` readiness.
  - Double-click the **day number** element (not the whole cell) to avoid targeting events.
  - Wait for `#call-reminder-form`.
  - Submit and **capture the JSON response** to get a specific `reminder_id`.
  - Wait for the event with that `data-gts-reminder-id`.
  - Cleanup by deleting the reminder via API.
- Updated the E2E recurrence test similarly (avoid skips, click day number, assert creation).

## Result
After all fixes:
- `python -m pytest -rs` => **177 passed, 0 skipped**

## Changes made (high level)
- Added missing template: `rental_scheduler/templates/rental_scheduler/jobs/_job_detail_partial.html`
- Removed skip markers in `rental_scheduler/tests/test_partials.py`
- Removed duplicate `JobForm` class from `rental_scheduler/views.py` so the canonical form is used
- Updated `rental_scheduler/forms.py::JobForm`
  - Added `date_call_received` (template expects it)
  - Made `status` non-required (panel template doesn’t submit it)
- Hardened `job_calendar.js` date handling (local date + `info.dateStr` usage)
- Made E2E tests deterministic and removed their self-skipping paths
