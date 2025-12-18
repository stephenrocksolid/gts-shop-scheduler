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


@pytest.mark.django_db
class TestCalendarAPIQueryCount:
    """Test that calendar feed maintains expected query count (no N+1)."""
    
    # Maximum expected queries for a cache-miss calendar feed request:
    # 1 - Jobs query (with annotations)
    # 2 - Standalone CallReminder query
    # Plus a small margin for session/auth queries
    MAX_EXPECTED_QUERIES = 5
    
    def test_query_count_with_multiple_jobs(self, api_client, calendar):
        """
        Ensure loading multiple jobs doesn't trigger N+1 queries.
        This is a regression test for the recurring property fix.
        """
        from django.db import connection, reset_queries
        from django.conf import settings
        
        now = timezone.now()
        
        # Create 10 jobs - if N+1 exists, this would cause 10+ extra queries
        for i in range(10):
            Job.objects.create(
                calendar=calendar,
                business_name=f"Test Business {i}",
                start_dt=now + timedelta(days=i),
                end_dt=now + timedelta(days=i, hours=2),
                status='uncompleted',
            )
        
        start = now.date() - timedelta(days=1)
        end = now.date() + timedelta(days=15)
        
        # Enable query logging
        old_debug = settings.DEBUG
        settings.DEBUG = True
        reset_queries()
        
        try:
            url = reverse('rental_scheduler:job_calendar_data')
            # Add fresh=1 to bypass cache
            response = api_client.get(url, {
                'start': start.isoformat(),
                'end': end.isoformat(),
                'calendar': calendar.id,
                'fresh': '1',
            })
            
            assert response.status_code == 200
            
            query_count = len(connection.queries)
            assert query_count <= self.MAX_EXPECTED_QUERIES, (
                f"Expected <= {self.MAX_EXPECTED_QUERIES} queries, got {query_count}. "
                f"This may indicate an N+1 query regression."
            )
            
        finally:
            settings.DEBUG = old_debug
            reset_queries()
    
    def test_query_count_with_recurring_jobs(self, api_client, calendar):
        """
        Ensure recurring parent/instance jobs don't trigger extra queries.
        The is_recurring_parent and is_recurring_instance properties should
        use recurrence_parent_id (not load the related object).
        """
        from django.db import connection, reset_queries
        from django.conf import settings
        
        now = timezone.now()
        
        # Create a parent job with recurrence_rule
        parent = Job.objects.create(
            calendar=calendar,
            business_name="Recurring Parent",
            start_dt=now,
            end_dt=now + timedelta(hours=2),
            status='uncompleted',
            recurrence_rule={'type': 'monthly', 'interval': 1},
        )
        
        # Create some instance jobs that reference the parent
        for i in range(5):
            Job.objects.create(
                calendar=calendar,
                business_name=f"Recurring Instance {i}",
                start_dt=now + timedelta(days=30 * (i + 1)),
                end_dt=now + timedelta(days=30 * (i + 1), hours=2),
                status='uncompleted',
                recurrence_parent=parent,
                recurrence_original_start=now + timedelta(days=30 * (i + 1)),
            )
        
        start = now.date() - timedelta(days=1)
        end = now.date() + timedelta(days=180)
        
        # Enable query logging
        old_debug = settings.DEBUG
        settings.DEBUG = True
        reset_queries()
        
        try:
            url = reverse('rental_scheduler:job_calendar_data')
            response = api_client.get(url, {
                'start': start.isoformat(),
                'end': end.isoformat(),
                'calendar': calendar.id,
                'fresh': '1',
            })
            
            assert response.status_code == 200
            
            query_count = len(connection.queries)
            assert query_count <= self.MAX_EXPECTED_QUERIES, (
                f"Expected <= {self.MAX_EXPECTED_QUERIES} queries with recurring jobs, "
                f"got {query_count}. Recurring properties may be triggering N+1."
            )
            
        finally:
            settings.DEBUG = old_debug
            reset_queries()


