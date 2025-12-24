## Phase 3 Execution Plan — Split `job_calendar.js` into logical modules (keep `window.jobCalendar`)

Date: 2025-12-19

### Phase 3 goal
Refactor the **giant** calendar driver (`rental_scheduler/static/rental_scheduler/js/job_calendar.js`, ~4350 LOC) into smaller, navigable modules under `rental_scheduler/static/rental_scheduler/js/calendar/` **without changing behavior** and **without breaking** the existing global contract:

- `window.jobCalendar` remains the primary runtime object.
- Existing callers continue to work (workspace tooltips, entrypoints, panel flows).

### Phase 3 definition of done
- **`job_calendar.js` is mostly glue** (bootstrapping + applying modules + minimal facade).
- Calendar features live in `js/calendar/*` modules.
- **No feature regressions** (calendar UX, today sidebar, search panel toggle/layout, tooltips, call reminders, virtual recurrence materialize).
- Existing automated tests pass:
  - `tests/e2e/test_calendar_smoke.py`
  - `rental_scheduler/tests/test_partials.py`

### Constraints (Phase 3)
- **No bundler / no ES modules**: use plain scripts loaded in order.
- **Keep global contracts stable**:
  - `window.jobCalendar` object
  - `window.jobCalendar.calendar` (FullCalendar instance)
  - `window.calendarConfig` (injected by `calendar.html`)
- **Keep persistence keys unchanged** (localStorage key names/values).
- **No scope creep** into Phase 4+ (panel cleanup, URL policy cleanup, endpoint changes, bundler/linting).

---

## 0) Phase 3 audit notes (ground truth from current code)

### Key files involved
- **Primary**: `rental_scheduler/static/rental_scheduler/js/job_calendar.js`
- **Calendar entrypoint**: `rental_scheduler/static/rental_scheduler/js/entrypoints/calendar_page.js`
- **Workspace integration**: `rental_scheduler/static/rental_scheduler/js/workspace.js`
- **Templates**:
  - `rental_scheduler/templates/rental_scheduler/calendar.html` (loads `job_calendar.js` + `entrypoints/calendar_page.js`)

### External callers / contracts we must preserve
- `rental_scheduler/static/rental_scheduler/js/workspace.js`
  - calls `window.jobCalendar.showEventTooltip(fakeEvent, tabElement)`
  - calls `window.jobCalendar.hideEventTooltip()`
- `rental_scheduler/static/rental_scheduler/js/entrypoints/calendar_page.js`
  - reads `window.jobCalendar.searchPanelOpen`
  - calls `window.jobCalendar.toggleSearchPanel()`
  - calls `window.jobCalendar.selectAllCalendars()`
  - calls `window.jobCalendar.forceEqualWeekHeights()`
  - uses `window.jobCalendar.calendar.updateSize()`
- `rental_scheduler/static/rental_scheduler/js/entrypoints/job_form_partial.js`
  - uses `window.jobCalendar.calendar.refetchEvents()` after saves
- `rental_scheduler/templates/rental_scheduler/call_reminders/_call_reminder_form_partial.html`
  - uses `window.jobCalendar.calendar.refetchEvents()` after reminder submit

### Persistence keys used by `job_calendar.js` (must remain stable)
- `gts-calendar-search-open`
- `gts-calendar-today-sidebar-open`
- `gts-calendar-current-date`
- `gts-calendar-filters`
- `gts-selected-calendars`
- `gts-default-calendar`
- `cal-events-cache:*` (5 min TTL; keep last ~5 keys)

### Phase-3-relevant drift/bugs discovered during audit (resolve while splitting)
- **Duplicate FullCalendar config key**: `datesSet` is specified twice in `setupCalendar()`.
  - One value is `this.handleDatesSet.bind(this)`
  - Later overwritten by `datesSet: () => { this.saveCurrentDate(); this.scheduleUIUpdate(); }`
  - Net effect: `handleDatesSet(info)` is currently *effectively dead*.
- **Missing method reference**: `this.debouncedRefetchEvents()` is called twice, but no such method exists.
  - Present in `materializeAndOpenJob()` and `materializeAndShowCallReminder()`
  - Must be replaced with the intended method (`debouncedRefetch()` or `calendar.refetchEvents()`), preserving current UX.
- **(Phase 5, out-of-scope but relevant context)**: `updateJobStatus()` still posts to a hard-coded `/rental_scheduler/api/...` URL.
  - Do **not** change URL policy in Phase 3; just keep this in mind while moving code.

