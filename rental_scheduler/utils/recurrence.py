"""
Recurring event utilities for the rental scheduler.
Provides functionality similar to Google Calendar's recurring events.
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class RecurrenceGenerator:
    """
    Generates recurring event instances based on recurrence rules.
    """
    
    def __init__(self, parent_job):
        """
        Initialize with a parent job that has recurrence_rule defined.
        
        Args:
            parent_job: Job instance with recurrence_rule set
        """
        self.parent_job = parent_job
        self.rule = parent_job.recurrence_rule or {}
        
    def generate_instances(self, max_count=None, end_date=None):
        """
        Generate recurring job instances based on the recurrence rule.
        
        Args:
            max_count: Maximum number of instances to generate (default from rule or 52)
            end_date: Don't generate instances beyond this date
            
        Returns:
            List of Job instances (not yet saved to database)
        """
        if not self.rule:
            return []
            
        recurrence_type = self.rule.get('type', 'none')
        if recurrence_type == 'none':
            return []
            
        # Determine interval and count
        interval = self.rule.get('interval', 1)
        count = max_count or self.rule.get('count', 50)  # Default 50 occurrences
        until_date = self.rule.get('until_date')
        
        # Parse until_date if it's a string
        if until_date and isinstance(until_date, str):
            until_date = datetime.fromisoformat(until_date.replace('Z', '+00:00'))
            if timezone.is_naive(until_date):
                until_date = timezone.make_aware(until_date)
        
        # Use the more restrictive of until_date and end_date
        if end_date:
            if timezone.is_naive(end_date):
                end_date = timezone.make_aware(end_date)
            if until_date:
                until_date = min(until_date, end_date)
            else:
                until_date = end_date
                
        # Check end_recurrence_date from parent
        if self.parent_job.end_recurrence_date:
            end_recur_dt = timezone.make_aware(
                datetime.combine(self.parent_job.end_recurrence_date, datetime.min.time())
            )
            if until_date:
                until_date = min(until_date, end_recur_dt)
            else:
                until_date = end_recur_dt
        
        instances = []
        current_start = self.parent_job.start_dt
        current_end = self.parent_job.end_dt
        
        # Calculate duration for each instance
        duration = current_end - current_start
        
        for i in range(1, count + 1):  # Start from 1 (parent is 0)
            # Calculate next occurrence
            if recurrence_type == 'monthly':
                # Preserve the same weekday occurrence (e.g., 3rd Friday)
                # Get the weekday and which occurrence it is
                original_weekday = current_start.weekday()  # 0=Monday, 6=Sunday
                original_date = current_start.date()
                
                # Calculate which occurrence of this weekday in the month
                first_of_month = original_date.replace(day=1)
                days_into_month = (original_date - first_of_month).days
                occurrence = (days_into_month // 7) + 1
                
                # Calculate target month
                target_month_date = current_start + relativedelta(months=interval)
                target_year = target_month_date.year
                target_month = target_month_date.month
                
                # Get timezone
                tz = timezone.get_current_timezone() if timezone.is_aware(current_start) else None
                
                # Find the Nth occurrence of the same weekday in the target month
                next_start = get_nth_weekday_of_month(
                    target_year, 
                    target_month, 
                    original_weekday, 
                    occurrence,
                    current_start.time(),
                    tz
                )
                
                # If we couldn't find it (shouldn't happen with our fallback logic), use simple addition
                if next_start is None:
                    next_start = current_start + relativedelta(months=interval)
                    
            elif recurrence_type == 'yearly':
                # Preserve the same ISO week and weekday
                # Get ISO calendar values (year, week, weekday)
                iso_year, iso_week, iso_weekday = current_start.isocalendar()
                
                # Calculate target year
                target_year = current_start.year + interval
                
                # Get timezone
                tz = timezone.get_current_timezone() if timezone.is_aware(current_start) else None
                
                # Find the same weekday in the same ISO week of the target year
                # Note: iso_weekday is 1-7 (Mon-Sun), but we need 0-6 for get_date_from_iso_week
                next_start = get_date_from_iso_week(
                    target_year,
                    iso_week,
                    iso_weekday - 1,  # Convert from 1-7 to 0-6
                    current_start.time(),
                    tz
                )
                
            elif recurrence_type == 'weekly':
                next_start = current_start + timedelta(weeks=interval)
            elif recurrence_type == 'daily':
                next_start = current_start + timedelta(days=interval)
            else:
                logger.warning(f"Unknown recurrence type: {recurrence_type}")
                break
                
            # Check if we've exceeded until_date
            if until_date and next_start > until_date:
                break
                
            next_end = next_start + duration
            
            # Create instance (don't save yet)
            instance = self._create_instance(next_start, next_end, i)
            instances.append(instance)
            
            # Update for next iteration
            current_start = next_start
            current_end = next_end
            
        return instances
        
    def _create_instance(self, start_dt, end_dt, occurrence_number):
        """
        Create a recurring instance from the parent job.
        
        Args:
            start_dt: Start datetime for this instance
            end_dt: End datetime for this instance
            occurrence_number: Which occurrence this is (1-based)
            
        Returns:
            Job instance (not saved)
        """
        from rental_scheduler.models import Job
        
        # Copy all fields from parent except primary key and recurrence fields
        instance = Job(
            # Link to parent
            recurrence_parent=self.parent_job,
            recurrence_original_start=start_dt,
            
            # Copy basic fields
            calendar=self.parent_job.calendar,
            status='uncompleted',  # New instances start as uncompleted
            business_name=self.parent_job.business_name,
            contact_name=self.parent_job.contact_name,
            phone=self.parent_job.phone,
            address_line1=self.parent_job.address_line1,
            address_line2=self.parent_job.address_line2,
            city=self.parent_job.city,
            state=self.parent_job.state,
            postal_code=self.parent_job.postal_code,
            
            # Timing
            start_dt=start_dt,
            end_dt=end_dt,
            all_day=self.parent_job.all_day,
            
            # Don't copy repeat fields (instances don't repeat themselves)
            repeat_type='none',
            repeat_n_months=None,
            
            # Copy call reminder settings
            has_call_reminder=self.parent_job.has_call_reminder,
            call_reminder_weeks_prior=self.parent_job.call_reminder_weeks_prior,
            call_reminder_completed=False,  # Each instance starts with reminder not completed
            
            # Copy job details
            notes=self.parent_job.notes,
            repair_notes=self.parent_job.repair_notes,
            trailer_color=self.parent_job.trailer_color,
            trailer_serial=self.parent_job.trailer_serial,
            trailer_details=self.parent_job.trailer_details,
            quote=self.parent_job.quote,
            trailer_color_overwrite=self.parent_job.trailer_color_overwrite,
            quote_text=self.parent_job.quote_text,
            
            # System fields
            is_deleted=False,
            created_by=self.parent_job.created_by,
        )
        
        return instance


def create_recurring_instances(parent_job, count=None, until_date=None):
    """
    Create and save recurring instances for a parent job.
    
    Args:
        parent_job: Parent Job with recurrence_rule set
        count: Maximum number of instances to generate
        until_date: Don't generate beyond this date
        
    Returns:
        List of created Job instances
    """
    generator = RecurrenceGenerator(parent_job)
    instances = generator.generate_instances(max_count=count, end_date=until_date)
    
    if not instances:
        return []
    
    # Bulk create for efficiency
    with transaction.atomic():
        created_instances = []
        for instance in instances:
            instance.save()
            created_instances.append(instance)
            
            # Create CallReminder if needed
            if instance.has_call_reminder and instance.call_reminder_weeks_prior:
                from rental_scheduler.models import CallReminder
                from rental_scheduler.utils.events import get_call_reminder_sunday
                
                try:
                    reminder_date = get_call_reminder_sunday(
                        instance.start_dt, 
                        instance.call_reminder_weeks_prior
                    ).date()
                    
                    CallReminder.objects.create(
                        job=instance,
                        calendar=instance.calendar,
                        reminder_date=reminder_date,
                        notes='',
                        completed=False
                    )
                    logger.debug(f"Created call reminder for recurring instance {instance.id} on {reminder_date}")
                except Exception as e:
                    logger.error(f"Error creating call reminder for instance {instance.id}: {str(e)}")
            
    logger.info(f"Created {len(created_instances)} recurring instances for job {parent_job.id}")
    return created_instances


def delete_recurring_instances(parent_job, after_date=None):
    """
    Delete all recurring instances of a parent job.
    
    Args:
        parent_job: Parent Job instance
        after_date: Only delete instances after this date (optional)
        
    Returns:
        Number of instances deleted
    """
    from rental_scheduler.models import Job
    
    queryset = Job.objects.filter(recurrence_parent=parent_job)
    
    if after_date:
        queryset = queryset.filter(recurrence_original_start__gte=after_date)
        
    count = queryset.count()
    queryset.delete()
    
    logger.info(f"Deleted {count} recurring instances for job {parent_job.id}")
    return count


def update_recurring_instances(parent_job, update_type='all', after_date=None, fields_to_update=None):
    """
    Update recurring instances based on changes to the parent.
    
    Args:
        parent_job: Parent Job instance
        update_type: 'all' or 'future' - which instances to update
        after_date: For 'future' updates, update instances after this date
        fields_to_update: Dict of field names and values to update
        
    Returns:
        Number of instances updated
    """
    from rental_scheduler.models import Job
    
    if not fields_to_update:
        return 0
        
    queryset = Job.objects.filter(recurrence_parent=parent_job)
    
    if update_type == 'future' and after_date:
        queryset = queryset.filter(recurrence_original_start__gte=after_date)
        
    # Don't update completed or canceled instances (preserve user actions)
    queryset = queryset.exclude(status__in=['completed', 'canceled'])
    
    count = queryset.update(**fields_to_update)
    
    logger.info(f"Updated {count} recurring instances for job {parent_job.id}")
    return count


def regenerate_recurring_instances(parent_job):
    """
    Delete all instances and regenerate them based on current recurrence_rule.
    Useful when the recurrence rule itself changes.
    
    Args:
        parent_job: Parent Job instance
        
    Returns:
        List of newly created instances
    """
    # Delete existing instances (except completed/canceled ones)
    from rental_scheduler.models import Job
    
    with transaction.atomic():
        # Keep completed and canceled instances as history
        Job.objects.filter(
            recurrence_parent=parent_job
        ).exclude(
            status__in=['completed', 'canceled']
        ).delete()
        
        # Generate new instances
        new_instances = create_recurring_instances(parent_job)
        
    logger.info(f"Regenerated {len(new_instances)} instances for job {parent_job.id}")
    return new_instances


def cancel_future_recurrences(parent_job, from_date):
    """
    Cancel all future recurrences starting from a given date.
    
    Args:
        parent_job: Parent Job instance
        from_date: Date to start canceling from
        
    Returns:
        Tuple of (instances_canceled, parent_updated)
    """
    from rental_scheduler.models import Job
    
    with transaction.atomic():
        # Update parent's end_recurrence_date
        parent_job.end_recurrence_date = from_date
        parent_job.save(update_fields=['end_recurrence_date'])
        
        # Cancel future instances
        instances = Job.objects.filter(
            recurrence_parent=parent_job,
            recurrence_original_start__gte=from_date
        ).exclude(status='completed')  # Don't change completed instances
        
        count = instances.update(status='canceled')
        
    logger.info(f"Canceled {count} future instances for job {parent_job.id} from {from_date}")
    return count, True


def get_nth_weekday_of_month(year, month, weekday, occurrence, time_obj, tz):
    """
    Find the Nth occurrence of a weekday in a given month.
    
    Args:
        year: Target year
        month: Target month (1-12)
        weekday: Target weekday (0=Monday, 6=Sunday)
        occurrence: Which occurrence (1=first, 2=second, etc.)
        time_obj: Time to apply to the date (datetime.time object)
        tz: Timezone to apply
        
    Returns:
        datetime object with timezone, or None if occurrence doesn't exist
    """
    # Find the first day of the target month
    first_day = datetime(year, month, 1)
    
    # Find the first occurrence of the target weekday
    days_until_weekday = (weekday - first_day.weekday()) % 7
    first_occurrence = first_day + timedelta(days=days_until_weekday)
    
    # Calculate the Nth occurrence
    target_date = first_occurrence + timedelta(weeks=(occurrence - 1))
    
    # Check if the target date is still in the same month
    if target_date.month != month:
        # This occurrence doesn't exist in this month, use the last occurrence
        target_date = target_date - timedelta(weeks=1)
        
        # Verify it's still in the correct month
        if target_date.month != month:
            return None
    
    # Combine date with time and apply timezone
    result = datetime.combine(target_date.date(), time_obj)
    if tz:
        # Use replace() to set the timezone for zoneinfo compatibility
        result = result.replace(tzinfo=tz)
    
    return result


def get_date_from_iso_week(year, week, weekday, time_obj, tz):
    """
    Get a datetime from ISO year, week number, and weekday.
    
    Args:
        year: Target ISO year
        week: ISO week number (1-53)
        weekday: ISO weekday (0=Monday, 6=Sunday)
        time_obj: Time to apply to the date (datetime.time object)
        tz: Timezone to apply
        
    Returns:
        datetime object with timezone
    """
    # Use datetime.fromisocalendar() which properly handles ISO week dates
    # ISO weekday: 1=Monday, 7=Sunday
    iso_weekday = weekday + 1  # Convert from 0-6 to 1-7
    if iso_weekday > 7:
        iso_weekday = 7
    
    try:
        # Create date from ISO year, week, and weekday
        target_date = datetime.fromisocalendar(year, week, iso_weekday)
    except ValueError:
        # Week might not exist in this year (e.g., week 53 doesn't always exist)
        # Fall back to the last week of the year
        try:
            target_date = datetime.fromisocalendar(year, 52, iso_weekday)
        except ValueError:
            # If even week 52 fails, use week 51
            target_date = datetime.fromisocalendar(year, 51, iso_weekday)
    
    # Combine with time and apply timezone
    result = datetime.combine(target_date.date(), time_obj)
    if tz:
        # Use replace() to set the timezone for zoneinfo compatibility
        result = result.replace(tzinfo=tz)
    
    return result







