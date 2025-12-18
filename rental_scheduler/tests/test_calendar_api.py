"""
Tests for calendar API endpoints.
Ensures multi-day clamping and lean payload are working correctly.
"""
import pytest
import json
from datetime import datetime, timedelta
from django.test import Client
from django.utils import timezone
from django.urls import reverse
from rental_scheduler.models import Job, Calendar
from rental_scheduler.constants import MAX_MULTI_DAY_EXPANSION_DAYS


@pytest.mark.django_db
class TestCalendarAPIClamp:
    """Test that multi-day expansion is clamped to request window."""
    
    def create_long_span_job_directly(self, calendar, days=200):
        """
        Create a job with a very long span by bypassing validation.
        This simulates bad data that might slip into the DB.
        Uses raw SQL insert to bypass Django model validation.
        """
        from django.db import connection
        now = timezone.now()
        end = now + timedelta(days=days)
        
        # First create a valid job
        job = Job.objects.create(
            calendar=calendar,
            business_name="Long Span Test",
            start_dt=now,
            end_dt=now + timedelta(hours=2),  # Valid short span
            all_day=False,
            status='uncompleted',
        )
        
        # Then update it with raw SQL to bypass validation
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE rental_scheduler_job SET end_dt = %s WHERE id = %s",
                [end, job.id]
            )
        
        # Refresh from DB
        job.refresh_from_db()
        return job
    
    def test_multiday_expansion_clamped_to_window(self, api_client, calendar):
        """Events should only be returned for the requested window."""
        # Create a job spanning many days
        job = self.create_long_span_job_directly(calendar, days=200)
        
        # Request just a 7-day window
        start = timezone.now().date()
        end = start + timedelta(days=7)
        
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'calendar': calendar.id,
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        
        # Count events for this job
        job_events = [e for e in data['events'] if e.get('extendedProps', {}).get('job_id') == job.id]
        
        # Should be clamped to at most 8 events (7 days + 1 for boundary)
        assert len(job_events) <= 8, f"Expected <= 8 events, got {len(job_events)}"
        
        # Cleanup
        job.delete()
    
    def test_max_expansion_cap_applied(self, api_client, calendar):
        """Even with large window, expansion should be capped."""
        # Create a very long span job
        job = self.create_long_span_job_directly(calendar, days=500)
        
        # Request a large window
        start = timezone.now().date()
        end = start + timedelta(days=365)
        
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'calendar': calendar.id,
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Count events for this job
        job_events = [e for e in data['events'] if e.get('extendedProps', {}).get('job_id') == job.id]
        
        # Should be capped to MAX_MULTI_DAY_EXPANSION_DAYS + 1
        max_expected = MAX_MULTI_DAY_EXPANSION_DAYS + 1
        assert len(job_events) <= max_expected, f"Expected <= {max_expected} events, got {len(job_events)}"
        
        # Cleanup
        job.delete()


@pytest.mark.django_db
class TestCalendarAPIPayload:
    """Test that event payload is lean (no notes/repair_notes)."""
    
    def test_payload_does_not_include_notes(self, api_client, calendar):
        """Event extendedProps should not include notes or repair_notes."""
        now = timezone.now()
        job = Job.objects.create(
            calendar=calendar,
            business_name="Test Business",
            notes="These are some long notes that should not be in the payload",
            repair_notes="These are repair notes that should not be in the payload",
            start_dt=now,
            end_dt=now + timedelta(hours=2),
            status='uncompleted',
        )
        
        start = now.date() - timedelta(days=1)
        end = now.date() + timedelta(days=1)
        
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'calendar': calendar.id,
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the job event
        job_events = [e for e in data['events'] if e.get('extendedProps', {}).get('job_id') == job.id]
        assert len(job_events) >= 1
        
        for event in job_events:
            props = event.get('extendedProps', {})
            assert 'notes' not in props, "notes should not be in extendedProps"
            assert 'repair_notes' not in props, "repair_notes should not be in extendedProps"
            assert 'trailer_details' not in props, "trailer_details should not be in extendedProps"
    
    def test_payload_includes_essential_fields(self, api_client, calendar):
        """Event extendedProps should include essential fields."""
        now = timezone.now()
        job = Job.objects.create(
            calendar=calendar,
            business_name="Test Business",
            trailer_color="Red",
            phone="555-1234",
            start_dt=now,
            end_dt=now + timedelta(hours=2),
            status='uncompleted',
        )
        
        start = now.date() - timedelta(days=1)
        end = now.date() + timedelta(days=1)
        
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'calendar': calendar.id,
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the job event
        job_events = [e for e in data['events'] if e.get('extendedProps', {}).get('job_id') == job.id]
        assert len(job_events) >= 1
        
        event = job_events[0]
        props = event.get('extendedProps', {})
        
        # Essential fields should be present
        assert 'job_id' in props
        assert 'status' in props
        assert 'calendar_id' in props
        assert 'phone' in props
        assert 'trailer_color' in props
        assert 'display_name' in props
        # display_name should match the job's display_name property
        assert props['display_name'] == "Test Business"


@pytest.mark.django_db
class TestCalendarAPIResponse:
    """Test general API response behavior."""
    
    def test_returns_json(self, api_client, calendar):
        """API should return valid JSON."""
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': '2025-01-01',
            'end': '2025-01-31',
        })
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        
        # Should parse as JSON
        data = response.json()
        assert 'status' in data
    
    def test_success_response_structure(self, api_client, calendar):
        """Successful response should have expected structure."""
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': '2025-01-01',
            'end': '2025-01-31',
        })
        
        data = response.json()
        assert data['status'] == 'success'
        assert 'events' in data
        assert isinstance(data['events'], list)


@pytest.mark.django_db
class TestCalendarAPIReadOnly:
    """Test that calendar feed is read-only (no DB writes during GET)."""
    
    def test_calendar_api_does_not_write_to_db(self, api_client, calendar):
        """
        Calendar GET endpoint should not perform any DB writes.
        This is a performance optimization - reads should be pure reads.
        """
        from rental_scheduler.models import CallReminder
        from django.db import connection, reset_queries
        from django.conf import settings
        
        # Create a standalone call reminder
        reminder_date = timezone.now().date()
        reminder = CallReminder.objects.create(
            calendar=calendar,
            reminder_date=reminder_date,
            notes="Test reminder",
            completed=False,
        )
        
        # Get the reminder's updated_at timestamp
        original_updated = reminder.updated_at
        
        # Enable query logging
        old_debug = settings.DEBUG
        settings.DEBUG = True
        reset_queries()
        
        try:
            # Make the API call
            url = reverse('rental_scheduler:job_calendar_data')
            response = api_client.get(url, {
                'start': (reminder_date - timedelta(days=1)).isoformat(),
                'end': (reminder_date + timedelta(days=1)).isoformat(),
                'calendar': calendar.id,
            })
            
            assert response.status_code == 200
            
            # Check that no UPDATE/INSERT queries were run
            queries = connection.queries
            write_queries = [
                q for q in queries
                if q['sql'].strip().upper().startswith(('UPDATE', 'INSERT', 'DELETE'))
            ]
            
            assert len(write_queries) == 0, f"Expected no write queries, got: {write_queries}"
            
            # Verify the reminder wasn't modified
            reminder.refresh_from_db()
            assert reminder.updated_at == original_updated, "CallReminder should not be modified by GET"
            
        finally:
            settings.DEBUG = old_debug
            reset_queries()