---

## 1) JobCalendar method inventory (for precise extraction)

This list is the **mechanical map** from the current monolith to the new modules.
Line numbers below refer to `rental_scheduler/static/rental_scheduler/js/job_calendar.js`.

### Lifecycle / FullCalendar wiring
- `constructor` (11)
- `initialize` (103)
- `initializeElements` (114)
- `setupCalendar` (126)
- `setupEventListeners` (1977)
- `destroy` (4332)

### Layout + sizing + wheel navigation
- `ensureCalendarVisible` (709)
- `adjustHeaderColumnWidths` (725)
- `scheduleUIUpdate` (754)
- `forceEqualWeekHeights` (770)
- `_applyWeekHeights` (786)
- `setupResizeObserver` (823) *(currently disabled; keep behavior)*
- `enableDayCellScrolling` (1995) *(scroll wheel navigates by week)*
- `adjustSundayColumnWidth` (1284)

### Today sidebar
- `toggleTodaySidebar` (4296)
- `applyTodaySidebarState` (4313)
- `renderTodayPanel` (959)
- `initializeDatePickerControls` (1173)
- `focusEventInCalendar` (1273)
- Helpers used by Today panel:
  - `startOfDay` (844)
  - `endOfDay` (860)
  - `isSameDay` (866)
  - `formatDateForInput` (853)
  - `eventOverlapsDay` (934)
  - `_dateKey` (875)
  - `_buildEventDayIndex` (884)
  - `_getEventsForDay` (925)

### Toolbar controls (jump-to-date, calendar multi-select, status dropdown)
- `styleCustomButtons` (1315)
- `addJumpToDateControl` (1341)
- `initializeJumpToDate` (1834)
- `createCalendarMultiSelect` (1570)
- `updateCalendarButtonText` (1811)
- `initializeMovedCalendarDropdown` (1949)
- `initializeMovedStatusDropdown` (1963)
- `selectAllCalendars` (4141)

### Filter state persistence
- `loadSavedFilters` (2539)
- `initializeSelectedCalendars` (2572)
- `saveFilters` (2611)
- `updateURLParams` (2627)
- `clearFilters` (2662)
- `handleFilterChange` (2687)
- `handleDatesSet` (2702) *(currently shadowed by duplicate FullCalendar key)*

### Event fetching + caching (stale-while-revalidate)
- `_buildEventsCacheKey` (2049)
- `_computeEventsSignature` (2067)
- `_getCachedEvents` (2103)
- `_setCachedEvents` (2126)
- `_touchCacheTimestamp` (2149)
- `_cleanupEventCache` (2165)
- `fetchEvents` (2203)
- `_backgroundRefetch` (2414)
- `invalidateEventsCache` (2500)
- `debouncedRefetch` (2521)
- `refreshCalendar` (4085)
- `loadCalendarData` (4098)
- `showLoading` (4105)
- `hideLoading` (4114)
- `updateNoCalendarsOverlay` (4124)

### Tooltips
- `showEventTooltip` (2710)
- `hideEventTooltip` (2976)
- `showJobRowTooltip` (2987) *(currently unused; keep until proven dead)*
- `handleEventMouseEnter` (3027)
- `handleEventMouseLeave` (3043)

### Event interactions (panel/workspace integration)
- `handleEventClick` (3057)
- `openJobInPanel` (3164)
- `showUnsavedChangesDialog` (3324)

### Day interactions (popover + double-click create)
- `setupDayNumberClicks` (307)
- `showDayEventsPopover` (487)
- `openCreateFormForDate` (419)
- `handleDateClick` (3812)

### Rendering / styling
- `handleEventMount` (3896)
- `lightenColor` (3940)
- `getEventClassNames` (3961)
- `renderEventContent` (3978)
- `renderDayCellContent` (4011)

### Virtual recurrence materialization
- `materializeAndOpenJob` (3190)
- `materializeAndShowCallReminder` (3258)

### Call reminders
- `showCallReminderPanel` (3489)
- `markCallReminderComplete` (3620)
- `saveJobReminderNotes` (3654)
- `openJobFromReminder` (3695)
- `saveStandaloneReminderNotes` (3705)
- `markStandaloneReminderComplete` (3739)
- `deleteStandaloneReminder` (3774)

