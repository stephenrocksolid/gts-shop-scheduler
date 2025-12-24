# Documentation Refresh Plan (Inventory → Strategy → Updates)

Date: 2025-12-22  
Scope: bring repo documentation up to date after the frontend refactor phases and add drift-prevention rules for Cursor agents.

## Goals (from project TODO)

1. Inventory all existing documentation
2. Identify outdated docs and update them
3. Identify legacy docs that can be deleted
4. Craft a robust documentation strategy for the project
5. Update the project with the correct documentation
6. Add concise `.mdc` Cursor rule docs in `.cursor/rules/` that point to canonical docs and reduce code drift
7. Move phase execution plans + `FRONTEND_INVENTORY_AND_REFACTOR_PLAN.md` into a docs archive

## Progress

- ✅ **PR 1 (docs home + archive moves)** — completed 2025-12-22
  - Added `docs/README.md`
  - Created `docs/archive/execution-plans/` + `docs/archive/refactor-plans/`
  - Moved phase execution plans into `docs/archive/execution-plans/`
  - Moved `FRONTEND_INVENTORY_AND_REFACTOR_PLAN.md` into `docs/archive/refactor-plans/`
  - Deleted empty `plan.md`
- ✅ **PR 2 (architecture/reference docs)** — completed 2025-12-22
  - Added architecture docs under `docs/architecture/` (`frontend.md`, `backend.md`, `data-model.md`)
  - Added reference docs under `docs/reference/` (`urls-and-routing.md`, `frontend-globals.md`)
  - Added runbook `docs/runbooks/local-dev.md`
  - Updated `docs/README.md` to link to the new canonical docs
- ✅ **PR 3 (recurring-events docs migration + updates)** — completed 2025-12-22
  - Moved legacy docs out of `rental_scheduler/docs/` into `docs/features/recurring-events/`
  - Updated docs to match current endpoints (including delete scope + materialize API)
  - Documented “forever series” + virtual occurrences
- ✅ **PR 4 (README refresh + template docs refresh)** — completed 2025-12-22
  - Updated `README.md` with a docs entrypoint and Linux/macOS equivalents for setup + Playwright
  - Updated `rental_scheduler/templates/README.md` to match current template structure (removed deleted files, added includes/call_reminders)
- ✅ **PR 5 (Cursor rules .mdc files)** — completed 2025-12-22
  - Added `.cursor/rules/*.mdc` drift-prevention rules pointing to canonical `docs/`

---

## Guiding principles (so docs don’t drift again)

- **One canonical home for docs**: use `docs/` at repo root as the entry point and information architecture.
- **Prefer links over duplication**: docs should point to the authoritative code locations (files, functions, URL names) rather than copying large code blocks.
- **Docs are part of the API**: when we change any public contract (URLs, JS globals, event schemas), we update docs in the same PR.
- **Archive, don’t delete history**: execution plans and exploratory documents go to `docs/archive/` (keeps context without cluttering the root).
- **Keep Cursor rules short**: `.cursor/rules/*.mdc` should be “guardrails + pointers”, not full documentation.

---

## 1) Inventory (current markdown files in repo)

This is the current complete list of `*.md` files (as of 2025-12-22).

| Path | Type | Current status | Proposed action | Notes |
|---|---|---:|---|---|
| `README.md` | Project README | Updated | Keep | Links to `docs/` and includes Linux/macOS + Windows setup steps (PR4). |
| `docs/README.md` | Docs index | New | Keep | Canonical docs entrypoint (PR1). |
| `docs/DOCUMENTATION_REFRESH_PLAN.md` | Plan | Active | Keep | Canonical plan + progress log (this file). |
| `docs/architecture/frontend.md` | Architecture | New | Keep | Frontend contracts + file layout (PR2). |
| `docs/architecture/backend.md` | Architecture | New | Keep | Backend structure + routing + contracts (PR2). |
| `docs/architecture/data-model.md` | Architecture | New | Keep | High-level model map (PR2). |
| `docs/reference/urls-and-routing.md` | Reference | New | Keep | Canonical URL strategy for JS (PR2). |
| `docs/reference/frontend-globals.md` | Reference | New | Keep | Global JS facades/contracts (PR2). |
| `docs/runbooks/local-dev.md` | Runbook | New | Keep | Local setup/run/test instructions (PR2). |
| `rental_scheduler/templates/README.md` | Internal docs | Updated | Keep | Updated directory tree; removed deleted templates; added `includes/` + `call_reminders/` (PR4). |
| `docs/features/recurring-events/guide.md` | Feature guide | Updated | Keep | Migrated from `rental_scheduler/docs/` (PR3). |
| `docs/features/recurring-events/api.md` | API reference | Updated | Keep | Migrated from `rental_scheduler/docs/` (PR3). |
| `docs/archive/execution-plans/PHASE_1_EXECUTION_PLAN.md` | Execution plan | Archived | Keep (archived) | Moved from repo root (PR1). |
| `docs/archive/execution-plans/PHASE_2_EXECUTION_PLAN.md` | Execution plan | Archived | Keep (archived) | Moved from repo root (PR1). |
| `docs/archive/execution-plans/PHASE_3_EXECUTION_PLAN.md` | Execution plan | Archived | Keep (archived) | Moved from repo root (PR1). |
| `docs/archive/execution-plans/PHASE_4_EXECUTION_PLAN.md` | Execution plan | Archived | Keep (archived) | Moved from repo root (PR1). |
| `docs/archive/execution-plans/PHASE_5_EXECUTION_PLAN.md` | Execution plan | Archived | Keep (archived) | Moved from repo root (PR1). |
| `docs/archive/execution-plans/PHASE_6_EXECUTION_PLAN.md` | Execution plan | Archived | Keep (archived) | Moved from repo root (PR1). |
| `docs/archive/refactor-plans/FRONTEND_INVENTORY_AND_REFACTOR_PLAN.md` | Architecture + plan | Archived | Keep (archived) | Moved from repo root (PR1). |

