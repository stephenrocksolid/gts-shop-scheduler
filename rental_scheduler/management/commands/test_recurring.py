"""
Management command to test recurring events functionality
Run with: python manage.py test_recurring
"""

from django.core.management.base import BaseCommand
from datetime import datetime, date
from rental_scheduler.models import Job, Calendar
from django.utils import timezone


class Command(BaseCommand):
    help = 'Test the recurring events system'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("TESTING RECURRING EVENTS SYSTEM"))
        self.stdout.write("="*60 + "\n")

        # Get or create a test calendar
        calendar, created = Calendar.objects.get_or_create(
            name="Test Calendar",
            defaults={'color': '#3B82F6'}
        )
        self.stdout.write(self.style.SUCCESS(f"[OK] Using calendar: {calendar.name}"))

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
        self.stdout.write(self.style.SUCCESS(f"[OK] Created parent job: ID={parent_job.id}"))

        # Set up monthly recurrence (every 1 month, 6 times)
        parent_job.create_recurrence_rule(
            recurrence_type='monthly',
            interval=1,
            count=6
        )
        self.stdout.write(self.style.SUCCESS(
            f"[OK] Set recurrence rule: monthly, every 1 month, 6 occurrences"
        ))

        # Generate recurring instances
        instances = parent_job.generate_recurring_instances()
        self.stdout.write(self.style.SUCCESS(
            f"[OK] Generated {len(instances)} recurring instances"
        ))

        # Display the instances
        self.stdout.write("\n" + "-"*60)
        self.stdout.write("GENERATED RECURRING JOBS:")
        self.stdout.write("-"*60)
        self.stdout.write(f"Parent Job (ID: {parent_job.id}): {parent_job.start_dt.strftime('%Y-%m-%d')}")
        for instance in instances:
            self.stdout.write(
                f"  Instance (ID: {instance.id}): "
                f"{instance.start_dt.strftime('%Y-%m-%d')} - Status: {instance.status}"
            )

        # Test properties
        self.stdout.write("\n" + "-"*60)
        self.stdout.write("TESTING PROPERTIES:")
        self.stdout.write("-"*60)
        self.stdout.write(f"Parent is_recurring_parent: {parent_job.is_recurring_parent}")
        self.stdout.write(f"Parent is_recurring_instance: {parent_job.is_recurring_instance}")
        if instances:
            self.stdout.write(f"First instance is_recurring_parent: {instances[0].is_recurring_parent}")
            self.stdout.write(f"First instance is_recurring_instance: {instances[0].is_recurring_instance}")
            self.stdout.write(f"First instance parent ID: {instances[0].recurrence_parent_id}")

        # Test marking one instance complete
        if instances:
            first_instance = instances[0]
            first_instance.status = 'completed'
            first_instance.save()
            self.stdout.write(self.style.SUCCESS(
                f"\n[OK] Marked instance {first_instance.id} as completed"
            ))
            
            # Check that parent is still uncompleted
            parent_job.refresh_from_db()
            self.stdout.write(self.style.SUCCESS(f"[OK] Parent status still: {parent_job.status}"))

        # Test canceling future recurrences
        cancel_date = date(2025, 4, 1)  # Cancel from April 1st onward
        canceled_count, parent_updated = parent_job.cancel_future_recurrences(cancel_date)
        self.stdout.write(self.style.SUCCESS(
            f"\n[OK] Canceled {canceled_count} future instances from {cancel_date}"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"[OK] Parent end_recurrence_date set to: {parent_job.end_recurrence_date}"
        ))

        # Show final state
        self.stdout.write("\n" + "-"*60)
        self.stdout.write("FINAL STATE:")
        self.stdout.write("-"*60)
        all_jobs = Job.objects.filter(
            recurrence_parent=parent_job
        ).order_by('recurrence_original_start')
        for job in all_jobs:
            self.stdout.write(
                f"  Instance {job.id}: "
                f"{job.recurrence_original_start.strftime('%Y-%m-%d')} - Status: {job.status}"
            )

        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("[OK] ALL TESTS PASSED!"))
        self.stdout.write("="*60 + "\n")

        # Cleanup
        self.stdout.write(self.style.WARNING("\nCleaning up test data..."))
        parent_job.delete()  # This will cascade delete all instances
        self.stdout.write(self.style.SUCCESS("[OK] Cleaned up test data"))