### Misc utilities
- `saveCurrentDate` (743)
- `getSavedDate` (831)
- `showToast` (4176) *(calendar-local wrapper; currently delegates to global/shared)*
- `getCSRFToken` (4191) *(delegates to `GTS.csrf.getToken()` when present)*
- `debounce` (4200)
- `showError` (4217)
- `showSuccess` (4232)
- `toggleSearchPanel` (4244)
- `updateJobStatus` (4044)

---

## 2) Target Phase 3 file layout (no bundler)

Create:

- `rental_scheduler/static/rental_scheduler/js/calendar/`
  - `registry.js` *(mixin registry / module wiring)*
  - `utils.js`
  - `core.js`
  - `layout.js`
  - `toolbar.js`
  - `filters.js`
  - `events.js`
  - `today_sidebar.js`
  - `tooltips.js`
  - `rendering.js`
  - `day_interactions.js`
  - `job_actions.js`
  - `recurrence_virtual.js`
  - `call_reminders.js`

Keep:
- `rental_scheduler/static/rental_scheduler/js/job_calendar.js` as the stable “entrypoint” loaded by `calendar.html`, but shrink it down so it:
  - defines the `JobCalendar` class (eventually minimal)
  - applies registered mixins
  - instantiates and assigns `window.jobCalendar`

### Why a registry/mixin approach
Without a bundler, we still need modularity. The safest, incremental strategy is:
- `calendar/*.js` files **register** a mixin with `GTS.calendar.register(name, fn)`.
- `job_calendar.js` defines the class and calls `GTS.calendar.applyMixins(JobCalendar)`.

This avoids fragile script ordering constraints (modules can load before the class exists), and enables **incremental extraction** (move one feature group at a time).

### Script load order (update `calendar.html`)
Update `rental_scheduler/templates/rental_scheduler/calendar.html` `{% block extra_js %}` so it loads:

- `js/calendar/registry.js`
- all `js/calendar/*.js` modules (order doesn’t matter once registry exists, but keep it consistent)
- `js/job_calendar.js` (applies mixins + instantiates)
- `js/entrypoints/calendar_page.js`

Keep the cache-busting query param style already used (`?v={{ timestamp|default:'1' }}`).

---

## 3) Detailed, prioritized execution plan (Phase 3 only)

### 3A) Scaffolding: calendar registry + safe bootstrapping (P0)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/registry.js`
- **Update** `rental_scheduler/templates/rental_scheduler/calendar.html`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

**Tasks**
- Implement `GTS.calendar.register(name, fn)` + `GTS.calendar.applyMixins(JobCalendar)`.
- Update `job_calendar.js` so it:
  - calls `GTS.calendar.applyMixins(JobCalendar)` before instantiation
  - keeps instantiation timing identical (still on DOM ready)
- Add a small runtime assertion (dev-only `console.warn` is fine) to log if critical prototype methods are missing before instantiation (helps catch missing module loads during Phase 3).

**Acceptance checks**
- Calendar page loads with zero behavior changes.
- `window.jobCalendar` still exists and `window.jobCalendar.calendar` is created.

---

### 3B) Extract shared utilities used across calendar modules (P0)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/utils.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

**Move (as methods on `JobCalendar.prototype`)**
- `showToast` (4176)
- `getCSRFToken` (4191)
- `debounce` (4200)
- `showError` (4217)
- `showSuccess` (4232)

**Notes**
- Keep current semantics: `showError/showSuccess` prefer `GTS.toast.*` when present.
- Do not change storage keys.

**Acceptance checks**
- No changes in toast appearance/behavior.
- No changes in CSRF behavior for POSTs.

---

### 3C) Extract layout + sizing + search-panel toggle (P0)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/layout.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

**Move**
- Layout/sizing:
  - `ensureCalendarVisible` (709)
  - `adjustHeaderColumnWidths` (725)
  - `scheduleUIUpdate` (754)
  - `forceEqualWeekHeights` (770)
  - `_applyWeekHeights` (786)
  - `setupResizeObserver` (823) *(keep disabled behavior)*
  - `enableDayCellScrolling` (1995) *(wheel → week navigation)*
- Date-position persistence:
  - `saveCurrentDate` (743)
  - `getSavedDate` (831)
- Search panel layout toggle (search functionality remains in `entrypoints/calendar_page.js`):
  - `toggleSearchPanel` (4244)
