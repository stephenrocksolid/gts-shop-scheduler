## Phase 4 Execution Plan — Panel cleanup (choose one implementation)

**STATUS: ✅ COMPLETED** (2025-12-19)

This plan covers **Phase 4 only** from `FRONTEND_INVENTORY_AND_REFACTOR_PLAN.md`.

Date: 2025-12-19

### Phase 4 goal / definition of done
- **Goal**: One panel implementation, one state store.
- **Definition of Done**:
  - **One codepath** for panel behavior (no Alpine vs vanilla split).
  - **One place** to change panel persistence (single key / single schema).

---

## The Phase 4 decision questions (and answers)

### Q1) Is Alpine truly supported in this app?
**Answer: No. Treat Alpine usage as accidental/leftover and remove it.**

**Evidence (from repo code):**
- `rental_scheduler/templates/base.html` does **not** load Alpine (no Alpine `<script>` tag).
- Repo-wide search turns up **no Alpine library include**; `Alpine` appears only in:
  - `rental_scheduler/static/rental_scheduler/js/panel.js` (compat code)
  - planning docs
- Alpine directives exist in only two templates:
  - `rental_scheduler/templates/rental_scheduler/workorders/workorder_detail.html` (`x-data`, `x-show`, `@click`)
  - `rental_scheduler/templates/rental_scheduler/components/modal.html` (`x-data`, `x-show`, transitions)

**Implication:**
- Remove Alpine compatibility paths from `panel.js`.
- Remove leftover Alpine directives (`x-*`, `@click`, etc.) from templates by converting those UI bits to vanilla JS / native HTML.

### Q2) What should be the single persisted state store for the panel?
**Answer: Use `jobPanelState` (JSON) as the canonical store and fold size into it. Deprecate `gts-panel-width` / `gts-panel-height`.**

**Why this is the best choice here:**
- `jobPanelState` already persists panel state (open/close, position, docking, title).
- `gts-panel-width` / `gts-panel-height` are used only by `rental_scheduler/static/rental_scheduler/js/entrypoints/panel_shell.js`.
- A single structured key makes migrations simpler and avoids “two sources of truth”.

**Back-compat strategy:**
- On first load after Phase 4, **read legacy** `gts-panel-width/height` and migrate into `jobPanelState.w/h`.

---

## 0) Current state (ground truth)

### Panel markup
- `rental_scheduler/templates/rental_scheduler/includes/panel.html`
  - Defines `#job-panel` and resize handle elements:
    - `#panel-resize-handle-right`
    - `#panel-resize-handle-bottom`
    - `#panel-resize-handle-corner`

### Panel behavior split across two files
- **Core panel behavior** (open/close, drag, unsaved tracking, load/showContent, workspace integration):
  - `rental_scheduler/static/rental_scheduler/js/panel.js`
- **Panel shell behaviors** (resize handles + refresh binding) extracted from the template:
  - `rental_scheduler/static/rental_scheduler/js/entrypoints/panel_shell.js`

### Persistence is currently split across keys
- `panel.js` persists `jobPanelState` with fields like `{ x, y, w, h, docked, title, isOpen }`.
  - Today: **w/h exist in the saved JSON but are not actually applied/maintained by resize logic.**
- `panel_shell.js` persists size separately:
  - `gts-panel-width`
  - `gts-panel-height`

### Alpine drift
- `panel.js` contains an Alpine component factory (`window.jobPanel = function jobPanel() { ... }`) and an Alpine detection path, but:
  - `base.html` does not load Alpine
  - the panel template does not use `x-data="jobPanel()"`

---

## 1) Work breakdown (prioritized, shippable increments)

### 4A) P0 — Make `jobPanelState` the single source of truth for panel persistence

**Primary files:**
- `rental_scheduler/static/rental_scheduler/js/panel.js`

**Tasks (panel.js)**
- **State schema**: standardize the canonical schema to (keep existing names for minimal churn):
  - `{ x, y, w, h, docked, title, isOpen }`
  - Interpret `w/h` as **pixel width/height**.
- **Migration in `load()`**:
  - Read `jobPanelState`.
  - If `w` or `h` missing/invalid:
    - Read legacy `gts-panel-width` / `gts-panel-height` via `GTS.storage.getRaw()`.
    - Coerce to numbers; clamp to min/max.
    - Write back to `jobPanelState`.
  - After successful migration, **remove** legacy keys (optional but recommended) to avoid drift.
- **Make `save(vm)` authoritative**:
  - Ensure `save()` writes correct `w/h` values.
  - Recommended approach: store `w/h` from `#job-panel.offsetWidth/offsetHeight` at save-time (so the state always matches DOM).
- **Apply saved size on init**:
  - On panel init, apply `w/h` to `#job-panel.style.width/height` (respect `min-*` and `max-*`).

**Acceptance checks**
- Resizing the panel, reloading, and re-opening preserves the size via `jobPanelState`.
- Existing users with `gts-panel-width/height` see no regression (values migrate).

---

### 4B) P0 — Move resize + refresh binding into `panel.js` and remove `panel_shell.js`

