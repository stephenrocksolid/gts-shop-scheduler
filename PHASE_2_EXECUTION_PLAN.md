## Phase 2 Execution Plan — Shared frontend library helpers

This plan covers **Phase 2 only** from `FRONTEND_INVENTORY_AND_REFACTOR_PLAN.md`.

Phase 1 is complete.

### Phase 2 goal
Stop duplicating common frontend helpers by creating a small shared “frontend library” under:

- `rental_scheduler/static/rental_scheduler/js/shared/`

### Phase 2 definition of done
- **Panel + workspace** use the **same** draft HTML serialize/sanitize implementation.
- **Calendar/panel/workspace** use the **same** CSRF + toast helpers.

### Constraints (Phase 2)
- **No bundler**: plain JS files loaded via `<script>` tags; **load order matters**.
- **No behavior changes**: UI/UX and persistence remain identical.
- **Keep contracts stable**:
  - Keep existing localStorage keys (no renames in Phase 2).
  - Keep globals used elsewhere (`window.JobPanel`, `window.JobWorkspace`, `window.jobCalendar`, `window.calendarConfig`, `window.showToast`, `window.getCookie`).
- **Out of scope** (explicit): Phase 3+ refactors (no internal `job_calendar.js` module split, no panel persistence consolidation, no URL cleanup, no endpoint changes).

### Phase 2 status (implementation audit)
As of **2025-12-19** (static code audit only; see Validation plan below):

- **Definition of done**: likely met (pending runtime validation)
- **2A (shared load order)**: complete
- **2B (html_state)**: complete
- **2C (csrf)**: complete (calendar delegates via a wrapper method)
- **2D (toast)**: complete (calendar no longer has a custom toast renderer)
- **2E (storage)**: complete (workspace quota fallback preserved)
- **2F (dom helpers)**: implemented; adoption is optional/partial

---

## 0) Audit notes (ground truth from current code)

### Unified helper sources (post-Phase-2 snapshot)

#### Toast
- **Toast UI renderer**: `rental_scheduler/templates/base.html` defines `window.showToast(message, type, duration)`.
- **Shared wrapper API**: `rental_scheduler/static/rental_scheduler/js/shared/toast.js`
  - `GTS.toast.*`
  - `GTS.showToast = GTS.toast.show` (back-compat)
- **Consumers**:
  - `panel.js`, `workspace.js` use `GTS.toast.*`
  - `job_calendar.js` routes toast calls through `GTS.toast.*` (wrapper method remains as a thin delegate)
  - `entrypoints/job_form_partial.js` uses `GTS.showToast(...)` (alias)

#### CSRF
- **Base template**: `rental_scheduler/templates/base.html`
  - `<meta name="csrf-token" content="{{ csrf_token }}">`
  - `window.getCookie(name)`
  - HTMX `htmx:configRequest` handler uses `GTS.csrf.getToken()` (with fallback)
- **Shared CSRF module**: `rental_scheduler/static/rental_scheduler/js/shared/csrf.js`
  - `GTS.csrf.getToken({ root? })`
  - `GTS.csrf.headers(extraHeaders, { root? })`
  - `GTS.getCookie(name)` (back-compat alias)
- **Config utility**: `rental_scheduler/static/rental_scheduler/js/config.js` still implements `RentalConfig.getCSRFToken()` + `getApiHeaders()` (optional future delegation).
- **Consumers**:
  - `panel.js` uses `GTS.csrf.headers(..., { root: form })` for fetch paths.
  - `entrypoints/job_form_partial.js` uses `GTS.csrf.getToken/headers`.
  - `job_calendar.js` delegates `getCSRFToken()` to `GTS.csrf.getToken()` (wrapper method remains; duplicate methods removed).

#### Draft HTML state (serialize/sanitize)
- **Canonical implementation**: `rental_scheduler/static/rental_scheduler/js/shared/html_state.js` (`GTS.htmlState.*`)
- **Consumers**:
  - `panel.js` uses `GTS.htmlState.serializeDraftHtml(...)` and `GTS.htmlState.sanitizeDraftHtml(...)`.
  - `workspace.js` uses `GTS.htmlState.sanitizeDraftHtml(...)`.

