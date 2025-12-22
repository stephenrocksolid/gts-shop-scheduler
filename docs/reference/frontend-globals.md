# Frontend Globals / Contracts

Last updated: 2025-12-22

This document lists the **global JavaScript contracts** that other parts of the UI assume exist.
If you change these, update the docs and check for cross-file usages.

## `window.GTS` (namespace)

`base.html` ensures `window.GTS` exists and loads shared modules under it:

- `GTS.csrf` → `static/.../js/shared/csrf.js`
- `GTS.toast` → `static/.../js/shared/toast.js`
- `GTS.storage` → `static/.../js/shared/storage.js`
- `GTS.dom` → `static/.../js/shared/dom.js`
- `GTS.htmlState` → `static/.../js/shared/html_state.js`
- `GTS.urls` → injected by Django in `base.html`, helpers in `static/.../js/shared/urls.js`

See also: `docs/reference/urls-and-routing.md`.

## `window.JobPanel` (floating editor panel)

Defined in: `rental_scheduler/static/rental_scheduler/js/panel.js`

### Core methods

- `JobPanel.open()`: open the panel UI
- `JobPanel.close(skipUnsavedCheck)`: close; `skipUnsavedCheck=true` is used for minimize flows
- `JobPanel.load(url)`: HTMX-load a partial into the panel and open it
- `JobPanel.showContent(html)`: inject raw HTML (used for draft restore) and re-initialize form behaviors
- `JobPanel.setTitle(title)`: update panel title
- `JobPanel.setCurrentJobId(jobId)`: set the active job id for coordination with workspace
- `JobPanel.saveForm(callback)`: programmatically save the current form (used during job switching)
- `JobPanel.hasUnsavedChanges()`: boolean
- `JobPanel.clearUnsavedChanges()`: reset dirty-state tracking
- `JobPanel.trackFormChanges()`: attach dirty-state tracking to the current panel form
- `JobPanel.updateMinimizeButton()`: keep minimize button state in sync with workspace

### State fields / flags

- `JobPanel.currentDraftId`: set when a new job is minimized as a draft, used for draft promotion after save
- `JobPanel.currentJobId`: getter/setter that proxies to the internal panel instance
- `JobPanel.isSwitchingJobs`: used as a flag during programmatic saves to relax “human submit” validation (set dynamically)

## `window.JobWorkspace` (bottom tabs)

Defined in: `rental_scheduler/static/rental_scheduler/js/workspace.js` (class instance assigned to `window.JobWorkspace`)

### Core methods

- `JobWorkspace.openJob(jobId, meta)`: open job in panel + add tab
- `JobWorkspace.addJobMinimized(jobId, meta)`: add tab minimized without opening
- `JobWorkspace.switchToJob(jobId)`: restore tab and open the job in the panel
- `JobWorkspace.minimizeJob(jobId)`: mark minimized and close panel (skip unsaved check)
- `JobWorkspace.closeJob(jobId)`: remove tab; closes panel if it was active
- `JobWorkspace.updateJobMeta(jobId, meta)`: update tab label/color metadata

### Draft support

- `JobWorkspace.createDraft({ customerName, trailerColor, calendarColor, html })` → returns `draft-...` id
- `JobWorkspace.promoteDraft(draftId, realJobId, updatedMeta?)`
- `JobWorkspace.isDraftId(id)`
- `JobWorkspace.isUnsaved(id)`
- `JobWorkspace.getUnsavedHtml(id)`

## `window.jobCalendar` (calendar instance)

Defined in: `rental_scheduler/static/rental_scheduler/js/job_calendar.js` (calendar page only)

Important cross-component usage:

- Workspace tab hover tooltips call:
  - `jobCalendar.showEventTooltip(fakeEvent, anchorEl)`
  - `jobCalendar.hideEventTooltip()`

The bulk of calendar behavior is implemented via mixins under `static/.../js/calendar/*.js`.

## Legacy globals (kept for compatibility)

`base.html` also provides:

- `window.showToast(message, type?, duration?)` (wrapped by `GTS.toast.*`)
- `window.getCookie(name)` (wrapped by `GTS.csrf.getToken()` precedence rules)


