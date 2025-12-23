# Recurring Events API

Last updated: 2025-12-22

## Overview
The recurring events API provides full support for Google Calendar-like recurring job management.

## Status: ✅ IMPLEMENTED

All backend functionality is complete and ready to use:
- ✅ Database migrations applied
- ✅ Model methods implemented
- ✅ API endpoints created
- ✅ Calendar data includes recurring info

---

## API Endpoints

### 1. Create Job with Recurrence

**Endpoint:** `POST /api/jobs/create/`

**Request Body:**
```json
{
  "business_name": "ABC Monthly Service",
  "contact_name": "John Doe",
  "phone": "555-1234",
  "start": "2025-01-01T09:00:00",
  "end": "2025-01-01T17:00:00",
  "allDay": false,
  "status": "uncompleted",
  "notes": "Regular monthly service",
  "calendar_id": 1,
  "recurrence": {
    "enabled": true,
    "type": "monthly",
    "interval": 1,
    "count": 12,
    "until_date": "2025-12-31"
  }
}
```

**Recurrence Parameters:**
- `enabled` (boolean): Whether to create recurring instances
- `type` (string): `"monthly"`, `"yearly"`, `"weekly"`, or `"daily"`
- `interval` (integer): How often (e.g., `2` = every 2 months)
- `count` (integer, optional): Maximum number of instances to create
- `until_date` (string, optional): Don't create instances after this date (YYYY-MM-DD)

**Response:**
```json
{
  "id": 123,
  "business_name": "ABC Monthly Service",
  "start": "2025-01-01T09:00:00",
  "end": "2025-01-01T17:00:00",
  "is_recurring_parent": true,
  "is_recurring_instance": false,
  "recurrence_rule": {
    "type": "monthly",
    "interval": 1,
    "count": 12
  },
  "recurrence_created": true
}
```

---

### 2. Update Job with Scope

**Endpoint:** `POST /api/jobs/<id>/update/`

**Request Body:**
```json
{
  "business_name": "Updated Business Name",
  "phone": "555-9999",
  "update_scope": "this_and_future"
}
```

**Update Scopes:**
- `"this_only"`: Update only this job (default)
- `"this_and_future"`: Update this job and all future instances
- `"all"`: Update parent and all instances in the series

**Response:**
```json
{
  "id": 124,
  "business_name": "Updated Business Name",
  "phone": "555-9999",
  "instances_updated": 10,
  "update_scope": "this_and_future"
}
```

---

### 3. Cancel Future Recurrences

**Endpoint:** `POST /api/jobs/<id>/cancel-future/`

**Request Body:**
```json
{
  "from_date": "2025-06-01"
}
```

This cancels all recurring instances on or after the specified date.

**Response:**
```json
{
  "success": true,
  "canceled_count": 4,
  "end_recurrence_date": "2025-06-01",
  "parent_id": 123
}
```

---

### 4. Delete with Scope (Soft Delete)

**Endpoint:** `POST /api/jobs/<id>/delete-recurring/`

**Request Body:**
```json
{
  "delete_scope": "this_only"
}
```

**Delete Scopes:**
- `"this_only"`: Soft delete only this job (default). **Note:** Deleting only the parent is rejected with 400 error if instances exist.
- `"this_and_future"`: Soft delete this and all future instances. Also truncates `end_recurrence_date` to prevent virtual occurrences from being generated beyond the deleted boundary.
  - For instances: Sets parent's `end_recurrence_date` to day before the deleted instance
  - For parent: Deletes all instances and sets `end_recurrence_date` to parent's start date (keeps parent itself)
- `"all"`: Soft delete entire series (parent + all instances)

**Important:** This endpoint uses **soft delete** (`is_deleted=True`) instead of hard delete to:
- Prevent cascading deletes of related objects (WorkOrders, CallReminders)
- Keep deleted occurrences in DB so calendar feed can avoid re-emitting them as virtual occurrences
- Maintain consistency with the rest of the app's delete behavior

**Response:**
```json
{
  "success": true,
  "deleted_count": 5,
  "scope": "this_and_future"
}
```

**Error Response (attempting to delete parent only):**
```json
{
  "status": "error",
  "error": "Cannot delete only the series template. Choose to delete the entire series or delete this and future events."
}
```

**Legacy Support:**

The backend also accepts DELETE method with query parameter:

`DELETE /api/jobs/<id>/delete-recurring/?scope=<scope>`

However, POST with JSON body is preferred for consistency.

---

### 5. Materialize Virtual Occurrence (Forever Series)

The calendar feed can include **virtual** occurrences for never-ending series. This endpoint creates (or returns) the real `Job` row for a specific occurrence.

**How virtual occurrences work:**

