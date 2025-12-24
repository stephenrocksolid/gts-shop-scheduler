"""
Tests for calendar virtual occurrences (forever recurring series).

These tests verify that navigating to far-future calendar windows still renders
virtual occurrences for forever recurring series.
"""
import json
from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from rental_scheduler.models import Job


@pytest.mark.django_db
class TestCalendarVirtualOccurrences:
    """Test virtual occurrence generation in the calendar feed."""

    def test_forever_series_shows_virtual_occurrences_4_years_ahead(self, api_client, calendar):
        """
        A forever recurring series should emit virtual_job events when
        the calendar navigates to a window ~4 years in the future.
        """
        tz = timezone.get_current_timezone()
        # Create parent job starting today
        now = timezone.now()
        start = timezone.make_aware(
            datetime(now.year, now.month, now.day, 10, 0, 0), tz
        )
        end = start + timedelta(hours=1)

        parent = Job.objects.create(
            calendar=calendar,
            business_name="Forever Weekly Job",
            contact_name="Test Contact",
            start_dt=start,
            end_dt=end,
            all_day=False,
            status="uncompleted",
            recurrence_rule={
                "type": "weekly",
                "interval": 1,
                "end": "never",
            },
        )

        # Request a window 4 years ahead (one month window)
        window_start = (start + timedelta(days=4 * 365)).date()
        window_end = window_start + timedelta(days=30)

        url = reverse("rental_scheduler:job_calendar_data")
        response = api_client.get(url, {
            "start": window_start.isoformat(),
            "end": window_end.isoformat(),
            "calendar": calendar.id,
        })

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        events = data["events"]
        # Filter for virtual_job events from this parent
        virtual_jobs = [
            e for e in events
            if e.get("extendedProps", {}).get("type") == "virtual_job"
            and e.get("extendedProps", {}).get("recurrence_parent_id") == parent.id
        ]

        # With weekly recurrence over a 30-day window, we expect ~4-5 virtual occurrences
        assert len(virtual_jobs) >= 4, (
            f"Expected at least 4 virtual_job events for forever weekly series in a 30-day window "
            f"4 years ahead, got {len(virtual_jobs)}"
        )

        # Verify each virtual event has required properties
        for vj in virtual_jobs:
            props = vj["extendedProps"]
            assert props["is_virtual"] is True
            assert props["is_recurring_instance"] is True
            assert props["recurrence_parent_id"] == parent.id
            assert props["recurrence_original_start"] is not None

    def test_forever_series_monthly_shows_virtual_occurrences_far_future(self, api_client, calendar):
        """
        A forever monthly recurring series should emit virtual_job events
        when navigating far into the future.
        """
        tz = timezone.get_current_timezone()
        now = timezone.now()
        start = timezone.make_aware(
            datetime(now.year, now.month, 15, 14, 0, 0), tz
        )
        end = start + timedelta(hours=2)

        parent = Job.objects.create(
            calendar=calendar,
            business_name="Forever Monthly Job",
            start_dt=start,
            end_dt=end,
            all_day=False,
            status="uncompleted",
            recurrence_rule={
                "type": "monthly",
                "interval": 1,
                "end": "never",
            },
        )

        # Request a window 3 years ahead (3 month window)
        window_start = (start + timedelta(days=3 * 365)).date()
        window_end = window_start + timedelta(days=90)

        url = reverse("rental_scheduler:job_calendar_data")
        response = api_client.get(url, {
            "start": window_start.isoformat(),
            "end": window_end.isoformat(),
            "calendar": calendar.id,
        })

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        events = data["events"]
        virtual_jobs = [
            e for e in events
            if e.get("extendedProps", {}).get("type") == "virtual_job"
            and e.get("extendedProps", {}).get("recurrence_parent_id") == parent.id
        ]

        # With monthly recurrence over a 90-day window, expect 3 virtual occurrences
        assert len(virtual_jobs) >= 3, (
            f"Expected at least 3 virtual_job events for forever monthly series, "
            f"got {len(virtual_jobs)}"
        )

    def test_forever_series_daily_shows_virtual_occurrences(self, api_client, calendar):
        """
        A forever daily recurring series should emit virtual_job events
        even for a window years ahead.
        """
        tz = timezone.get_current_timezone()
        now = timezone.now()
        start = timezone.make_aware(
            datetime(now.year, now.month, now.day, 9, 0, 0), tz
        )
        end = start + timedelta(hours=1)

        parent = Job.objects.create(
            calendar=calendar,
            business_name="Forever Daily Job",
            start_dt=start,
            end_dt=end,
            all_day=False,
            status="uncompleted",
            recurrence_rule={
                "type": "daily",
                "interval": 1,
                "end": "never",
            },
        )

        # Request a window 2 years ahead (7-day window to keep response reasonable)
        window_start = (start + timedelta(days=2 * 365)).date()
        window_end = window_start + timedelta(days=7)

        url = reverse("rental_scheduler:job_calendar_data")
        response = api_client.get(url, {
            "start": window_start.isoformat(),
            "end": window_end.isoformat(),
            "calendar": calendar.id,
        })

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        events = data["events"]
        virtual_jobs = [
            e for e in events
            if e.get("extendedProps", {}).get("type") == "virtual_job"
            and e.get("extendedProps", {}).get("recurrence_parent_id") == parent.id
        ]

        # With daily recurrence over a 7-day window, expect 7-8 virtual occurrences
        assert len(virtual_jobs) >= 7, (
            f"Expected at least 7 virtual_job events for forever daily series in a 7-day window, "
            f"got {len(virtual_jobs)}"
        )

    def test_forever_series_with_materialized_instance_excludes_from_virtuals(self, api_client, calendar):
        """
        If a virtual occurrence has been materialized into a real Job row,
        the calendar should NOT emit a duplicate virtual_job for that datetime.
        """
        tz = timezone.get_current_timezone()
        now = timezone.now()
        start = timezone.make_aware(
            datetime(now.year, now.month, now.day, 10, 0, 0), tz
        )
        end = start + timedelta(hours=1)

        parent = Job.objects.create(
            calendar=calendar,
            business_name="Forever Weekly With Instance",
            start_dt=start,
            end_dt=end,
            all_day=False,
            status="uncompleted",
            recurrence_rule={
                "type": "weekly",
                "interval": 1,
                "end": "never",
            },
        )

        # Materialize an instance for next week
        next_week_start = start + timedelta(weeks=1)
        instance = Job.objects.create(
            calendar=calendar,
            business_name="Forever Weekly With Instance",
            start_dt=next_week_start,
            end_dt=next_week_start + timedelta(hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_parent=parent,
            recurrence_original_start=next_week_start,
        )

        # Request a window covering the next 3 weeks (should include parent + 2-3 virtual)
        window_start = start.date()
        window_end = (start + timedelta(weeks=3)).date()

        url = reverse("rental_scheduler:job_calendar_data")
        response = api_client.get(url, {
            "start": window_start.isoformat(),
            "end": window_end.isoformat(),
            "calendar": calendar.id,
        })

        assert response.status_code == 200
        data = response.json()

        events = data["events"]
        # Find the materialized instance (real job event)
        real_instance_events = [
            e for e in events
            if e.get("extendedProps", {}).get("type") == "job"
            and e.get("extendedProps", {}).get("job_id") == instance.id
        ]
        assert len(real_instance_events) >= 1, "Materialized instance should appear as a real job event"

        # Find virtual occurrences from parent
        virtual_jobs = [
            e for e in events
            if e.get("extendedProps", {}).get("type") == "virtual_job"
            and e.get("extendedProps", {}).get("recurrence_parent_id") == parent.id
        ]

        # Check that none of the virtual_jobs have the same recurrence_original_start as the instance
        instance_original_start_iso = next_week_start.isoformat()
        for vj in virtual_jobs:
            vj_original = vj.get("extendedProps", {}).get("recurrence_original_start", "")
            # Normalize for comparison (strip timezone info if present)
            assert not vj_original.startswith(instance_original_start_iso[:19]), (
                f"Virtual occurrence should not duplicate materialized instance at {instance_original_start_iso}"
            )