**Primary files:**
- `rental_scheduler/static/rental_scheduler/js/panel.js`
- `rental_scheduler/templates/base.html`
- `rental_scheduler/templates/rental_scheduler/includes/panel.html`

**Tasks**
- **Move resize logic**:
  - Port the resize code from `rental_scheduler/static/rental_scheduler/js/entrypoints/panel_shell.js` into `panel.js`.
  - Wire resize handlers to update `jobPanelState` (via `save()` / `vm.w/vm.h`).
  - Reuse/merge viewport constraint logic so “resize beyond viewport” stays sane.
- **Move refresh binding** (choose one implementation and delete the other):
  - **Option A (preferred)**: after `JobPanel.load()` sets `hx-get` and `hx-trigger="refresh"`, call `htmx.process(target)` so htmx binds the custom event trigger.
  - **Option B (conservative)**: keep a manual `refresh` event listener on `#job-panel .panel-body` that calls `htmx.ajax('GET', hxGet, {target: el})`.
- **Remove `panel_shell.js` load**:
  - Update `rental_scheduler/templates/base.html` to stop loading `entrypoints/panel_shell.js`.
- **Delete or retire file**:
  - Delete `rental_scheduler/static/rental_scheduler/js/entrypoints/panel_shell.js` once unused.
- **Template cleanup**:
  - Update `rental_scheduler/templates/rental_scheduler/includes/panel.html` to remove stale comments referencing `panel_shell.js`.
  - Consider removing `resize: horizontal;` on `#job-panel` if it conflicts with handle-based resizing (decide based on QA).

**Acceptance checks**
- Right/bottom/corner resize handles behave exactly as before.
- A `refresh` event on panel body still reloads content.
- No duplicate listeners / resize “speed up” after repeated usage.

---

### 4C) P0 — Remove Alpine compatibility code from `panel.js` (one implementation)

**Primary files:**
- `rental_scheduler/static/rental_scheduler/js/panel.js`

**Tasks**
- Remove Alpine detection / delayed init in `initPanel()`.
- Remove `isAlpineMode` and any Alpine-only logging.
- Delete the Alpine component factory:
  - `window.jobPanel = function jobPanel() { ... }`
- Remove Alpine-only helper functions that become dead after deleting `window.jobPanel`.

**Acceptance checks**
- `window.JobPanel` API remains stable (calendar/workspace continue to call it).
- Panel still:
  - opens/closes
  - drags
  - loads partials
  - tracks unsaved changes
  - integrates with workspace draft/minimize flows

---

### 4D) P1 — Remove leftover `x-data` / Alpine directives from templates

Because we’re choosing **“Alpine is not supported”**, any Alpine directives should be removed or replaced.

**Primary files:**
- `rental_scheduler/templates/rental_scheduler/workorders/workorder_detail.html`
- `rental_scheduler/templates/rental_scheduler/components/modal.html`

**Tasks**
- `workorder_detail.html`:
  - Replace the Alpine dropdown (`x-data`, `x-show`, `@click`) with either:
    - a native `<details>/<summary>` dropdown (no JS), or
    - a tiny vanilla click-toggle + click-away close handler (prefer a small page-level script include).
- `components/modal.html`:
  - First confirm whether it’s used (current repo search shows no includes).
  - If unused: delete it (and remove any references).
  - If intended for future use: rewrite to vanilla modal behavior, using either:
    - `<dialog>` + a small helper, or
    - a hidden overlay + `data-modal-*` attributes + helper.

**Acceptance checks**
- Work order “Print Options” dropdown works without Alpine.
- No `x-*` / `@click` Alpine directives remain in templates (unless Alpine is explicitly adopted later).

---

## 2) Suggested PR sequence (low-risk rollout)

1. **PR 1 (P0)**: Consolidate panel size persistence into `jobPanelState` + migrate legacy `gts-panel-width/height`.
2. **PR 2 (P0)**: Move resize/refresh into `panel.js`, remove `panel_shell.js` include, delete `panel_shell.js`, remove Alpine branch + `window.jobPanel`.
3. **PR 3 (P1)**: Template cleanup of Alpine directives (workorder dropdown + modal component decision).

---

## 3) Validation plan (Phase 4)

### Automated
- Run Playwright smoke: `tests/e2e/test_calendar_smoke.py` (covers panel open + draft/workspace flows).

### Manual checklist (high-signal)
- Calendar page:
  - Open job from event → panel opens.
  - Resize panel (all handles) → reload page → size persists.
  - Drag panel → reload page → position persists.
  - Save job → panel/workspace closes/minimizes as before; calendar refetch happens.
  - Minimize to workspace → restore tab → unsaved/draft HTML restore works.
  - Trigger any existing panel refresh mechanism → panel body reloads.
- Work order detail:
  - Print Options dropdown opens/closes and click-away works.

---

## 4) Explicit non-goals (Phase 4)
- Phase 5: URL cleanup / removing hard-coded endpoints.
- Phase 6: replacing HTML scraping (`fetch('/jobs') + DOMParser`) with purpose-built partial endpoints.
- Phase 7: formatting/linting/bundler tooling.
