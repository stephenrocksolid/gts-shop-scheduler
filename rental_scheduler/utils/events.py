"""
Event datetime normalization utilities for handling all-day events.

This module provides utilities to properly handle all-day events with FullCalendar's
exclusive end semantics and timezone-aware datetime storage.
"""

from datetime import datetime, timedelta, timezone as dt_timezone
from django.utils import timezone
from django.utils.dateparse import parse_datetime


def get_call_reminder_sunday(job_start_dt, weeks_prior):
    """
    Calculate the Sunday date for a call reminder event.
    
    The reminder should appear on:
    - weeks_prior=2 ("1 week prior" in UI): Sunday of the previous week
    - weeks_prior=3 ("2 weeks prior" in UI): Sunday 2 weeks before the job
    
    Args:
        job_start_dt: Job start datetime (timezone-aware)
        weeks_prior: Number of weeks (2 or 3)
        
    Returns:
        datetime: Timezone-aware datetime for midnight on the reminder Sunday
    """
    # Convert to local timezone for date calculations
    local_start = timezone.localtime(job_start_dt)
    
    # Get the date of the job
    job_date = local_start.date()
    
    # Find the Sunday of the job's week
    # weekday() returns 0=Monday, 6=Sunday
    days_since_sunday = (job_date.weekday() + 1) % 7
    job_week_sunday = job_date - timedelta(days=days_since_sunday)
    
    # Calculate the reminder Sunday based on weeks_prior
    # weeks_prior=2 ("1 week prior" in UI) = 1 week earlier
    # weeks_prior=3 ("2 weeks prior" in UI) = 2 weeks earlier
    reminder_sunday = job_week_sunday - timedelta(weeks=weeks_prior - 1)
    
    # Create datetime at midnight local time
    naive_dt = datetime(reminder_sunday.year, reminder_sunday.month, reminder_sunday.day, 0, 0, 0)
    reminder_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())
    
    return reminder_dt


def normalize_event_datetimes(start_value, end_value, all_day: bool):
    """
    Normalize event datetimes for consistent storage and display.
    
    For all-day events:
    - Stores as midnight local timezone (converted to UTC in DB)
    - Returns date-only strings (YYYY-MM-DD) for JSON API
    - End date is exclusive (FullCalendar convention)
    
    For timed events:
    - Stores as timezone-aware datetimes (UTC in DB)
    - Returns ISO 8601 strings with timezone for JSON API
    
    Args:
        start_value: Either a date string (YYYY-MM-DD) or ISO datetime string/datetime object
        end_value: Either a date string (YYYY-MM-DD) or ISO datetime string/datetime object (can be None)
        all_day: Boolean indicating if this is an all-day event
        
    Returns:
        Tuple of (start_dt, end_dt, start_json, end_json, all_day_json) where:
        - start_dt/end_dt: timezone-aware datetimes to store in DB (UTC)
        - start_json/end_json: strings to send to FullCalendar
        - all_day_json: bool for API
    """
    
    if all_day:
        # Handle all-day events: normalize to noon local time to avoid timezone shift issues
        # Accept 'YYYY-MM-DD' or ISO datetime; use only date part for all-day
        
        if isinstance(start_value, str):
            # Extract date portion (first 10 chars: YYYY-MM-DD)
            start_date_str = start_value[:10]
            y, m, d = map(int, start_date_str.split('-'))
            # Create naive datetime at noon, then make timezone-aware
            naive_start = datetime(y, m, d, 12, 0, 0)
            start_dt = timezone.make_aware(naive_start, timezone.get_current_timezone())
        else:
            # Already a datetime object; normalize to noon local
            start_local = timezone.localtime(start_value)
            naive_start = datetime(start_local.year, start_local.month, start_local.day, 12, 0, 0)
            start_dt = timezone.make_aware(naive_start, timezone.get_current_timezone())
        
        # Handle end date - use noon on the same or specified end date
        if end_value:
            end_date_str = str(end_value)[:10]
            y2, m2, d2 = map(int, end_date_str.split('-'))
            # Create naive datetime at noon, then make timezone-aware
            naive_end = datetime(y2, m2, d2, 12, 0, 0)
            end_dt = timezone.make_aware(naive_end, timezone.get_current_timezone())
        else:
            # No end specified, default to same day at noon (single-day event)
            end_dt = start_dt
        
        # Convert to UTC for database storage
        start_dt_utc = start_dt.astimezone(dt_timezone.utc)
        end_dt_utc = end_dt.astimezone(dt_timezone.utc)
        
        # API should return date-only strings for all_day events
        # Use the local date for JSON output
        start_json = start_dt.date().isoformat()  # YYYY-MM-DD
        end_json = end_dt.date().isoformat()      # YYYY-MM-DD (exclusive)
        
        return start_dt_utc, end_dt_utc, start_json, end_json, True
    
    # Timed events: keep timezone-aware datetimes and output ISO 8601 with timezone
    
    def to_aware(dt_or_str):
        """Convert string or naive datetime to timezone-aware datetime"""
        if isinstance(dt_or_str, str):
            # Parse ISO datetime string
            parsed = parse_datetime(dt_or_str)
            if parsed is None:
                # Fallback: treat as date -> midnight local
                date_str = dt_or_str[:10]
                y, m, d = map(int, date_str.split('-'))
                naive_dt = datetime(y, m, d, 0, 0, 0)
                return timezone.make_aware(naive_dt, timezone.get_current_timezone())
            if timezone.is_naive(parsed):
                # Make aware in local timezone
                parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
            return parsed
        else:
            # Already a datetime object
            if timezone.is_naive(dt_or_str):
                return timezone.make_aware(dt_or_str, timezone.get_current_timezone())
            return dt_or_str
    
    start_dt = to_aware(start_value)
    end_dt = to_aware(end_value) if end_value else start_dt
    
    # Store as UTC in database
    start_dt_utc = start_dt.astimezone(dt_timezone.utc)
    end_dt_utc = end_dt.astimezone(dt_timezone.utc)
    
    # Return ISO 8601 with timezone for JSON (in local timezone)
    start_dt_local = timezone.localtime(start_dt_utc)
    end_dt_local = timezone.localtime(end_dt_utc)
    start_json = start_dt_local.isoformat()
    end_json = end_dt_local.isoformat()
    
    return start_dt_utc, end_dt_utc, start_json, end_json, False


