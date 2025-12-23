"""
Tests for the recurrence preview occurrences endpoint.

These tests verify that the endpoint correctly generates and returns
virtual occurrence rows for forever recurring series.
"""
from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from rental_scheduler.models import Job


@pytest.mark.django_db
class TestRecurrencePreviewOccurrences:
    """Test the recurrence preview occurrences endpoint."""

    def test_preview_returns_html_rows_for_forever_series(self, api_client, calendar):
        """Preview endpoint should return HTML rows with virtual occurrences."""
        tz = timezone.get_current_timezone()
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

        url = reverse("rental_scheduler:recurrence_preview_occurrences")
        response = api_client.get(url, {"parent_id": parent.id, "count": 5})

        assert response.status_code == 200
        content = response.content.decode("utf-8")

        # Should contain virtual occurrence rows with proper data attributes
        assert 'data-virtual="1"' in content
        assert f'data-recurrence-parent-id="{parent.id}"' in content
        assert 'data-recurrence-original-start' in content
        # Should contain the business name
        assert "Forever Weekly Job" in content

    def test_preview_respects_count_parameter(self, api_client, calendar):
        """Preview should return up to the requested count of occurrences."""
        tz = timezone.get_current_timezone()
        now = timezone.now()
        start = timezone.make_aware(
            datetime(now.year, now.month, now.day, 9, 0, 0), tz
        )
        end = start + timedelta(hours=1)

        parent = Job.objects.create(
            calendar=calendar,
            business_name="Daily Job",
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

        url = reverse("rental_scheduler:recurrence_preview_occurrences")
        
        # Request 3 occurrences
        response = api_client.get(url, {"parent_id": parent.id, "count": 3})
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Count virtual occurrence rows (but not the show-more row)
        virtual_count = content.count('data-virtual="1"')
        assert virtual_count == 3

    def test_preview_caps_count_at_max(self, api_client, calendar):
        """Preview should cap count at 20 to prevent abuse."""
        tz = timezone.get_current_timezone()
        now = timezone.now()
        start = timezone.make_aware(
            datetime(now.year, now.month, now.day, 9, 0, 0), tz
        )
        end = start + timedelta(hours=1)

        parent = Job.objects.create(
            calendar=calendar,
            business_name="Daily Job",
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

        url = reverse("rental_scheduler:recurrence_preview_occurrences")
        
        # Request 300 occurrences (should be capped at 200)
        response = api_client.get(url, {"parent_id": parent.id, "count": 300})
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Should return at most 200 occurrences
        virtual_count = content.count('data-virtual="1"')
        assert virtual_count <= 200

    def test_preview_requires_parent_id(self, api_client):
        """Preview should return 400 if parent_id is missing."""
        url = reverse("rental_scheduler:recurrence_preview_occurrences")
        response = api_client.get(url)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "parent_id" in data["error"]

    def test_preview_rejects_non_forever_series(self, api_client, calendar):
        """Preview should return 400 for jobs that are not forever series."""
        tz = timezone.get_current_timezone()
        now = timezone.now()
        start = timezone.make_aware(
            datetime(now.year, now.month, now.day, 10, 0, 0), tz
        )
        end = start + timedelta(hours=1)

        # Create a finite recurring parent (not forever)
        parent = Job.objects.create(
            calendar=calendar,
            business_name="Finite Recurring Job",
            start_dt=start,
            end_dt=end,
            all_day=False,
            status="uncompleted",
            recurrence_rule={
                "type": "weekly",
                "interval": 1,
                "count": 10,  # Finite series
            },
        )

        url = reverse("rental_scheduler:recurrence_preview_occurrences")
        response = api_client.get(url, {"parent_id": parent.id})
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "forever" in data["error"].lower()

    def test_preview_rejects_recurring_instance(self, api_client, calendar):
        """Preview should return 400 for recurring instances (not parents)."""
        tz = timezone.get_current_timezone()
        now = timezone.now()
        start = timezone.make_aware(
            datetime(now.year, now.month, now.day, 10, 0, 0), tz
        )
        end = start + timedelta(hours=1)

        # Create parent
        parent = Job.objects.create(
            calendar=calendar,
            business_name="Parent Job",
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

        # Create an instance (child of parent)
        instance = Job.objects.create(
            calendar=calendar,
            business_name="Instance Job",
            start_dt=start + timedelta(weeks=1),
            end_dt=end + timedelta(weeks=1),
            all_day=False,
            status="uncompleted",
            recurrence_parent=parent,
            recurrence_original_start=start + timedelta(weeks=1),
        )

        url = reverse("rental_scheduler:recurrence_preview_occurrences")
        response = api_client.get(url, {"parent_id": instance.id})
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "instance" in data["error"].lower()

    def test_preview_returns_404_for_nonexistent_job(self, api_client):
        """Preview should return 404 for non-existent job ID."""
        url = reverse("rental_scheduler:recurrence_preview_occurrences")
        response = api_client.get(url, {"parent_id": 999999})
        
        assert response.status_code == 404

    def test_preview_shows_has_more_button_when_more_exist(self, api_client, calendar):
        """Preview should include a 'show more' button when more occurrences exist."""
        tz = timezone.get_current_timezone()
        now = timezone.now()
        start = timezone.make_aware(
            datetime(now.year, now.month, now.day, 9, 0, 0), tz
        )
        end = start + timedelta(hours=1)

        parent = Job.objects.create(
            calendar=calendar,
            business_name="Daily Job",
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

        url = reverse("rental_scheduler:recurrence_preview_occurrences")
        response = api_client.get(url, {"parent_id": parent.id, "count": 3})
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Should contain "show more" button
        assert "show-more-occurrences-btn" in content
        assert "Show 5 more occurrences" in content


@pytest.mark.django_db
class TestJobRowExpandControl:
    """Test that job rows render with expand control for forever series."""

    def test_forever_series_row_has_expand_button(self, api_client, calendar):
        """Forever series job row should include the expand button."""
        tz = timezone.get_current_timezone()
        now = timezone.now()
        start = timezone.make_aware(
            datetime(now.year, now.month, now.day, 10, 0, 0), tz
        )
        end = start + timedelta(hours=1)

        parent = Job.objects.create(
            calendar=calendar,
            business_name="Forever Weekly",
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

        url = reverse("rental_scheduler:job_list")
        response = api_client.get(url, {"date_filter": "all"})
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Should have the expand button with correct data attribute
        assert 'expand-occurrences-btn' in content
        assert f'data-parent-id="{parent.id}"' in content
        # Should have the forever-series-row class
        assert 'forever-series-row' in content
        # Should have the data-forever-parent attribute
        assert 'data-forever-parent="1"' in content

    def test_finite_series_row_has_no_expand_button(self, api_client, calendar):
        """Finite recurring series should NOT have an expand button."""
        tz = timezone.get_current_timezone()
        now = timezone.now()
        start = timezone.make_aware(
            datetime(now.year, now.month, now.day, 10, 0, 0), tz
        )
        end = start + timedelta(hours=1)

        parent = Job.objects.create(
            calendar=calendar,
            business_name="Finite Monthly",
            start_dt=start,
            end_dt=end,
            all_day=False,
            status="uncompleted",
            recurrence_rule={
                "type": "monthly",
                "interval": 1,
                "count": 12,  # Finite
            },
        )

        url = reverse("rental_scheduler:job_list")
        response = api_client.get(url, {"date_filter": "all"})
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Should NOT have forever-series-row class or expand button for this job
        assert 'data-forever-parent="1"' not in content