@pytest.mark.django_db
class TestCalendarAPIRecurringFlags:
    """Test that recurring flags are correctly serialized."""
    
    def test_recurring_parent_flag_serialized(self, api_client, calendar):
        """A job with recurrence_rule and no parent should have is_recurring_parent=True."""
        now = timezone.now()
        parent = Job.objects.create(
            calendar=calendar,
            business_name="Recurring Parent",
            start_dt=now,
            end_dt=now + timedelta(hours=2),
            status='uncompleted',
            recurrence_rule={'type': 'monthly', 'interval': 1},
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
        
        job_events = [e for e in data['events'] if e.get('extendedProps', {}).get('job_id') == parent.id]
        assert len(job_events) >= 1
        
        props = job_events[0]['extendedProps']
        assert props.get('is_recurring_parent') is True
        assert props.get('is_recurring_instance') is False
    
    def test_recurring_instance_flag_serialized(self, api_client, calendar):
        """A job with recurrence_parent should have is_recurring_instance=True."""
        now = timezone.now()
        parent = Job.objects.create(
            calendar=calendar,
            business_name="Recurring Parent",
            start_dt=now - timedelta(days=30),
            end_dt=now - timedelta(days=30) + timedelta(hours=2),
            status='uncompleted',
            recurrence_rule={'type': 'monthly', 'interval': 1},
        )
        
        instance = Job.objects.create(
            calendar=calendar,
            business_name="Recurring Instance",
            start_dt=now,
            end_dt=now + timedelta(hours=2),
            status='uncompleted',
            recurrence_parent=parent,
            recurrence_original_start=now,
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
        
        job_events = [e for e in data['events'] if e.get('extendedProps', {}).get('job_id') == instance.id]
        assert len(job_events) >= 1
        
        props = job_events[0]['extendedProps']
        assert props.get('is_recurring_parent') is False
        assert props.get('is_recurring_instance') is True


@pytest.mark.django_db
class TestCalendarAPICallReminderAnnotations:
    """Test that call reminder annotations work correctly."""
    
    def test_job_call_reminder_notes_annotated(self, api_client, calendar):
        """Job-linked call reminders should have notes annotated correctly."""
        from rental_scheduler.models import CallReminder
        
        # Create a job 3 weeks in the future with weeks_prior=2
        # This ensures the reminder (1 week before job's week Sunday) falls within the request window
        now = timezone.now()
        job_date = now + timedelta(weeks=3)  # 3 weeks in future
        job = Job.objects.create(
            calendar=calendar,
            business_name="Test Business",
            start_dt=job_date,
            end_dt=job_date + timedelta(hours=2),
            status='uncompleted',
            has_call_reminder=True,
            call_reminder_weeks_prior=2,  # Reminder 1 week prior (weeks_prior=2 in DB)
        )
        
        # Create a call reminder linked to this job with notes
        # The reminder_date here is separate from the computed reminder date
        CallReminder.objects.create(
            job=job,
            calendar=calendar,
            reminder_date=now.date() + timedelta(weeks=2),  # ~2 weeks from now
            notes="Please call customer about scheduling",
            completed=False,
        )
        
        # Request window should cover both now and 4 weeks out
        start = now.date() - timedelta(days=7)
        end = now.date() + timedelta(weeks=4)
        
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'calendar': calendar.id,
            'fresh': '1',  # Bypass cache
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the call reminder event (type=call_reminder)
        reminder_events = [
            e for e in data['events'] 
            if e.get('extendedProps', {}).get('type') == 'call_reminder' 
            and e.get('extendedProps', {}).get('job_id') == job.id
        ]
        assert len(reminder_events) >= 1, f"Expected call reminder event for job {job.id}"
        
        props = reminder_events[0]['extendedProps']
        assert props.get('has_notes') is True
        assert 'call customer' in props.get('notes_preview', '').lower()
    
    def test_standalone_call_reminder_displayed(self, api_client, calendar):
        """Standalone call reminders should appear in the feed."""
        from rental_scheduler.models import CallReminder
        
        reminder_date = timezone.now().date()
        reminder = CallReminder.objects.create(
            calendar=calendar,
            reminder_date=reminder_date,
            notes="Standalone reminder note",
            completed=False,
        )
        
        start = reminder_date - timedelta(days=1)
        end = reminder_date + timedelta(days=1)
        
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'calendar': calendar.id,
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the standalone call reminder event
        reminder_events = [
            e for e in data['events'] 
            if e.get('extendedProps', {}).get('type') == 'standalone_call_reminder'
            and e.get('extendedProps', {}).get('reminder_id') == reminder.id
        ]
        assert len(reminder_events) == 1
        
        props = reminder_events[0]['extendedProps']
        assert props.get('has_notes') is True
        assert 'Standalone' in props.get('notes_preview', '')


@pytest.mark.django_db
class TestCalendarAPIPostgres:
    """Tests specific to PostgreSQL performance path."""
    
    def test_postgres_backend_detection(self, api_client, calendar):
        """Verify PostgreSQL backend is detected and used."""
        from django.db import connection
        
        # Only run meaningful assertions on PostgreSQL
        if connection.vendor != 'postgresql':
            pytest.skip("Test only applicable to PostgreSQL backend")
        
        # Create a test job - use noon to avoid timezone edge cases
        today = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        job = Job.objects.create(
            calendar=calendar,
            business_name="Postgres Test Job",
            contact_name="Test Contact",
            start_dt=today,
            end_dt=today + timedelta(hours=2),
            all_day=False,
            status='uncompleted',
        )
        
        start = today.date() - timedelta(days=1)
        end = today.date() + timedelta(days=1)
        
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'calendar': calendar.id,
            'fresh': '1',  # Bypass cache
        })
        
        assert response.status_code == 200
        
        # Check that the Postgres path was used (indicated by X-DB-Backend header in DEBUG mode)
        from django.conf import settings
        if settings.DEBUG:
            assert response.get('X-DB-Backend') == 'postgresql'
        
        data = response.json()
        assert data['status'] == 'success'
        
        # Verify the job appears in results (at least one event)
        job_events = [
            e for e in data['events']
            if e.get('extendedProps', {}).get('job_id') == job.id
        ]
        assert len(job_events) >= 1, "Expected at least 1 event for the job"
        
        job.delete()
    
    def test_postgres_query_count_single_query(self, api_client, calendar):
        """PostgreSQL path should use minimal queries (ideally 1 for main data)."""
        from django.db import connection, reset_queries
        from django.conf import settings
        
        if connection.vendor != 'postgresql':
            pytest.skip("Test only applicable to PostgreSQL backend")
        
        # Create multiple jobs and reminders
        now = timezone.now()
        jobs = []
        for i in range(5):
            job = Job.objects.create(
                calendar=calendar,
                business_name=f"Postgres Query Test {i}",
                start_dt=now + timedelta(days=i),
                end_dt=now + timedelta(days=i, hours=2),
                all_day=False,
                status='uncompleted',
            )
            jobs.append(job)
        
        start = now.date() - timedelta(days=1)
        end = now.date() + timedelta(days=10)
        
        # Reset query log
        reset_queries()
        
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'calendar': calendar.id,
            'fresh': '1',
        })
        
        assert response.status_code == 200
        
        # Count queries - should be very low (1 for main call + a few for virtual occurrences check)
        # The main calendar_feed function is 1 query, virtual occurrences add 1-2 more
        query_count = len(connection.queries)
        
        # Should be significantly fewer queries than the number of jobs
        # With ORM path, it would be at least 1 per job for call reminders
        MAX_EXPECTED_POSTGRES_QUERIES = 10  # Very generous limit
        assert query_count <= MAX_EXPECTED_POSTGRES_QUERIES, (
            f"Expected <= {MAX_EXPECTED_POSTGRES_QUERIES} queries on Postgres, got {query_count}"
        )
        
        # Cleanup
        for job in jobs:
            job.delete()
    
    def test_postgres_multiday_expansion(self, api_client, calendar):
        """PostgreSQL path should correctly expand multi-day jobs."""
        from django.db import connection
        
        if connection.vendor != 'postgresql':
            pytest.skip("Test only applicable to PostgreSQL backend")
        
        # Use a future date at noon to avoid timezone edge cases
        base_date = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Create a 5-day job (starts tomorrow noon, ends 4 days later at noon)
        job = Job.objects.create(
            calendar=calendar,
            business_name="Multi-Day Postgres Test",
            start_dt=base_date,
            end_dt=base_date + timedelta(days=4),
            all_day=False,
            status='uncompleted',
        )
        
        # Request window encompasses the entire job with margin
        start = base_date.date() - timedelta(days=1)
        end = base_date.date() + timedelta(days=10)
        
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'calendar': calendar.id,
            'fresh': '1',
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Find all events for this job
        job_events = [
            e for e in data['events']
            if e.get('extendedProps', {}).get('job_id') == job.id
        ]
        
        # Should have at least 4 events (one per day) - could be 5 depending on timing
        assert len(job_events) >= 4, f"Expected >= 4 day events, got {len(job_events)}"
        assert len(job_events) <= 6, f"Expected <= 6 day events, got {len(job_events)}"
        
        # All should be marked as multi-day
        for event in job_events:
            assert event['extendedProps']['is_multi_day'] is True
        
        job.delete()
    
    def test_postgres_call_reminder_included(self, api_client, calendar):
        """PostgreSQL path should include job-linked call reminders."""
        from django.db import connection
        
        if connection.vendor != 'postgresql':
            pytest.skip("Test only applicable to PostgreSQL backend")
        
        # Create a job with call reminder in 2 weeks
        now = timezone.now()
        job_date = now + timedelta(weeks=3)
        job = Job.objects.create(
            calendar=calendar,
            business_name="Call Reminder Postgres Test",
            start_dt=job_date,
            end_dt=job_date + timedelta(hours=2),
            all_day=False,
            status='uncompleted',
            has_call_reminder=True,
            call_reminder_weeks_prior=2,
            call_reminder_completed=False,
        )
        
        # Request window should include the reminder date (2 weeks before job)
        start = now.date()
        end = job_date.date() + timedelta(days=1)
        
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'calendar': calendar.id,
            'fresh': '1',
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Find call reminder events for this job
        reminder_events = [
            e for e in data['events']
            if e.get('extendedProps', {}).get('type') == 'call_reminder'
            and e.get('extendedProps', {}).get('job_id') == job.id
        ]
        
        assert len(reminder_events) == 1, "Expected 1 call reminder event"
        assert '📞' in reminder_events[0]['title']
        
        job.delete()
    
    def test_postgres_standalone_reminder_included(self, api_client, calendar):
        """PostgreSQL path should include standalone call reminders."""
        from django.db import connection
        from rental_scheduler.models import CallReminder
        
        if connection.vendor != 'postgresql':
            pytest.skip("Test only applicable to PostgreSQL backend")
        
        reminder_date = timezone.now().date() + timedelta(days=2)
        reminder = CallReminder.objects.create(
            calendar=calendar,
            reminder_date=reminder_date,
            notes="Postgres standalone test",
            completed=False,
        )
        
        start = reminder_date - timedelta(days=1)
        end = reminder_date + timedelta(days=1)
        
        url = reverse('rental_scheduler:job_calendar_data')
        response = api_client.get(url, {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'calendar': calendar.id,
            'fresh': '1',
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Find standalone reminder
        standalone_events = [
            e for e in data['events']
            if e.get('extendedProps', {}).get('type') == 'standalone_call_reminder'
            and e.get('extendedProps', {}).get('reminder_id') == reminder.id
        ]
        
        assert len(standalone_events) == 1
        assert 'Postgres standalone' in standalone_events[0]['title']
        
        reminder.delete()
    
    def test_postgres_search_filter(self, api_client, calendar):
        """PostgreSQL path should respect search filters."""
        from django.db import connection
        
        if connection.vendor != 'postgresql':
            pytest.skip("Test only applicable to PostgreSQL backend")
        
        now = timezone.now()
        job1 = Job.objects.create(
            calendar=calendar,
            business_name="Alpha Corp",
            start_dt=now,
            end_dt=now + timedelta(hours=2),
            status='uncompleted',
        )
        job2 = Job.objects.create(
            calendar=calendar,
            business_name="Beta Inc",
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
            'search': 'Alpha',
            'fresh': '1',
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return Alpha Corp
        job_events = [
            e for e in data['events']
            if e.get('extendedProps', {}).get('type') == 'job'
        ]
        
        job_ids = {e.get('extendedProps', {}).get('job_id') for e in job_events}
        assert job1.id in job_ids
        assert job2.id not in job_ids
        
        job1.delete()
        job2.delete()