**Inventory completeness note**: Cursor rules now exist under `.cursor/rules/`:

- `.cursor/rules/00-docs-and-contracts.mdc`
- `.cursor/rules/frontend-architecture.mdc`
- `.cursor/rules/backend-architecture.mdc`
- `.cursor/rules/recurring-events.mdc`
- `.cursor/rules/testing.mdc`

---

## 2) Identify outdated docs (drift signals + verification checklist)

### Drift signals (fast heuristics)

- Mentions files that no longer exist (example: `templates/README.md` lists `components/modal.html`).
- Refers to endpoints that do not exist in `rental_scheduler/urls.py`.
- Mentions frontend contracts that were replaced (hard-coded URLs vs `window.GTS.urls`, inline JS that moved to `static/.../entrypoints/`, etc.).
- Mentions removed tech (e.g. Alpine mode, legacy init patterns).

### Verification checklist (per doc)

For each doc we keep, verify:

- **Code pointers are correct**: file paths, key functions/classes, Django URL `name=...`, and JS global names.
- **Examples still run**: curl/js snippets use correct endpoints + CSRF behavior.
- **Schemas match**: request/response examples match what handlers actually accept/return.
- **Cross-links resolve**: relative links work after moving docs into `docs/`.

---

## 3) Legacy docs: what can be deleted vs archived?

### Delete candidates (safe)

- ✅ `plan.md` (empty) — deleted (PR1)

### Archive candidates (keep history, remove root clutter)

- ✅ `docs/archive/execution-plans/PHASE_1_EXECUTION_PLAN.md` … `PHASE_6_EXECUTION_PLAN.md` — archived (PR1)
- ✅ `docs/archive/refactor-plans/FRONTEND_INVENTORY_AND_REFACTOR_PLAN.md` — archived (PR1)

---

## 4) Documentation strategy (target structure + conventions)

### Canonical docs tree (proposal)

Create a root `docs/` folder with a clear information architecture:

```
docs/
  README.md                      # docs index (start here)
  architecture/
    frontend.md                  # JS + templates architecture + contracts
    backend.md                   # Django architecture + URL map + view patterns
    data-model.md                # key models + invariants (Job, Calendar, recurrence fields)
  features/
    recurring-events/
      guide.md                   # (from rental_scheduler/docs/RECURRING_EVENTS_GUIDE.md)
      api.md                     # (from rental_scheduler/docs/API_RECURRING_EVENTS.md)
  runbooks/
    local-dev.md                 # how to run server + tailwind + tests
    releases.md                  # optional if you deploy
  reference/
    urls-and-routing.md          # `window.GTS.urls`, Django url names, “no hard-coded URLs”
    frontend-globals.md          # `JobPanel`, `JobWorkspace`, `jobCalendar` contracts
  archive/
    execution-plans/             # all PHASE_* plans
    refactor-plans/              # FRONTEND_INVENTORY... and other big planning docs
```

### Doc conventions (lightweight)

- **Top of file header**: include `Last updated:` and a short “What this doc is for”.
- **Prefer “contracts” sections**:
  - Frontend: `window.GTS.urls`, `window.JobPanel`, `window.JobWorkspace`, `window.jobCalendar`, `window.calendarConfig` schema.
  - Backend: URL names, view ownership, API schemas, partial rendering contracts.
- **Link to code** using stable identifiers:
  - Django: URL name (e.g. `rental_scheduler:job_list_table_partial`), view class/function, template path.
  - JS: file path + exported global name.

---

## 5) Step-by-step execution plan (ship in small PRs)

### PR 1 — Establish docs home + archive old plans (no behavior change) ✅ COMPLETED

- Create `docs/README.md` (docs index) with links to:
  - architecture docs
  - features docs (recurrence)
  - runbooks
  - archive
- Create `docs/archive/execution-plans/` and `docs/archive/refactor-plans/`.
- Move:
  - `PHASE_*_EXECUTION_PLAN.md` → `docs/archive/execution-plans/`
  - `FRONTEND_INVENTORY_AND_REFACTOR_PLAN.md` → `docs/archive/refactor-plans/`