#### Storage
- **Canonical implementation**: `rental_scheduler/static/rental_scheduler/js/shared/storage.js` (`GTS.storage.*`)
- **Consumers migrated (Phase 2 scope)**:
  - `panel.js` uses `GTS.storage.getJson/setJson` for `jobPanelState`
  - `workspace.js` uses `GTS.storage.getJson/setJson/remove` for `gts-job-workspace` (**includes quota-exceeded fallback retry without HTML**)
  - entrypoints: `calendar_page.js`, `jobs_list_page.js`, `panel_shell.js`
- Direct `localStorage.*` usage still exists in `job_calendar.js` for calendar-only keys (out of Phase 2 scope; Phase 4+ can standardize further).

---

## 1) Target Phase 2 file layout

Create these files (no bundler required):

- `rental_scheduler/static/rental_scheduler/js/shared/`
  - `csrf.js` — single CSRF getter + header helper
  - `toast.js` — wrap `window.showToast`
  - `storage.js` — namespaced localStorage helpers (JSON/boolean/raw)
  - `dom.js` — safe binding + delegation helpers
  - `html_state.js` — serialize/sanitize draft HTML

---

## 2) Proposed shared API contract (script-tag friendly)

Implement helpers under `window.GTS` (keep existing global style consistent with `gts_init.js`).

### Relationship to `gts_init.js` (Phase 2 cleanup)
- `gts_init.js` currently does **two jobs**: (1) idempotent init utilities and (2) “shared helpers” (`getCookie`, `showToast`).
- In Phase 2, once `shared/csrf.js` and `shared/toast.js` exist, **move**:
  - `GTS.getCookie` → `shared/csrf.js`
  - `GTS.showToast` → `shared/toast.js`
- Then slim `gts_init.js` back down to **init-only** (no CSRF/toast helpers) to eliminate duplication and clarify responsibilities.
- Keep compatibility by preserving the **same names** (`GTS.getCookie`, `GTS.showToast`) as aliases provided by the new shared modules.

### `shared/csrf.js`
- **`GTS.csrf.getToken(options?) -> string`**
  - Precedence (consistent across all call sites):
    1) `meta[name="csrf-token"]`
    2) `options.root?.querySelector('input[name="csrfmiddlewaretoken"]')` (if provided)
    3) cookie `csrftoken` via `window.getCookie` or a safe internal fallback
- **`GTS.csrf.headers(extraHeaders = {}) -> Object`**
  - Returns `{...extraHeaders, 'X-CSRFToken': token}` (token may be empty string).

### `shared/toast.js`
- **`GTS.toast.show(message, type='info', duration=5000)`**
  - Uses `window.showToast` when available; otherwise `console.log` fallback.
- Convenience:
  - `GTS.toast.success(message, duration?)`
  - `GTS.toast.error(message, duration?)`
  - `GTS.toast.warning(message, duration?)`
  - `GTS.toast.info(message, duration?)`
- Back-compat alias:
  - **`GTS.showToast = GTS.toast.show`** (so existing Phase 1 entrypoint remains stable)

### `shared/storage.js`
- **`GTS.storage.getRaw(key) -> string|null`**
- **`GTS.storage.setRaw(key, value) -> void`**
- **`GTS.storage.remove(key) -> void`**
- **`GTS.storage.getJson(key, fallback=null)`** (try/catch)
- **`GTS.storage.setJson(key, value) -> boolean`** (try/catch; returns false if storage fails)
- **`GTS.storage.getBool(key, fallback=false)`**
- **`GTS.storage.setBool(key, value)`**
- Optional future-proofing (keep keys unchanged for Phase 2):
  - `GTS.storage.namespace(prefix)` returns wrapper for `{ getJson, setJson, ... }`

### `shared/dom.js`
- **`GTS.dom.on(el, eventName, handler, options?)`** (direct)
- **`GTS.dom.on(el, eventName, selector, handler, options?)`** (delegated)
- **`GTS.dom.closest(el, selector)`**
- **`GTS.dom.stop(e)`** (`preventDefault` + `stopPropagation`)

### `shared/html_state.js`
- **`GTS.htmlState.sanitizeDraftHtml(html) -> string`**
  - Trim whitespace in `value` attributes for strict input types.
- **`GTS.htmlState.serializeDraftHtml(rootEl) -> string|null`**
  - Preserve checkbox/radio `checked`, select `selected`, textarea content, and text/date/number inputs.

---

## 3) Work breakdown (ordered, shippable increments)

### 2A) Create `shared/` folder + wire global load order

