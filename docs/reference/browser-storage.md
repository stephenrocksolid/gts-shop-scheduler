# Browser Storage Audit (localStorage + sessionStorage)

Last updated: 2025-12-22

This document audits **browser storage** usage in this repo, including both `localStorage` (persists across sessions) and `sessionStorage` (tab-scoped, clears on browser close).

## Design principles

1. **Minimize persistent sensitive data**: Draft HTML (which may contain customer PII) is stored in `sessionStorage`, not `localStorage`.
2. **Bounded growth**: Keys that could grow unboundedly (e.g., per-job warning flags) use a single JSON map with TTL and entry cap.
3. **Disabled third-party caching**: HTMX history cache is disabled to prevent HTML snapshots from persisting.
4. **Recoverable**: All GTS-related storage can be cleared via `GTS.storage.clearLocalData()`.

## Quick summary

| Risk Level | Key(s) | Notes |
|------------|--------|-------|
| **Low** | UI preferences (panel size, sidebar width, filters) | User-recoverable via UI interaction |
| **Low** | `gts-job-workspace` (metadata only) | No longer stores draft HTML |
| **Low** | `gts-job-initial-save-attempted` | Bounded JSON map with 90-day TTL, 500 entry cap |
| **Mitigated** | `cal-events-cache:*` | 5-minute TTL, auto-cleanup, max 5 entries |
| **Disabled** | `htmx-history-cache` | Disabled via `htmx_config.js` |
| **Removed** | `rental_env` / `rental_debug` | Cleaned up on load, no longer used |

## Inventory: keys, owners, and recovery

### UI preferences (localStorage - generally OK)

| Key / prefix | Owner (code) | Stored value | Expiry / cleanup | Recoverable in UI? |
|---|---|---|---|---|
| `jobPanelState` | `panel.js` | JSON: `{x,y,w,h,docked,title,isOpen}` | None; overwritten on change | **Mostly yes** (drag/resize/dock) |
| `gts-sidebar-width` | `calendar_page.js` | Raw number (px) | None; overwritten on resize | **Yes** (resize handle) |
| `job-list-filters` | `jobs_list_page.js` | JSON: `{calendars, dateFilter}` | None; overwritten on change | **Yes** (change filters) |
| `gts-calendar-current-date` | `calendar/layout.js` | ISO timestamp string | None; overwritten on navigation | **Yes** (calendar navigation) |
| `gts-calendar-search-open` | `calendar/layout.js` | `'true'/'false'` | None; overwritten on toggle | **Yes** (toggle search panel) |
| `gts-calendar-today-sidebar-open` | `calendar/today_sidebar.js` | `'true'/'false'` | None; overwritten on toggle | **Yes** (toggle Today sidebar) |
| `gts-calendar-filters` | `calendar/filters.js` | JSON: `{calendar,status,search}` | None; overwritten on change | **Yes** (change/clear filters) |
| `gts-selected-calendars` | `calendar/toolbar.js` | JSON array of calendar IDs | None; overwritten on change | **Yes** (calendar multi-select) |
| `gts-default-calendar` | `calendar/toolbar.js` | String calendar ID | None; overwritten on change | **Yes** (click calendar name) |

### Workspace state (localStorage - metadata only)

| Key | Owner (code) | Stored value | Expiry / cleanup | Notes |
|---|---|---|---|---|
| `gts-job-workspace` | `workspace.js` | JSON: `{schemaVersion: 2, jobs: [[id, metadata]...], activeJobId}` | None; user-driven cleanup via "Close All" | **No longer stores draft HTML** - only tab metadata (customerName, colors, flags). Schema version 2 introduced. |

### Draft HTML (sessionStorage - tab-scoped)

| Key prefix | Owner (code) | Stored value | Expiry / cleanup | Notes |
|---|---|---|---|---|
| `gts-job-workspace:html:<jobId>` | `workspace.js` | Sanitized HTML string | **Clears on browser close** (sessionStorage) | Draft form content for unsaved/minimized jobs. Capped at 100KB per job. Tab-scoped for security. |

### One-time warning tracking (localStorage - bounded)

| Key | Owner (code) | Stored value | Expiry / cleanup | Notes |
|---|---|---|---|---|
| `gts-job-initial-save-attempted` | `panel.js` | JSON: `{schemaVersion: 1, entries: {key: timestamp}}` | **90-day TTL**, max 500 entries | Replaced unbounded per-job keys. Cleaned on read/write. Legacy keys migrated automatically. |

### Caches (localStorage - time-bounded)

| Key prefix | Owner (code) | Stored value | Expiry / cleanup | Notes |
|---|---|---|---|---|
| `cal-events-cache:*` | `calendar/events.js` | JSON: `{events, signature, timestamp}` | **5-minute TTL**; max 5 keys | Enhanced cleanup removes expired entries opportunistically. |

### Disabled / Removed

| Key | Previous Owner | Status | Notes |
|---|---|---|---|
| `htmx-history-cache` | `htmx.min.js` | **Disabled** | `htmx_config.js` sets `historyCacheSize = 0` and clears existing cache on load. |
| `rental_env` | `config.js` | **Removed** | Cleaned up on load. No longer used for environment override. |
| `rental_debug` | `config.js` | **Removed** | Cleaned up on load. Debug mode now based solely on environment detection. |
| `gts-job-initial-save-attempted:*` | `panel.js` | **Migrated** | Legacy per-job keys migrated to bounded map and deleted. |

## Programmatic reset

All GTS-related storage can be cleared programmatically:

```javascript
// Clear all local data (returns { cleared: number, errors: string[] })
GTS.storage.clearLocalData();

// Reload to apply fresh state
location.reload();
```

This function is exposed in `rental_scheduler/static/rental_scheduler/js/shared/storage.js` and clears:
- Workspace metadata + sessionStorage draft HTML
- Warning map + legacy warning keys
- Calendar caches
- Panel state and UI preferences
- HTMX history cache
- Legacy debug overrides

## Configuration files

| File | Purpose |
|---|---|
| `shared/storage.js` | Storage helpers including `clearLocalData()` |
| `shared/htmx_config.js` | Disables HTMX history cache |
| `config.js` | Cleans up legacy `rental_env`/`rental_debug` keys |
| `workspace.js` | Manages workspace metadata (localStorage) + draft HTML (sessionStorage) |
| `panel.js` | Manages warning map with TTL/cap |
| `calendar/events.js` | Manages event cache with TTL cleanup |

## Migration notes

### v1 → v2 (workspace schema)

When loading workspace state with `schemaVersion < 2`:
1. If `unsavedHtml` exists in localStorage entries, migrate to sessionStorage
2. Save updated state with `schemaVersion: 2`
3. Future loads skip migration

### Legacy warning keys → bounded map

On load, `panel.js`:
1. Scans for `gts-job-initial-save-attempted:*` keys
2. Migrates values to the bounded map
3. Deletes legacy keys

## Developer notes

### Finding storage usages

Primary entry points:
- `GTS.storage` wrapper: `shared/storage.js`
- Job Panel persistence: `panel.js`
- Workspace persistence: `workspace.js`
- Calendar caching: `calendar/events.js`
- HTMX config: `shared/htmx_config.js`

### Adding new storage keys

When adding new localStorage/sessionStorage keys:
1. Document in this file
2. Consider if TTL/cap is needed
3. Add to `clearLocalData()` if user should be able to reset it
4. Prefer sessionStorage for sensitive/temporary data
