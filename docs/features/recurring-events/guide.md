# Recurring Events (Guide)

Last updated: 2025-12-22

## Overview

This document describes the Google Calendar-like recurring event system implemented in the GTS Scheduler.

See also:

- API reference: `docs/features/recurring-events/api.md`

## Database Schema

### New Job Model Fields

1. **`recurrence_rule`** (JSONField): Stores the recurrence pattern
   ```json
   {
     "type": "monthly|yearly|weekly|daily",
     "interval": 2,           // Every 2 months/years/weeks/days
     "count": 12,             // Generate 12 occurrences
     "until_date": "2025-12-31",  // Don't generate after this date (optional)
     "end": "never"               // Optional: marks a “forever” series (virtual occurrences)
   }
   ```

2. **`recurrence_parent`** (ForeignKey): Links child instances to parent job

3. **`recurrence_original_start`** (DateTimeField): Tracks which occurrence this instance represents

4. **`end_recurrence_date`** (DateField): When to stop generating new occurrences

5. **`status`** (CharField): Updated to include:
   - `pending`: Not yet started
   - `uncompleted`: In progress or scheduled
   - `completed`: Finished successfully
   - `canceled`: Canceled/won't happen

## Usage Examples

### Creating a Recurring Job

```python
from rental_scheduler.models import Job, Calendar
from datetime import datetime, timedelta

# Create parent job
job = Job.objects.create(
    calendar=my_calendar,
    business_name="ABC Company",
    start_dt=datetime(2025, 1, 1, 9, 0),
    end_dt=datetime(2025, 1, 1, 17, 0),
    # ... other fields
)

# Set up monthly recurrence (every 2 months, 12 total occurrences)
job.create_recurrence_rule(
    recurrence_type='monthly',
    interval=2,
    count=12
)

# Generate the recurring instances
instances = job.generate_recurring_instances()
# This creates 12 child jobs, one every 2 months
```

### Editing a Recurring Event

#### Edit Single Instance Only
```python
# User clicks "Edit this event"
instance = Job.objects.get(id=instance_id)

# Update this instance only
instance.business_name = "New Business Name"
instance.save()
# Parent and other instances remain unchanged
```

#### Edit This and Future Events
```python
# User clicks "Edit this and following events"
instance = Job.objects.get(id=instance_id)
parent = instance.recurrence_parent

# Update this instance
instance.business_name = "New Business Name"
instance.save()

# Update all future instances (excluding completed/canceled)
parent.update_recurring_instances(
    update_type='future',
    after_date=instance.recurrence_original_start,
    fields_to_update={'business_name': 'New Business Name'}
)
```

#### Edit All Events
```python
# User clicks "Edit all events in series"
parent = Job.objects.get(id=parent_id)

# Update parent
parent.business_name = "New Business Name"
parent.save()

# Update all instances
parent.update_recurring_instances(
    update_type='all',
    fields_to_update={'business_name': 'New Business Name'}
)
```

#### Edit Recurrence Rule (Finite ↔ Forever)

You can edit a recurring parent to change its recurrence rule, including converting between finite and forever series.

**Converting Finite to Forever:**
```python
# A job with count=50 can be changed to forever
parent = Job.objects.get(id=parent_id, recurrence_parent__isnull=True)

# Update the recurrence rule
rule = parent.recurrence_rule or {}
rule['end'] = 'never'
rule['count'] = None
rule['until_date'] = None
parent.recurrence_rule = rule
parent.save(update_fields=['recurrence_rule'])

# Existing materialized instances remain intact
# Virtual occurrences will now generate indefinitely
```

**Converting Forever to Finite:**
```python
# A forever series can be converted to have a count
parent = Job.objects.get(id=parent_id, recurrence_parent__isnull=True)

rule = parent.recurrence_rule or {}
rule['count'] = 24
rule['until_date'] = None
if 'end' in rule:
    del rule['end']
parent.recurrence_rule = rule
parent.save(update_fields=['recurrence_rule'])
```

**Important Notes:**
- Only recurring *parents* can have their recurrence rule edited (not instances)
- Existing materialized instances are preserved—no data loss occurs
- Virtual occurrences adjust automatically based on the new rule
- The UI (Job Form) supports this via the "Ends" dropdown

