"""
Management command to fix invalid call_reminder_weeks_prior values.
The field should only contain 2 or 3, but some records have 1.
"""
from django.core.management.base import BaseCommand
from rental_scheduler.models import Job


class Command(BaseCommand):
    help = 'Fix invalid call_reminder_weeks_prior values (convert 1 to 2)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Checking Job records for invalid call_reminder_weeks_prior...'))
        
        # Find jobs with invalid call_reminder_weeks_prior values
        invalid_jobs = Job.objects.filter(call_reminder_weeks_prior=1)
        count = invalid_jobs.count()
        
        self.stdout.write(f'Found {count} jobs with call_reminder_weeks_prior = 1')
        
        if count > 0:
            # Fix them by setting to 2 (which means "1 week prior")
            updated = invalid_jobs.update(call_reminder_weeks_prior=2)
            self.stdout.write(self.style.SUCCESS(f'Fixed {updated} jobs (changed 1 -> 2)'))
        else:
            self.stdout.write(self.style.SUCCESS('No invalid records found'))
        
        # Also check for any other invalid values
        all_jobs = Job.objects.exclude(call_reminder_weeks_prior__isnull=True).exclude(
            call_reminder_weeks_prior__in=[2, 3]
        )
        other_invalid = all_jobs.count()
        
        if other_invalid > 0:
            self.stdout.write(self.style.WARNING(f'Found {other_invalid} jobs with other invalid values'))
            for job in all_jobs[:10]:  # Show first 10
                self.stdout.write(f'  Job {job.id}: call_reminder_weeks_prior = {job.call_reminder_weeks_prior}')
        
        self.stdout.write(self.style.SUCCESS('\nProcessing complete!'))

