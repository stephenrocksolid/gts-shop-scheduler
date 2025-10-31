# Recurring Events Implementation Guide

## Overview
This document describes the Google Calendar-like recurring event system implemented in the GTS Scheduler.

## Database Schema

### New Job Model Fields

1. **`recurrence_rule`** (JSONField): Stores the recurrence pattern
   ```json
   {
     "type": "monthly|yearly|weekly|daily",
     "interval": 2,           // Every 2 months/years/weeks/days
     "count": 12,             // Generate 12 occurrences
     "until_date": "2025-12-31"  // Don't generate after this date
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

## API Endpoints

### Create Recurring Job
```
POST /api/jobs/create/
{
  "business_name": "ABC Company",
  "start": "2025-01-01T09:00:00",
  "end": "2025-01-01T17:00:00",
  "calendar": 1,
  "recurrence": {
    "type": "monthly",
    "interval": 2,
    "count": 12
  }
}
```

### Update Recurring Job
```
POST /api/jobs/<id>/update/
{
  "business_name": "New Name",
  "update_scope": "this_and_future"  // Options: "this_only", "this_and_future", "all"
}
```

### Cancel Future Recurrences
```
POST /api/jobs/<parent_id>/cancel-future/
{
  "from_date": "2025-06-01"
}
```

### Delete Recurring Event
```
DELETE /api/jobs/<id>/delete/
?scope=all  // Options: "this_only", "all", "future"
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

# Calendar will display both parent jobs and generated instances
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