- Forever series (with `recurrence_rule.end === 'never'`) don't pre-generate all instances as DB rows
- Instead, the calendar feed generates `virtual_job` and `virtual_call_reminder` events on-the-fly for the requested date window
- Virtual occurrences work correctly for windows far into the future (4+ years ahead) thanks to a fast-forward optimization
- When a user clicks on a virtual occurrence, the frontend calls this endpoint to "materialize" it into a real Job row

**Endpoint:** `POST /api/recurrence/materialize/`

**Request Body:**

```json
{
  "parent_id": 123,
  "original_start": "2026-02-20T10:00:00"
}
```

**Response:**

```json
{
  "job_id": 456,
  "created": true,
  "job": { "id": 456, "recurrence_parent_id": 123, "...": "..." }
}
```

---

### 6. Preview Upcoming Occurrences (Forever Series)

Returns an HTML fragment containing the next N virtual occurrences for a forever recurring series. Used by the Jobs list and Calendar Search Panel to show expandable preview rows.

**Endpoint:** `GET /api/recurrence/preview/`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parent_id` | int | Yes | ID of the forever recurring parent job |
| `count` | int | No | Number of occurrences to return (default: 5, max: 200) |

**Response:** HTML fragment containing `<tr>` elements for each virtual occurrence.

Each virtual occurrence row includes:

- `data-virtual="1"` - Marks the row as a virtual occurrence
- `data-recurrence-parent-id` - The parent job ID
- `data-recurrence-original-start` - ISO datetime for the occurrence start
- `data-parent-row-id` - Reference to the parent row for JS manipulation

**Load-More Behavior:**

- For forever series, a "Show 5 more" button is always displayed until the maximum count (200) is reached
- Users can repeatedly click "Show more" to incrementally load additional occurrences
- This avoids loading hundreds of occurrences at once while still allowing deep exploration

**Error Responses:**

- `400` - Missing `parent_id`, job is not a forever series, or job is an instance (not a parent)
- `404` - Job not found

---

### 7. Series Occurrences (Grouped Search)

Returns an HTML fragment with materialized + virtual occurrences for a recurring series, filtered by search query and scope. Used by the Jobs list when search is active to expand series header rows.

**Endpoint:** `GET /api/recurrence/series-occurrences/`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parent_id` | int | Yes | ID of the recurring parent job |
| `scope` | string | Yes | `upcoming` or `past` - which occurrences to return |
| `search` | string | No | Search query to filter occurrences |
| `count` | int | No | Number of occurrences to return (default: 10, max: 50) |
| `offset` | int | No | Offset for pagination (default: 0) |

**Response:** HTML fragment containing `<tr>` elements for each occurrence.

Each occurrence row includes:

- `data-series-id` - The parent job ID
- `data-series-scope` - The scope (`upcoming` or `past`)
- `data-job-id` - For materialized jobs, the job ID
- `data-virtual="1"` - For virtual occurrences only

**Behavior:**

- Returns materialized occurrences (parent + instances) filtered by search and scope
- For forever series where parent matches search, also returns virtual occurrences
- Supports pagination with `offset` and `count` parameters
- Includes "Show more" button when more results are available

**Error Responses:**

- `400` - Missing `parent_id`, invalid scope, or job is an instance (not a parent)
- `404` - Job not found

---

### 8. Get Calendar Data (Updated)

**Endpoint:** `GET /api/job-calendar-data/`

**Response:** Now includes recurring event information

```json
{
  "status": "success",
  "events": [
    {
      "id": "job-123",
      "title": "ABC Monthly Service - 555-1234",
      "start": "2025-01-01T09:00:00",
      "end": "2025-01-01T17:00:00",
      "allDay": false,
      "extendedProps": {
        "job_id": 123,
        "status": "uncompleted",
        "business_name": "ABC Monthly Service",
        "is_recurring_parent": true,
        "is_recurring_instance": false,
        "recurrence_parent_id": null,
        "recurrence_rule": {
          "type": "monthly",
          "interval": 1,
          "count": 12
        },
        "repeat_type": "monthly",
        "repeat_n_months": 1
      }
    },
    {
      "id": "job-124",
      "title": "ABC Monthly Service - 555-1234",
      "start": "2025-02-01T09:00:00",
      "end": "2025-02-01T17:00:00",
      "allDay": false,
      "extendedProps": {
        "job_id": 124,
        "status": "uncompleted",
        "business_name": "ABC Monthly Service",
        "is_recurring_parent": false,
        "is_recurring_instance": true,
        "recurrence_parent_id": 123,
        "recurrence_rule": null
      }
    }
  ]
}
```

---

## Frontend Integration Examples

**Important (project rule):** this codebase forbids hard-coded app URLs in JS. If you add frontend code that calls these endpoints, inject them into `window.GTS.urls` (in `base.html`) and call them via the `GTS.urls.*` helpers (see `docs/reference/urls-and-routing.md`).