### Marking an Instance Complete

```python
# Complete just this occurrence
instance = Job.objects.get(id=instance_id)
instance.status = 'completed'
instance.save()
# Parent and other instances remain uncompleted
```

### Canceling Future Recurrences

```python
# Cancel all occurrences from a certain date forward
parent = Job.objects.get(id=parent_id)
from_date = datetime(2025, 6, 1).date()

instances_canceled, parent_updated = parent.cancel_future_recurrences(from_date)
# All instances on or after June 1, 2025 are now status='canceled'
# Parent's end_recurrence_date is set to June 1, 2025
```

### Deleting a Recurring Event

#### Delete Single Instance
```python
instance = Job.objects.get(id=instance_id)
instance.delete()
# Only this instance is deleted; parent and others remain
```

#### Delete All Future Instances
```python
parent = Job.objects.get(id=parent_id)
parent.delete_recurring_instances(after_date=datetime(2025, 6, 1))
# Deletes all instances on or after June 1, 2025
```

#### Delete Entire Series
```python
parent = Job.objects.get(id=parent_id)
parent.delete()
# CASCADE deletes parent and ALL child instances
```

## API Endpoints (JSON)

These endpoints are implemented in `rental_scheduler/views_recurring.py` and are documented in more detail in:

- `docs/features/recurring-events/api.md`

### Create job with recurrence

```
POST /api/jobs/create/
{
  "business_name": "ABC Company",
  "start": "2025-01-01T09:00:00",
  "end": "2025-01-01T17:00:00",
  "calendar_id": 1,
  "recurrence": {
    "enabled": true,
    "type": "monthly",
    "interval": 2,
    "count": 12
  }
}
```

### Create a “forever” series (virtual occurrences)

For never-ending series, send `end: "never"` (or explicitly mark it as forever and omit `count`/`until_date`).

```
POST /api/jobs/create/
{
  "business_name": "Weekly Check-in",
  "start": "2025-01-01T09:00:00",
  "end": "2025-01-01T10:00:00",
  "calendar_id": 1,
  "recurrence": {
    "enabled": true,
    "type": "weekly",
    "interval": 1,
    "end": "never"
  }
}
```

### Update job with scope

```
POST /api/jobs/<id>/update/
{
  "business_name": "New Name",
  "update_scope": "this_and_future"  // Options: "this_only", "this_and_future", "all"
}
```

### Cancel future recurrences

```
POST /api/jobs/<parent_id>/cancel-future/
{
  "from_date": "2025-06-01"
}
```

### Delete recurring with scope

Either:

```
DELETE /api/jobs/<id>/delete-recurring/?scope=this_only|this_and_future|all
```

Or:

```
POST /api/jobs/<id>/delete-recurring/
{
  "delete_scope": "this_only"  // or: "this_and_future", "all"
}
```

### Materialize a virtual occurrence (forever series)

When the calendar emits “virtual” occurrences, the UI materializes them into real rows via:

```
POST /api/recurrence/materialize/
{
  "parent_id": 123,
  "original_start": "2026-02-20T10:00:00"
}
```

## Calendar Query

### Fetching Events for Calendar Display

```python
from django.utils import timezone
from rental_scheduler.models import Job

# Get all jobs (parents and instances) for a date range
start_date = timezone.datetime(2025, 1, 1)
end_date = timezone.datetime(2025, 12, 31)

jobs = Job.objects.filter(
    start_dt__lte=end_date,
    end_dt__gte=start_date,
    is_deleted=False
).exclude(
    status='canceled'
).select_related('calendar', 'recurrence_parent')

# Calendar will display parent jobs and materialized instances.
# For “forever” series, the calendar feed also emits virtual occurrences in the requested window.
```

## Frontend Integration

### Displaying Recurrence Information

```javascript
// In job detail view
if (job.recurrence_parent_id) {
    // This is a recurring instance
    showRecurringBadge("Part of series");
} else if (job.recurrence_rule) {
    // This is a parent of recurring events
    const rule = job.recurrence_rule;
    showRecurringBadge(`Repeats ${rule.type} every ${rule.interval} ${rule.type}`);
}
```

