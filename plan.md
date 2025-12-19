## Status / is this expected?

No — these failures are not “expected progress” from Phase 1 in the sense of new product logic being broken.
They’re a **test-environment/staticfiles configuration issue** that prevents templates from rendering at all.

When the base template can’t render, anything that requests a page that extends `base.html` fails (calendar page, job list, job partials, etc.).
That’s why you’re seeing a large cascade of failures with the *same* exception.

---

## What is failing (symptom)

**Exception**: `ValueError: Missing staticfiles manifest entry for 'rental_scheduler/img/favicon-32x32.png'`

**Where it happens**:
- `rental_scheduler/templates/base.html` references multiple favicon/static assets via `{% static %}`.
- The *first* one in the file is:
  - `rental_scheduler/img/favicon-32x32.png`

**Why it cascades**:
- Many tests exercise endpoints that render templates extending `base.html`.
- Template rendering fails before the view can return a response, so tests that “just load the page” all fail.

---

## Root cause (why Django is throwing this)

### Root cause A — `ManifestStaticFilesStorage` is enabled during tests
In `gts_django/settings.py` you have:

- `STORAGES["staticfiles"]["BACKEND"] = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"`

`ManifestStaticFilesStorage` **requires** that `collectstatic` has been run so it can read `staticfiles.json` and map:

- `rental_scheduler/img/favicon-32x32.png` → `rental_scheduler/img/favicon-32x32.<hash>.png`

During `pytest`, **`collectstatic` is not run**, so there is no manifest mapping available.
When `{% static %}` calls `staticfiles_storage.url(...)`, Django tries to look up the hashed name in the manifest and raises:

- `Missing staticfiles manifest entry for ...`

### Root cause B — only one test module opts out of manifest storage
There is already a module-level fixture in:

- `rental_scheduler/tests/test_partials.py`

…that switches tests to `StaticFilesStorage` specifically “to avoid needing collectstatic”.
But that fixture only applies to that single test module.
All other template-rendering tests still use the project default (`ManifestStaticFilesStorage`) and crash.

### Root cause C — the base template touches static very early
Even though the favicon images *do* exist in:

- `rental_scheduler/static/rental_scheduler/img/`

…with `ManifestStaticFilesStorage`, existence in app static dirs is not enough — **the manifest mapping must exist**.
Because the favicon is the first `{% static %}` call in the `<head>`, template rendering fails immediately.

---

## “Root cause of each failing test” (grouped)

All 41 failures you pasted are the same underlying defect, just triggered from different pages/tests:

- **`rental_scheduler/tests/test_calendar_template.py`**: calendar page render extends `base.html` → fails on favicon static lookup.
- **`rental_scheduler/tests/test_date_filter_ui.py`**: calendar/job list pages extend `base.html` → same failure.
- **`rental_scheduler/tests/test_job_list_view_filters.py`**: job list pages extend `base.html` → same failure.
- **`rental_scheduler/tests/test_recurrence_generation.py`**: partials/pages still extend `base.html` (or render templates that include it) → same failure.

So the correct fix is **one change** in how staticfiles storage is configured for tests (or one change to run `collectstatic` during tests).

---

## Fix plan (actionable, step-by-step)

### Recommended approach (fast + keeps tests focused): use simple staticfiles storage in tests

**Goal**: tests should not require a build/collect step to render templates; they should validate HTML structure/behavior.

1. **Add a global autouse pytest fixture** in repo-root `conftest.py` that overrides `settings.STORAGES["staticfiles"]` to use `django.contrib.staticfiles.storage.StaticFilesStorage`.
   - This mirrors what you already do in `rental_scheduler/tests/test_partials.py`, but applies to the entire test suite.
2. **Remove or simplify the module-level fixture** in `rental_scheduler/tests/test_partials.py`.
   - Keep it only if you want to be explicit in that module; otherwise it becomes redundant and can drift.
3. **Run a single previously-failing test** to confirm the stacktrace is gone:

   - `python -m pytest rental_scheduler/tests/test_calendar_template.py::TestCalendarTemplateGuardrails::test_calendar_page_loads -q`

4. **Run full suite**:

   - `python -m pytest`

5. **If new failures appear after templates can render**, triage them next (they’ll now be “real” functional regressions rather than template boot failures).

**Why this is recommended right now**:
- It unblocks the test suite immediately.
- It matches the existing intent in `test_partials.py` (“avoid needing collectstatic”).
- It prevents front-end build/asset pipeline details from making unit/integration tests brittle.

---

### Alternative approach (production-like): run `collectstatic` during tests

**Goal**: keep `ManifestStaticFilesStorage` in tests so tests fail if any template references a missing static asset.

1. Keep `ManifestStaticFilesStorage` enabled.
2. In test setup (e.g. `pytest_configure` in root `conftest.py`), run:

   - `python manage.py collectstatic --noinput`

3. Ensure `STATIC_ROOT` points to a test-only temp folder so the repo working tree isn’t polluted.
4. Run pytest.

**Tradeoffs**:
- Slower tests.
- More moving parts (permissions, temp dirs, any static build steps, etc.).
- Can be worth it later as a dedicated CI job, but it’s usually overkill for most unit/integration tests.

---

### Optional hardening (recommended soon): make static storage environment-aware

Right now `DEBUG` is hardcoded `True`, and `ManifestStaticFilesStorage` is always enabled.
That’s brittle (dev pages can break unless you always run collectstatic).

1. Make `DEBUG` driven by env (`DEBUG=1/0`).
2. Choose the staticfiles backend based on env:
   - Dev/test: `StaticFilesStorage`
   - Production: `ManifestStaticFilesStorage` (or WhiteNoise’s compressed manifest storage)
3. Update deployment docs/scripts to always run `collectstatic` in production builds.

---

## Validation checklist (definition of done)

- [ ] `python -m pytest` runs without any `Missing staticfiles manifest entry` errors.
- [ ] `base.html` renders in tests (calendar page returns 200).
- [ ] No test relies on `collectstatic` unless explicitly intended.
- [ ] If keeping manifest in prod: deploy pipeline runs `collectstatic --noinput` and serves `STATIC_ROOT`.
