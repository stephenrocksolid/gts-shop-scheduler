# Migration to fix CallReminder reminder_date fields
# that may have datetime values instead of date values

from django.db import migrations
from datetime import datetime


def fix_reminder_dates(apps, schema_editor):
    """Convert any datetime values in reminder_date to date values"""
    CallReminder = apps.get_model('rental_scheduler', 'CallReminder')
    
    fixed_count = 0
    for reminder in CallReminder.objects.all():
        # Check if the value needs conversion
        if isinstance(reminder.reminder_date, datetime):
            reminder.reminder_date = reminder.reminder_date.date()
            reminder.save(update_fields=['reminder_date'])
            fixed_count += 1
    
    if fixed_count > 0:
        print(f"Fixed {fixed_count} call reminder date fields")


def reverse_fix(apps, schema_editor):
    # Nothing to reverse - we're just cleaning up data
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('rental_scheduler', '0028_add_call_reminder_completed'),
    ]

    operations = [
        migrations.RunPython(fix_reminder_dates, reverse_fix),
    ]