def event_to_calendar_json(event, title=None, **extra_props):
    """
    Serialize an event (Job) instance for the calendar feed API.
    
    For all-day events, emit date-only strings with +1 day added to end date
    to implement FullCalendar's exclusive end semantics (so the last day displays).
    For timed events, emit ISO datetimes in local timezone.
    
    Args:
        event: Job instance or any object with start_dt, end_dt, all_day attributes
        title: Optional title override (defaults to str(event))
        **extra_props: Additional properties to include in the event dict
        
    Returns:
        Dict suitable for FullCalendar event feed
    """
    if getattr(event, "all_day", False):
        # All-day events: use date-only strings
        start_date = timezone.localtime(event.start_dt).date()
        end_date = timezone.localtime(event.end_dt).date()
        
        # Add +1 day to end for FullCalendar's exclusive end semantics
        # This ensures the last day displays correctly without modifying stored data
        # E.g., Mon-Tue event (stored) becomes Mon to Wed (exclusive) for display
        end_date_exclusive = end_date + timedelta(days=1)
        
        return {
            "id": getattr(event, "id", None),
            "title": title or str(event),
            "allDay": True,
            "start": start_date.isoformat(),
            "end": end_date_exclusive.isoformat(),  # +1 day for exclusive end
            **extra_props
        }
    else:
        # Timed events: use ISO datetime strings WITHOUT timezone for local display
        # This prevents browser timezone conversion - times display exactly as stored
        start_dt = timezone.localtime(event.start_dt)
        end_dt = timezone.localtime(event.end_dt)
        
        # Remove timezone info to prevent client-side conversion
        # Format as YYYY-MM-DDTHH:MM:SS (no timezone offset)
        start_str = start_dt.strftime('%Y-%m-%dT%H:%M:%S')
        end_str = end_dt.strftime('%Y-%m-%dT%H:%M:%S')
        
        return {
            "id": getattr(event, "id", None),
            "title": title or str(event),
            "allDay": False,
            "start": start_str,
            "end": end_str,
            **extra_props
        }