**Acceptance checks**
- `window.jobCalendar.forceEqualWeekHeights()` still exists (used by `entrypoints/calendar_page.js`).
- Scroll wheel still navigates weeks.
- Search panel toggle still resizes the calendar and persists open/closed state.

---

### 3D) Extract event fetching + cache subsystem (P0)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/events.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

**Move**
- Cache helpers: `_buildEventsCacheKey` (2049), `_computeEventsSignature` (2067), `_getCachedEvents` (2103), `_setCachedEvents` (2126), `_touchCacheTimestamp` (2149), `_cleanupEventCache` (2165)
- Fetching: `fetchEvents` (2203), `_backgroundRefetch` (2414)
- Refresh/invalidate: `invalidateEventsCache` (2500), `debouncedRefetch` (2521), `refreshCalendar` (4085), `loadCalendarData` (4098)
- Loading/overlays: `showLoading` (4105), `hideLoading` (4114), `updateNoCalendarsOverlay` (4124)

**Phase-3 bug fix included here (required for correctness)**
- Replace missing `debouncedRefetchEvents()` calls (3244, 3310) with the intended refresh method:
  - Prefer `this.debouncedRefetch()` (keeps existing debounce behavior)
  - If behavior needs to be “immediate”, use `this.calendar.refetchEvents()` (but keep existing debouncing elsewhere)

**Acceptance checks**
- Reloading the calendar still uses cached events instantly (when available) and revalidates.
- Selecting/deselecting calendars still avoids network fetch when none are selected.

---

### 3E) Extract Today sidebar subsystem (P1)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/today_sidebar.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

**Move**
- Sidebar state: `toggleTodaySidebar` (4296), `applyTodaySidebarState` (4313)
- Today render + picker: `renderTodayPanel` (959), `initializeDatePickerControls` (1173), `focusEventInCalendar` (1273)
- Event indexing helpers: `_dateKey` (875), `_buildEventDayIndex` (884), `_getEventsForDay` (925)
- Date helpers: `startOfDay` (844), `endOfDay` (860), `isSameDay` (866), `formatDateForInput` (853), `eventOverlapsDay` (934)

**Acceptance checks**
- Today sidebar open/close persists.
- Today list renders correctly and clicking an item opens/switches job as before.

---

### 3F) Extract tooltip subsystem (P1)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/tooltips.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`
- **(No caller changes)**: keep `showEventTooltip/hideEventTooltip` names stable for workspace.

**Move**
- `showEventTooltip` (2710)
- `hideEventTooltip` (2976)
- `handleEventMouseEnter` (3027)
- `handleEventMouseLeave` (3043)
- `showJobRowTooltip` (2987) *(keep, even if unused, until explicitly removed)*

**Acceptance checks**
- Hover tooltips still appear for:
  - calendar events
  - today sidebar items
  - workspace tabs

---

### 3G) Extract rendering/styling logic for FullCalendar events (P1)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/rendering.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

**Move**
- `handleEventMount` (3896)
- `getEventClassNames` (3961)
- `renderEventContent` (3978)
- `renderDayCellContent` (4011)
- `lightenColor` (3940)

**Acceptance checks**
- Completed/canceled styling remains identical.
- E2E test selectors relying on `data-gts-*` attributes still exist.

---

### 3H) Extract day interactions (popover + double-click create) (P1)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/day_interactions.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

**Move**
- `setupDayNumberClicks` (307)
- `showDayEventsPopover` (487)
- `openCreateFormForDate` (419)
- `handleDateClick` (3812)

**Acceptance checks**
- Clicking day number shows event popover.
- Double-click in cell opens the correct form (job vs call reminder rule).
- No duplicate open on double-click (guard via `lastOpenedDateByDoubleClick`).

---

### 3I) Extract toolbar UI (jump-to-date, calendar multi-select, status dropdown) (P2)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/toolbar.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

**Move**
- `styleCustomButtons` (1315)
- `addJumpToDateControl` (1341)
- `initializeJumpToDate` (1834)
- `createCalendarMultiSelect` (1570)
- `updateCalendarButtonText` (1811)
- `initializeMovedCalendarDropdown` (1949)
- `initializeMovedStatusDropdown` (1963)
- `selectAllCalendars` (4141)
- `adjustSundayColumnWidth` (1284)

**Acceptance checks**
- Toolbar renders identically.
- Multi-calendar selection persists (`gts-selected-calendars`, `gts-default-calendar`).
- “Select All Calendars” overlay button still works.

---

### 3J) Extract filter state persistence (P2)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/filters.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