**Status**: complete

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/shared/` (directory)
- **Update** `rental_scheduler/templates/base.html`

**Tasks**
- Add `<script>` tags in `base.html` to load shared helpers globally (recommended: after `gts_init.js`).
- Document required order in a comment, e.g.:
  - `gts_init.js` → `shared/*` → `panel.js`/`workspace.js`/entrypoints

**Acceptance checks**
- No JS errors on pages that don’t use the helpers.
- `window.GTS.csrf`, `window.GTS.toast`, `window.GTS.storage`, `window.GTS.dom`, `window.GTS.htmlState` exist.

---

### 2B) `shared/html_state.js` + migrate panel/workspace

**Status**: complete

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/shared/html_state.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/panel.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/workspace.js`

**Tasks (new module)**
- Move the canonical implementations from `panel.js` into `shared/html_state.js`:
  - `sanitizeDraftHtml(html)`
  - `serializeDraftHtml(panelBody)`

**Tasks (panel)**
- Replace these call sites:
  - `serializeDraftHtml(panelBody)` (around `~L1257`, `~L1519`) → `GTS.htmlState.serializeDraftHtml(panelBody)`
  - `sanitizeDraftHtml(html)` (around `~L1667`) → `GTS.htmlState.sanitizeDraftHtml(html)`
- Remove the local `sanitizeDraftHtml` / `serializeDraftHtml` function definitions from `panel.js`.

**Tasks (workspace)**
- Remove the local `sanitizeDraftHtml` function.
- Replace:
  - `sanitizeDraftHtml(html)` (around `~L411`, `~L497`) → `GTS.htmlState.sanitizeDraftHtml(...)`

**Acceptance checks**
- Draft restore still works (no browser errors caused by invalid whitespace in strict input values).
- Workspace draft tabs still restore correctly.

---

### 2C) `shared/csrf.js` + migrate calendar/panel/workspace CSRF usage

**Status**: complete (calendar delegates via wrapper)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/shared/csrf.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/gts_init.js` *(remove duplicate cookie helper once shared module exists)*
- **Update** `rental_scheduler/templates/base.html`
- **Update** `rental_scheduler/static/rental_scheduler/js/panel.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/entrypoints/job_form_partial.js`
- *(Optional)* **Update** `rental_scheduler/static/rental_scheduler/js/config.js` to delegate token lookup to `GTS.csrf.getToken()` (or vice versa)

**Tasks (new module)**
- Implement `GTS.csrf.getToken()` with consistent precedence:
  - meta → hidden input (scoped) → cookie.
- Implement `GTS.csrf.headers(extraHeaders)` helper.
- Also expose/alias **`GTS.getCookie(name)`** from this module (re-homing the implementation currently in `gts_init.js`).

**Tasks (`gts_init.js`)**
- Remove the `GTS.getCookie(...)` implementation from `gts_init.js` once `shared/csrf.js` provides it.
- Keep `gts_init.js` focused on idempotent init utilities only.

**Tasks (base template)**
- Update `htmx:configRequest` listener to use `GTS.csrf.getToken()` instead of direct `window.getCookie('csrftoken')`.

**Tasks (panel)**
- Replace the duplicated CSRF fallback chain in `panel.js` (around `~L1108` and `~L2022`) with `GTS.csrf.getToken({ root: form })`.

**Tasks (job form partial entrypoint)**
- Replace header token selection to use `GTS.csrf.getToken({ root: form })`:
  - save-then-print fetch fallback (~`L309–L315`)
  - status update/delete fetches (~`L433–L472`)

**Tasks (calendar)**
- Replace all occurrences of `this.getCSRFToken()` used in fetch headers with `GTS.csrf.getToken()`:
  - `X-CSRFToken` usages include ~`L3203`, `L3271`, `L3620`, `L3656`, `L3707`, `L3739`, `L3778`, `L4041`
- Remove the duplicate `getCSRFToken()` methods from `job_calendar.js` so there is only one strategy.

**Acceptance checks**
- All POST actions still succeed:
  - panel save fallback
  - job status update/delete
  - call reminder actions
  - HTMX requests still include CSRF.

---

### 2D) `shared/toast.js` + migrate calendar/panel/workspace toast usage

**Status**: complete (no calendar custom renderer remains)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/shared/toast.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/gts_init.js` *(remove duplicate toast helper once shared module exists)*
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/panel.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/workspace.js`
- *(Optional)* **Update** `rental_scheduler/static/rental_scheduler/js/entrypoints/job_form_partial.js`

**Tasks (new module)**
- Implement `GTS.toast.show(...)` as a thin wrapper over `window.showToast`.
- Add convenience methods (`success/error/warning/info`).
- Add back-compat alias: `GTS.showToast = GTS.toast.show`.

**Tasks (`gts_init.js`)**
- Remove the `GTS.showToast(...)` implementation from `gts_init.js` once `shared/toast.js` provides it.
- Keep `gts_init.js` focused on idempotent init utilities only.

**Tasks (calendar)**
- Update `job_calendar.js` to use shared toast helpers:
  - Replace local toast DOM renderer (`showToast(...)`) with `GTS.toast.show(...)`
  - Update `showError()` / `showSuccess()` to call `GTS.toast.error/success`
  - Remove `window.layout.showToast` branching (calendar should use the same app toast UI)

**Tasks (panel)**
- Replace `window.showToast(...)` call sites with `GTS.toast.*(...)`:
  - includes warnings/errors around `~L1015`, `~L1314`, `~L1356`, `~L1358`, `~L1929`

**Tasks (workspace)**
- Replace max-tab warning `window.showToast(...)` call sites with `GTS.toast.warning(...)`:
  - around `~L112`, `~L163`, `~L479`

**Acceptance checks**
- Toast UX is consistent across calendar/panel/workspace (same styling, placement, dismissal).
- No custom toast rendering remains in `job_calendar.js`.

---

### 2E) `shared/storage.js` + migrate the “big 3” storage behaviors

**Status**: complete (workspace quota fallback preserved)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/shared/storage.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/panel.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/workspace.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/entrypoints/panel_shell.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/entrypoints/calendar_page.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/entrypoints/jobs_list_page.js`

**Tasks (new module)**
- Provide safe JSON parse/stringify wrappers and boolean helpers (try/catch).
- Keep keys unchanged (Phase 4 handles consolidation).

**Tasks (panel)**
- Replace `save()` / `load()` localStorage JSON logic (near `~L2352–L2358`) with `GTS.storage.setJson/getJson` using the existing `jobPanelState` key.

**Tasks (workspace)**
- Replace `saveToStorage()` / `loadFromStorage()` localStorage JSON logic (near `~L992–L1077`) with `GTS.storage.setJson/getJson`.
- Preserve the current “quota exceeded fallback” behavior.

**Tasks (entrypoints)**
- `panel_shell.js`: use `GTS.storage.getRaw/setRaw` for `gts-panel-width` / `gts-panel-height`.
- `calendar_page.js`: use `GTS.storage.getRaw/setRaw` for `gts-sidebar-width`.
- `jobs_list_page.js`: use `GTS.storage.getJson/setJson` for `job-list-filters`.

**Acceptance checks**
- All existing persistence remains identical (same keys, same values).
- Corrupt JSON or quota exceeded cases are handled consistently.

---

### 2F) `shared/dom.js` + opportunistic adoption

**Status**: implemented; adoption optional/partial

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/shared/dom.js`
- **Update** selected entrypoints as needed (no functional changes)

**Tasks**
- Implement small delegation helpers and standard “stop event” helper.
- Replace repeated boilerplate in entrypoints (where safe):
  - delegated click/hover patterns in `job_form_partial.js`, `jobs_list_page.js`, `calendar_page.js`

**Acceptance checks**
- No duplicate handler regressions (Phase 1 idempotent init remains respected).

---

## 4) Validation plan (Phase 2)

### Automated
- Playwright smoke test: `tests/e2e/test_calendar_smoke.py`.
  - Note: this environment currently lacks `pytest`, so automated validation was not run here.

### Manual regression checklist (high value)
- Calendar:
  - load calendar; open event → panel opens
  - status update/delete works; calendar refreshes
  - call reminder actions still work
- Panel/workspace:
  - open job → edit field → draft/unsaved indicator persists
  - minimize to workspace → restore tab → draft HTML restores correctly
  - repeated open/close/swap does not double-bind handlers
- Toasts:
  - warning/error/success toasts appear from calendar/panel/workspace and look the same

---

## 5) Explicit non-goals (Phase 2)
- Phase 3 `job_calendar.js` module split
- Phase 4 panel state store consolidation
- Phase 5 URL hard-coded endpoint cleanup
- Phase 6 server partial endpoints to replace DOM scraping
- Phase 7 formatting/linting/bundler changes