- Delete:
  - `plan.md` (empty)

**Acceptance checks**
- Repo root is no longer cluttered with phase plans.
- Links in `docs/README.md` work.
- No runtime code changes.

### PR 2 — Create architecture docs (minimal but correct) ✅ COMPLETED

- Add:
  - `docs/architecture/frontend.md`
  - `docs/architecture/backend.md`
  - `docs/reference/urls-and-routing.md`
  - `docs/reference/frontend-globals.md`
- Content requirements:
  - **Frontend**: explain `static/rental_scheduler/js/shared/*`, `entrypoints/*`, globals (`GTS.urls`, `JobPanel`, `JobWorkspace`, `jobCalendar`) and the “no hard-coded URLs” policy.
  - **Backend**: explain URL layout, views split (`views.py`, `views_recurring.py`), partial endpoints (`jobs/new/partial/`, `jobs/partial/table/`), and key API endpoints.

**Acceptance checks**
- A new dev can find “where to change X” quickly.
- Docs match current file structure.

### PR 3 — Move and update recurring-events docs ✅ COMPLETED

- Move:
  - `rental_scheduler/docs/RECURRING_EVENTS_GUIDE.md` → `docs/features/recurring-events/guide.md`
  - `rental_scheduler/docs/API_RECURRING_EVENTS.md` → `docs/features/recurring-events/api.md`
- Update content to:
  - reference current Django routes (from `rental_scheduler/urls.py`)
  - reference current backend handlers (from `rental_scheduler/views_recurring.py`)
  - reference current model fields/methods (from `rental_scheduler/models.py` + `utils/recurrence.py`)
- Add cross-links from `docs/architecture/backend.md` and `docs/README.md`.

**Acceptance checks**
- Docs use correct endpoints and field names.
- No references to moved/deleted file paths remain.

### PR 4 — Refresh project README + template docs ✅ COMPLETED

- Update `README.md`:
  - add “Docs” section linking to `docs/README.md`
  - ensure Linux commands are included alongside Windows examples
  - document basic “how to run tests” (pytest + playwright) and mention `BASE_URL`
- Update `rental_scheduler/templates/README.md`:
  - remove references to deleted templates
  - update notes to match current layout and component/partial usage

**Acceptance checks**
- Root README is accurate and points to canonical docs.

### PR 5 — Add Cursor drift-prevention rules (`.mdc`) ✅ COMPLETED

Add 3–5 concise `.mdc` rule files in `.cursor/rules/` that:

- summarize key contracts
- forbid common drift patterns
- point to the canonical docs under `docs/`

Recommended rule set:

1. `.cursor/rules/00-docs-and-contracts.mdc`
   - Applies broadly (`**/*`)
   - “If you change a contract, update docs in the same PR”
   - Points to `docs/README.md`

2. `.cursor/rules/frontend-architecture.mdc`
   - Globs: `rental_scheduler/static/rental_scheduler/js/**/*.js`, `rental_scheduler/templates/**/*.html`
   - Key rules:
     - Do not hard-code URLs; use `window.GTS.urls` and `GTS.urls.interpolate(...)`.
     - Preserve global facade contracts: `window.JobPanel`, `window.JobWorkspace`, `window.jobCalendar`.
   - Points to: `docs/architecture/frontend.md`, `docs/reference/frontend-globals.md`, `docs/reference/urls-and-routing.md`

3. `.cursor/rules/backend-architecture.mdc`
   - Globs: `rental_scheduler/**/*.py`
   - Key rules:
     - Maintain URL names (`name='...'`) stability; update `base.html` `GTS.urls` injection when adding/changing routes used by JS.
     - Prefer partial endpoints for fragment fetches (no HTML scraping).
   - Points to: `docs/architecture/backend.md`, `docs/reference/urls-and-routing.md`

4. (Optional) `.cursor/rules/recurring-events.mdc`
   - Globs: `rental_scheduler/views_recurring.py`, `rental_scheduler/utils/recurrence.py`, `rental_scheduler/models.py`, `docs/features/recurring-events/**/*.md`
   - Points to: recurring events docs

**Acceptance checks**
- Cursor rules are short, readable, and point to the canonical docs.
- They explicitly protect the “no drift” contracts (URLs + globals).

---

## 6) Optional: add drift guardrails (light automation)

These are “nice to have” once the docs stabilize:

- Add a small CI check that `docs/README.md` exists and contains links to the major sections (architecture, features, runbooks).
- Add a “Docs updated?” checklist item to PR template (if you use GitHub).

---

## Definition of Done (for the entire docs refresh)

- Root has **no** active phase plan docs; plans live under `docs/archive/`.
- `docs/README.md` exists and is the canonical entrypoint.
- Architecture docs exist and reflect current frontend/back-end contracts.
- Recurring-events docs are moved under `docs/features/` and verified against code.
- `.cursor/rules/*.mdc` exists and points agents to docs (and away from drift patterns).


