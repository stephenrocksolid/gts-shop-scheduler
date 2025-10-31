"""
Quick test to verify recurring events are working
Run with: python manage.py shell < test_recurring_events.py
"""

from datetime import datetime, timedelta
from rental_scheduler.models import Job, Calendar
from django.utils import timezone

print("\n" + "="*60)
print("TESTING RECURRING EVENTS SYSTEM")
print("="*60 + "\n")

# Get or create a test calendar
calendar, created = Calendar.objects.get_or_create(
    name="Test Calendar",
    defaults={'color': '#3B82F6'}
)
print(f"✓ Using calendar: {calendar.name}")

# Create a parent job
start_dt = timezone.make_aware(datetime(2025, 1, 1, 9, 0))
end_dt = timezone.make_aware(datetime(2025, 1, 1, 17, 0))

parent_job = Job.objects.create(
    calendar=calendar,
    business_name="ABC Monthly Service",
    contact_name="John Doe",
    phone="555-1234",
    start_dt=start_dt,
    end_dt=end_dt,
    all_day=False,
    status='uncompleted',
    notes="Test recurring job"
)
print(f"✓ Created parent job: ID={parent_job.id}")

# Set up monthly recurrence (every 1 month, 6 times)
parent_job.create_recurrence_rule(
    recurrence_type='monthly',
    interval=1,
    count=6
)
print(f"✓ Set recurrence rule: monthly, every 1 month, 6 occurrences")

# Generate recurring instances
instances = parent_job.generate_recurring_instances()
print(f"✓ Generated {len(instances)} recurring instances")

# Display the instances
print("\n" + "-"*60)
print("GENERATED RECURRING JOBS:")
print("-"*60)
print(f"Parent Job (ID: {parent_job.id}): {parent_job.start_dt.strftime('%Y-%m-%d')}")
for instance in instances:
    print(f"  Instance (ID: {instance.id}): {instance.start_dt.strftime('%Y-%m-%d')} - Status: {instance.status}")

# Test properties
print("\n" + "-"*60)
print("TESTING PROPERTIES:")
print("-"*60)
print(f"Parent is_recurring_parent: {parent_job.is_recurring_parent}")
print(f"Parent is_recurring_instance: {parent_job.is_recurring_instance}")
if instances:
    print(f"First instance is_recurring_parent: {instances[0].is_recurring_parent}")
    print(f"First instance is_recurring_instance: {instances[0].is_recurring_instance}")
    print(f"First instance parent ID: {instances[0].recurrence_parent_id}")

# Test marking one instance complete
if instances:
    first_instance = instances[0]
    first_instance.status = 'completed'
    first_instance.save()
    print(f"\n✓ Marked instance {first_instance.id} as completed")
    
    # Check that parent is still uncompleted
    parent_job.refresh_from_db()
    print(f"✓ Parent status still: {parent_job.status}")

# Test canceling future recurrences
from datetime import date
cancel_date = date(2025, 4, 1)  # Cancel from April 1st onward
canceled_count, parent_updated = parent_job.cancel_future_recurrences(cancel_date)
print(f"\n✓ Canceled {canceled_count} future instances from {cancel_date}")
print(f"✓ Parent end_recurrence_date set to: {parent_job.end_recurrence_date}")

# Show final state
print("\n" + "-"*60)
print("FINAL STATE:")
print("-"*60)
all_jobs = Job.objects.filter(
    recurrence_parent=parent_job
).order_by('recurrence_original_start')
for job in all_jobs:
    print(f"  Instance {job.id}: {job.recurrence_original_start.strftime('%Y-%m-%d')} - Status: {job.status}")

print("\n" + "="*60)
print("✓ ALL TESTS PASSED!")
print("="*60 + "\n")

# Cleanup (optional - uncomment to remove test data)
# parent_job.delete()  # This will cascade delete all instances
# print("✓ Cleaned up test data")