### Detecting Recurring Events

```javascript
// In calendar event rendering
if (event.extendedProps.is_recurring_parent) {
    // This is a parent - show recurring icon
    addRecurringIndicator(element, '🔄');
} else if (event.extendedProps.is_recurring_instance) {
    // This is an instance - show lighter indicator
    addRecurringIndicator(element, '↻');
}
```

### Creating a Recurring Event

```javascript
const formData = {
    business_name: document.getElementById('business_name').value,
    start: document.getElementById('start_dt').value,
    end: document.getElementById('end_dt').value,
    // ... other fields
    recurrence: {
        enabled: document.getElementById('recurrence_enabled').checked,
        type: document.getElementById('recurrence_type').value,
        interval: parseInt(document.getElementById('recurrence_interval').value),
        count: parseInt(document.getElementById('recurrence_count').value),
    }
};

fetch('/api/jobs/create/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify(formData)
})
.then(response => response.json())
.then(data => {
    if (data.recurrence_created) {
        console.log('Created recurring series!');
    }
    calendar.refetchEvents();
});
```

### Editing with Scope Selection

```javascript
// Show scope options when editing a recurring event
if (event.extendedProps.is_recurring_instance) {
    showScopeDialog([
        { value: 'this_only', label: 'Edit this event only' },
        { value: 'this_and_future', label: 'Edit this and following events' },
        { value: 'all', label: 'Edit all events in series' }
    ], (scope) => {
        updateJob(event.extendedProps.job_id, {
            ...formData,
            update_scope: scope
        });
    });
}
```

### Canceling Future Occurrences

```javascript
function cancelFutureRecurrences(jobId, fromDate) {
    fetch(`/api/jobs/${jobId}/cancel-future/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
            from_date: fromDate
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(`Canceled ${data.canceled_count} future occurrences`);
        calendar.refetchEvents();
    });
}
```

### Deleting with Scope

**Recommended Implementation (with modal):**

The app includes a built-in recurring delete modal in `job_form_partial.js` that:
- Automatically detects recurring jobs from the form DOM
- Shows appropriate options for instances vs. parent
- Uses user-friendly copy (no internal terms)
- Handles all scope logic

```javascript
// Automatic detection and modal - already implemented in job_form_partial.js
function deleteJob(jobId) {
    var recurrenceState = detectRecurrenceState();
    
    if (recurrenceState.isRecurring) {
        showRecurringDeleteModal(jobId, recurrenceState.isInstance);
    } else {
        // Simple confirm for non-recurring jobs
        if (confirm('Are you sure you want to delete this job?')) {
            fetch(GTS.urls.jobDelete(jobId), { method: 'POST', ... });
        }
    }
}
```

**Manual Implementation (if needed):**

```javascript
function deleteWithScope(jobId, scope) {
    fetch(GTS.urls.jobDeleteRecurring(jobId), {
        method: 'POST',
        headers: GTS.csrf.headers({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ delete_scope: scope })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            GTS.showToast(`Deleted ${data.deleted_count} event(s)`, 'success');
            if (window.jobCalendar && window.jobCalendar.calendar) {
                window.jobCalendar.calendar.refetchEvents();
            }
        } else {
            GTS.showToast('Failed to delete: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting job:', error);
        GTS.showToast('Error deleting job', 'error');
    });
}
```

---

## Testing

Run the test suite:
```bash
python manage.py test_recurring
```

This verifies:
- Creating recurring instances
- Marking instances complete independently
- Canceling future occurrences
- Cascade deletion

---

## Error Handling

### Common Errors

**1. No active calendar found**
```json
{
  "error": "No active calendar found"
}
```
**Solution:** Ensure at least one Calendar exists with `is_active=True`

**2. Invalid date format**
```json
{
  "error": "Invalid date format: ..."
}
```
**Solution:** Use ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`

**3. This job is not part of a recurring series**
```json
{
  "error": "This job is not part of a recurring series"
}
```
**Solution:** Only call cancel-future on jobs with `is_recurring_parent=true` or `is_recurring_instance=true`

---

## Database Schema Reference

### New Fields on Job Model

- `recurrence_rule` (JSONField): Stores the recurrence pattern
- `recurrence_parent_id` (ForeignKey): Links to parent job
- `recurrence_original_start` (DateTimeField): Original start date of this instance
- `end_recurrence_date` (DateField): Stops generating after this date
- `status` (CharField): Now includes `'canceled'` option

### Indexes

- `job_recur_idx`: Index on `(recurrence_parent, recurrence_original_start)` for fast queries

---

## Frontend status

Recurring UI (including virtual occurrence materialization) is implemented in the current frontend.

References:

- `docs/architecture/frontend.md`
- `rental_scheduler/static/rental_scheduler/js/calendar/recurrence_virtual.js`