**Move**
- `loadSavedFilters` (2539)
- `initializeSelectedCalendars` (2572)
- `saveFilters` (2611)
- `updateURLParams` (2627)
- `clearFilters` (2662)
- `handleFilterChange` (2687)
- `handleDatesSet` (2702)

**Phase-3 bug fix included here (required for correctness)**
- Remove/merge the duplicate `datesSet` FullCalendar config value in `setupCalendar()`.
  - Ensure the final `datesSet` handler does everything needed:
    - save date for persistence
    - schedule UI update
    - update `currentFilters.month/year` if that is still used

**Acceptance checks**
- URL params still update as before.
- No regression in calendar navigation persistence.

---

### 3K) Extract event click → panel/workspace behaviors (P2)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/job_actions.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

**Move**
- `handleEventClick` (3057)
- `openJobInPanel` (3164)
- `showUnsavedChangesDialog` (3324)
- `updateJobStatus` (4044) *(keep URL behavior unchanged in Phase 3)*

**Acceptance checks**
- Clicking a job event opens panel/workspace correctly.
- Unsaved-changes dialog path behaves identically.

---

### 3L) Extract virtual recurrence + call reminders (P2)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/recurrence_virtual.js`
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/call_reminders.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

**Move**
- Recurrence:
  - `materializeAndOpenJob` (3190)
  - `materializeAndShowCallReminder` (3258)
- Call reminders:
  - `showCallReminderPanel` (3489)
  - `markCallReminderComplete` (3620)
  - `saveJobReminderNotes` (3654)
  - `openJobFromReminder` (3695)
  - `saveStandaloneReminderNotes` (3705)
  - `markStandaloneReminderComplete` (3739)
  - `deleteStandaloneReminder` (3774)

**Acceptance checks**
- Virtual occurrences still materialize and open the resulting job/reminder.
- Reminder save/complete/delete still refreshes calendar and closes panel as before.

---

### 3M) Extract lifecycle + FullCalendar wiring (P2)

**Files**
- **Add** `rental_scheduler/static/rental_scheduler/js/calendar/core.js`
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`

**Move**
- `initialize` (103)
- `initializeElements` (114)
- `setupCalendar` (126)
- `setupEventListeners` (1977)
- `destroy` (4332)

**Notes**
- After this step, `job_calendar.js` should ideally contain only:
  - the `JobCalendar` constructor (state initialization)
  - applying mixins
  - DOM-ready instantiation

**Acceptance checks**
- FullCalendar still initializes with the same configuration.
- Existing callbacks remain bound correctly (especially `fetchEvents`, `handleDateClick`, `eventContent`, and tooltip handlers).

---

### 3N) Final consolidation: shrink `job_calendar.js` to glue (P2)
**Files**
- **Update** `rental_scheduler/static/rental_scheduler/js/job_calendar.js`
- **Update** `rental_scheduler/templates/rental_scheduler/calendar.html`

**Tasks**
- Ensure `job_calendar.js` contains only:
  - `class JobCalendar` with minimal state + constructor
  - the DOM-ready bootstrap
  - `GTS.calendar.applyMixins(JobCalendar)` call
- Ensure all moved methods exist in exactly one place (avoid duplicates).
- Ensure calendar template loads `calendar/registry.js` + all modules before `job_calendar.js`.

**Acceptance checks**
- `job_calendar.js` is “mostly glue”.
- All automated tests pass.

---

## 4) Validation plan (Phase 3)

### Automated
- Run the existing suite (Phase 0 safety net is already in place):
  - `tests/e2e/test_calendar_smoke.py`
  - `rental_scheduler/tests/test_partials.py`

### Manual (high-signal quick checks)
- Calendar loads (no console errors).
- Scroll wheel navigates weeks.
- Search panel toggle works and resizes calendar.
- Today sidebar toggle works; today list renders.
- Hover tooltips work on:
  - calendar events
  - today list items
  - workspace tabs
- Double-click day cell opens correct form.
- Call reminder open/save/complete/delete works.
- Virtual occurrence materialize works.

---

## 5) Explicit non-goals (Phase 3)
- Phase 4: panel refactor/persistence consolidation
- Phase 5: URL cleanup / removing hard-coded endpoints
- Phase 6: replacing HTML scraping (`fetch('/jobs') + DOMParser`) with purpose-built partial endpoints
- Phase 7: prettier/eslint/bundler tooling