### Edit Dialog Options

```javascript
if (job.is_recurring_instance) {
    // Show options:
    // - Edit this event only
    // - Edit this and future events
    // - Edit all events in series
} else if (job.is_recurring_parent) {
    // Show options:
    // - Edit this series (all events)
    // - Cancel future occurrences
}
```

### Virtual occurrences (forever series)

For "forever" series (those with `recurrence_rule.end === 'never'`), the calendar feed emits **virtual** events (not backed by a real `Job` row yet). These are generated on-the-fly for any calendar date window, including windows far into the future (4+ years ahead).

Virtual event types:

- `extendedProps.type === 'virtual_job'`
- `extendedProps.type === 'virtual_call_reminder'`

Virtual events include:

- `extendedProps.recurrence_parent_id`
- `extendedProps.recurrence_original_start` (ISO datetime string)
- `extendedProps.is_virtual === true`

The frontend materializes them via `POST /api/recurrence/materialize/` and then opens the resulting real job.

**Performance Note:** The virtual occurrence generator uses a fast-forward algorithm to efficiently handle distant future windows without iterating through years of dates. It also has iteration guardrails (max 2000 iterations per parent) to prevent runaway loops.

### Jobs list / Search behavior

When using the Jobs List page or the Calendar Search Panel with future-looking date filters (`future`, `two_years`, or `custom` with a future range):

- **Forever recurring parents** are included in the results, even if their original `start_dt` is in the past
- These parents are displayed with an **∞ badge** (e.g., "∞ Weekly") to indicate they're forever series
- Users can click on the parent row to view/edit the series template

This ensures forever series remain discoverable when searching for future events.

### Expandable preview of upcoming occurrences

Forever series rows in the Jobs list and Calendar Search Panel include a **"Show upcoming"** button next to the ∞ badge that reveals the next 5 upcoming virtual occurrences:

- Click the **"Show upcoming"** button to expand and show virtual occurrence rows (the button changes to "Hide upcoming" when expanded)
- Virtual rows are styled with a subtle indigo background and a "↻" icon to indicate they are not yet real jobs
- **Click any virtual row** to materialize it into a real Job and open it for editing
- Use the **"Show 5 more"** button to load additional occurrences (repeatable up to a maximum of 200 occurrences)
- Click the **"Hide upcoming"** button again to collapse the virtual rows

**Technical Details:**
- Virtual occurrences are generated on-the-fly via `GET /api/recurrence/preview/?parent_id=X&count=N` (max: 200)
- Clicking a virtual row calls `POST /api/recurrence/materialize/` to create the real Job before opening it
- The 200-occurrence cap prevents abuse while still allowing users to explore far into the future incrementally

## Best Practices

1. **Always check `is_recurring_instance` before editing** to show appropriate options
2. **Preserve completed/canceled instances** when updating series
3. **Use transactions** when updating multiple instances
4. **Index queries** on `recurrence_parent` and `recurrence_original_start`
5. **Limit generated instances** to avoid performance issues (default 52)
6. **Show recurrence indicators** in calendar UI (e.g., circular arrow icon)

## Migration Path

1. Run migration: `python manage.py migrate`
2. Update existing `repeat_type` jobs to use new system:
   ```python
   from rental_scheduler.models import Job
   
   # For existing jobs with repeat_type set
   for job in Job.objects.filter(repeat_type__in=['monthly', 'yearly']).exclude(repeat_type='none'):
       interval = job.repeat_n_months or 1 if job.repeat_type == 'monthly' else 1
       job.create_recurrence_rule(
           recurrence_type=job.repeat_type,
           interval=interval,
           count=12  # Or determine based on your needs
       )
       job.generate_recurring_instances()
   ```

## Troubleshooting

### Issue: Too many instances generated
**Solution**: Adjust `count` parameter or set `until_date`

### Issue: Completed instances being updated
**Solution**: Check that update queries exclude status='completed'

### Issue: Deleted parent doesn't delete instances
**Solution**: Verify CASCADE is set on `recurrence_parent` ForeignKey

### Issue: Calendar shows duplicate events
**Solution**: Ensure queries don't fetch both parent AND instances for the same date range







