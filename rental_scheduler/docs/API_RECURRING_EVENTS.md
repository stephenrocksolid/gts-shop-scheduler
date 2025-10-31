# Recurring Events API Documentation

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

### 4. Delete with Scope

**Endpoint:** `DELETE /api/jobs/<id>/delete-recurring/?scope=<scope>`

**Query Parameters:**
- `scope`: One of `"this_only"`, `"all"`, or `"future"`

**Scopes:**
- `this_only`: Delete only this job (default)
- `all`: Delete entire series (parent + all instances)
- `future`: Delete this and all future instances

**Response:**
```json
{
  "success": true,
  "deleted_count": 5,
  "scope": "future"
}
```

---

### 5. Get Calendar Data (Updated)

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

```javascript
function deleteWithScope(jobId, scope) {
    if (!confirm(`Delete ${scope === 'all' ? 'entire series' : scope}?`)) {
        return;
    }
    
    fetch(`/api/jobs/${jobId}/delete-recurring/?scope=${scope}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    .then(response => response.json())
    .then(data => {
        alert(`Deleted ${data.deleted_count} job(s)`);
        calendar.refetchEvents();
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

## Next Steps for Frontend

1. **Add Recurring UI to Job Form**
   - Checkbox: "Make this a recurring event"
   - Dropdown: Recurrence type (Monthly, Yearly, etc.)
   - Input: Interval (Every N months/years)
   - Input: End after X occurrences or by date

2. **Show Recurring Indicators**
   - Add icon/badge to recurring events on calendar
   - Distinguish between parent and instance events

3. **Update Edit Dialog**
   - Show scope options for recurring instances
   - Add "Cancel future occurrences" button
   - Add "Delete series" option

4. **Update Delete Dialog**
   - Show scope options (this only, all, future)
   - Warn user about cascade effects

5. **Add Recurrence Info Panel**
   - Show recurrence pattern in job details
   - Link to parent event
   - Show occurrence number (e.g., "3 of 12")







