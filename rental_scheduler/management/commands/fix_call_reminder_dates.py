"""
Management command to fix CallReminder reminder_date fields that may have been
stored as datetime instead of date.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from rental_scheduler.models import CallReminder


class Command(BaseCommand):
    help = 'Fix CallReminder reminder_date fields to ensure they are dates, not datetimes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Checking CallReminder records...'))
        
        fixed_count = 0
        error_count = 0
        
        # Get all call reminders
        reminders = CallReminder.objects.all()
        total_count = reminders.count()
        
        self.stdout.write(f'Found {total_count} call reminder records')
        
        for reminder in reminders:
            try:
                # Check if reminder_date is already a date object
                from datetime import datetime, date
                
                # Force refresh from database
                reminder.refresh_from_db()
                
                current_value = reminder.reminder_date
                
                # If it's somehow a datetime, convert it to date
                if isinstance(current_value, datetime):
                    self.stdout.write(
                        self.style.WARNING(
                            f'  Reminder ID {reminder.id}: Converting datetime {current_value} to date'
                        )
                    )
                    reminder.reminder_date = current_value.date()
                    reminder.save(update_fields=['reminder_date'])
                    fixed_count += 1
                elif isinstance(current_value, date):
                    # It's already a date, which is correct
                    pass
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  Reminder ID {reminder.id}: Unexpected type {type(current_value)}'
                        )
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Error processing reminder ID {reminder.id}: {str(e)}')
                )
                error_count += 1
        
        # Also check the database schema to ensure the field is correctly defined
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='rental_scheduler_callreminder'
            """)
            result = cursor.fetchone()
            if result:
                self.stdout.write('\nDatabase schema:')
                self.stdout.write(result[0])
        
        self.stdout.write(self.style.SUCCESS(f'\nProcessing complete:'))
        self.stdout.write(f'  Total records: {total_count}')
        self.stdout.write(f'  Fixed records: {fixed_count}')
        self.stdout.write(f'  Errors: {error_count}')
        
        if fixed_count > 0:
            self.stdout.write(self.style.SUCCESS('\n✓ Fixed corrupted date fields'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ No corrupted records found'))











