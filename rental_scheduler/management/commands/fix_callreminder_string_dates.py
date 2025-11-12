"""
Management command to fix CallReminder records that have string dates instead of proper date objects.
"""

from django.core.management.base import BaseCommand
from rental_scheduler.models import CallReminder
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fix CallReminder records with string dates, converting them to proper date objects'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting to fix CallReminder date fields...'))
        
        fixed_count = 0
        error_count = 0
        total_count = CallReminder.objects.count()
        
        self.stdout.write(f'Found {total_count} CallReminder records to check')
        
        for reminder in CallReminder.objects.all():
            try:
                reminder_date = reminder.reminder_date
                
                # Check if it's a string
                if isinstance(reminder_date, str):
                    self.stdout.write(
                        f'Reminder {reminder.id}: reminder_date is a string: "{reminder_date}"'
                    )
                    
                    # Try to parse the string to a date
                    try:
                        # Try standard format first
                        date_obj = datetime.strptime(reminder_date, '%Y-%m-%d').date()
                    except ValueError:
                        # Try with time component
                        try:
                            date_obj = datetime.strptime(reminder_date, '%Y-%m-%d %H:%M:%S').date()
                        except ValueError:
                            # Last resort: use dateutil parser
                            from dateutil.parser import parse as parse_date
                            date_obj = parse_date(reminder_date).date()
                    
                    # Update the reminder
                    reminder.reminder_date = date_obj
                    reminder.save(update_fields=['reminder_date'])
                    fixed_count += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'  Fixed reminder {reminder.id}: "{reminder_date}" -> {date_obj}')
                    )
                
                # Check if it's a datetime (should be fixed by previous migration, but check anyway)
                elif isinstance(reminder_date, datetime):
                    self.stdout.write(
                        f'Reminder {reminder.id}: reminder_date is a datetime: {reminder_date}'
                    )
                    
                    date_obj = reminder_date.date()
                    reminder.reminder_date = date_obj
                    reminder.save(update_fields=['reminder_date'])
                    fixed_count += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'  Fixed reminder {reminder.id}: {reminder_date} -> {date_obj}')
                    )
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  Error fixing reminder {reminder.id}: {str(e)}')
                )
                logger.error(f'Error fixing reminder {reminder.id}: {str(e)}')
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'Fixed {fixed_count} CallReminder records'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'{error_count} errors encountered'))
        self.stdout.write(self.style.SUCCESS('Done!'))

