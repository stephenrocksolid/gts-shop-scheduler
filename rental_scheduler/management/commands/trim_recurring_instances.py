"""
Management command to trim existing recurring instance sets that extend too far into the future.

This is useful for cleaning up recurring series that were created with very high occurrence
counts (e.g., 50 years of monthly jobs) before the "forever" recurrence feature was implemented.

Usage:
    python manage.py trim_recurring_instances --dry-run       # Preview what would be deleted
    python manage.py trim_recurring_instances                  # Actually delete instances
    python manage.py trim_recurring_instances --horizon 2      # Custom horizon (years)
    python manage.py trim_recurring_instances --convert-to-forever  # Also convert series to forever mode

"""

from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from rental_scheduler.models import Job


class Command(BaseCommand):
    help = 'Trim recurring job instances that extend beyond a configurable horizon'

    def add_arguments(self, parser):
        parser.add_argument(
            '--horizon',
            type=int,
            default=3,
            help='Number of years in the future to keep instances. Default: 3 years.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be deleted without actually deleting.'
        )
        parser.add_argument(
            '--convert-to-forever',
            action='store_true',
            help='Also convert parent series to "forever" mode (end=never) after trimming.'
        )
        parser.add_argument(
            '--min-instances',
            type=int,
            default=24,
            help='Only process series with at least this many instances. Default: 24.'
        )

    def handle(self, *args, **options):
        horizon_years = options['horizon']
        dry_run = options['dry_run']
        convert_to_forever = options['convert_to_forever']
        min_instances = options['min_instances']

        horizon_date = date.today() + timedelta(days=horizon_years * 365)
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("TRIM RECURRING INSTANCES"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"Horizon: {horizon_years} years ({horizon_date})")
        self.stdout.write(f"Minimum instances to process: {min_instances}")
        self.stdout.write(f"Convert to forever: {convert_to_forever}")
        self.stdout.write(f"Dry run: {dry_run}")
        self.stdout.write("-" * 70 + "\n")

        # Find recurring parents with instances beyond the horizon
        parents_with_future_instances = Job.objects.filter(
            recurrence_rule__isnull=False,
            recurrence_parent__isnull=True,  # Only parents
            is_deleted=False,
        ).exclude(
            status='canceled'
        ).prefetch_related('recurrence_instances')

        total_trimmed = 0
        total_series_affected = 0
        total_converted = 0

        for parent in parents_with_future_instances:
            # Count all instances
            all_instances = parent.recurrence_instances.filter(is_deleted=False)
            total_count = all_instances.count()

            if total_count < min_instances:
                continue

            # Find instances beyond horizon that are uncompleted
            future_instances = all_instances.filter(
                recurrence_original_start__date__gt=horizon_date,
                status='uncompleted'
            )
            future_count = future_instances.count()

            if future_count == 0:
                continue

            total_series_affected += 1
            
            self.stdout.write(f"\nSeries: {parent.business_name or parent.contact_name or f'Job #{parent.id}'}")
            self.stdout.write(f"  Parent ID: {parent.id}")
            self.stdout.write(f"  Total instances: {total_count}")
            self.stdout.write(f"  Instances beyond {horizon_date}: {future_count}")
            
            if dry_run:
                self.stdout.write(self.style.WARNING(f"  [DRY RUN] Would delete {future_count} instances"))
            else:
                # Delete future uncompleted instances
                with transaction.atomic():
                    deleted_count, _ = future_instances.delete()
                    total_trimmed += deleted_count
                    self.stdout.write(self.style.SUCCESS(f"  Deleted {deleted_count} instances"))

                    # Optionally convert to forever mode
                    if convert_to_forever:
                        rule = parent.recurrence_rule or {}
                        if rule.get('end') != 'never':
                            rule['end'] = 'never'
                            rule.pop('count', None)  # Remove count
                            rule.pop('until_date', None)  # Remove until_date
                            parent.recurrence_rule = rule
                            parent.end_recurrence_date = None
                            parent.save(update_fields=['recurrence_rule', 'end_recurrence_date'])
                            total_converted += 1
                            self.stdout.write(self.style.SUCCESS(f"  Converted to forever mode"))

        # Summary
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("SUMMARY")
        self.stdout.write("=" * 70)
        self.stdout.write(f"Series affected: {total_series_affected}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f"Instances that would be deleted: (dry run, no changes made)"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Instances deleted: {total_trimmed}"))
            if convert_to_forever:
                self.stdout.write(self.style.SUCCESS(f"Series converted to forever: {total_converted}"))

        self.stdout.write("=" * 70 + "\n")

        if dry_run and total_series_affected > 0:
            self.stdout.write(self.style.WARNING(
                "\nRun without --dry-run to actually delete the instances."
            ))




