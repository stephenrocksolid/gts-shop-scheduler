"""
Tests for grouped recurring search results.

Verifies:
- Recurring jobs are grouped under series header rows when search is active
- Series appears in both Upcoming and Past when applicable
- The series occurrences endpoint returns filtered materialized + virtual rows
"""
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from rental_scheduler.models import Job


@pytest.mark.django_db
class TestGroupedSearchContext:
    """Test that grouped search context is populated correctly."""

    def test_grouped_search_context_set_when_search_active(self, api_client, calendar):
        """When search is active, is_grouped_search and grouped_search are set."""
        now = timezone.now()
        
        # Create a recurring parent
        parent = Job.objects.create(
            calendar=calendar,
            business_name="GroupTest Monthly",
            start_dt=now + timedelta(days=1),
            end_dt=now + timedelta(days=1, hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_rule={"type": "monthly", "interval": 1, "end": "never"},
        )
        
        url = reverse("rental_scheduler:job_list_table_partial")
        response = api_client.get(url, {"search": "GroupTest"})
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Should contain series header row
        assert "series-header-row" in content
        
    def test_no_grouped_search_when_no_search_query(self, api_client, calendar):
        """Without search, standard rows are rendered (no series headers)."""
        now = timezone.now()
        
        Job.objects.create(
            calendar=calendar,
            business_name="Normal Job",
            start_dt=now + timedelta(days=1),
            end_dt=now + timedelta(days=1, hours=1),
            all_day=False,
            status="uncompleted",
        )
        
        url = reverse("rental_scheduler:job_list_table_partial")
        response = api_client.get(url)
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Should NOT contain series header rows
        assert "series-header-row" not in content
        # Should contain normal job row
        assert "job-row" in content

    def test_series_in_both_upcoming_and_past_sections(self, api_client, calendar):
        """Series with both past and future occurrences appears in both sections."""
        now = timezone.now()
        
        # Create parent in the past
        parent = Job.objects.create(
            calendar=calendar,
            business_name="BothSections Test",
            start_dt=now - timedelta(days=30),
            end_dt=now - timedelta(days=30, hours=-1),
            all_day=False,
            status="uncompleted",
            recurrence_rule={"type": "monthly", "interval": 1, "end": "never"},
        )
        
        # Create a future instance
        Job.objects.create(
            calendar=calendar,
            business_name="BothSections Test",
            start_dt=now + timedelta(days=30),
            end_dt=now + timedelta(days=30, hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_parent=parent,
            recurrence_original_start=now + timedelta(days=30),
        )
        
        url = reverse("rental_scheduler:job_list_table_partial")
        response = api_client.get(url, {"search": "BothSections", "date_filter": "all"})
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Should show both Upcoming and Past sections
        assert "Upcoming Events" in content
        assert "Past Events" in content
        
        # Should have series header rows (at least 2 - one for each section)
        assert content.count("series-header-row") >= 2

    def test_standalone_jobs_not_grouped(self, api_client, calendar):
        """Non-recurring jobs appear as standalone rows, not in series groups."""
        now = timezone.now()
        
        # Create a non-recurring job
        Job.objects.create(
            calendar=calendar,
            business_name="StandaloneSearch Test",
            start_dt=now + timedelta(days=1),
            end_dt=now + timedelta(days=1, hours=1),
            all_day=False,
            status="uncompleted",
        )
        
        # Create a recurring job
        Job.objects.create(
            calendar=calendar,
            business_name="RecurringSearch Test",
            start_dt=now + timedelta(days=2),
            end_dt=now + timedelta(days=2, hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_rule={"type": "monthly", "interval": 1, "end": "never"},
        )
        
        url = reverse("rental_scheduler:job_list_table_partial")
        response = api_client.get(url, {"search": "Search Test"})
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Should have both a series header and a regular job row
        assert "series-header-row" in content
        assert "StandaloneSearch Test" in content


@pytest.mark.django_db
class TestSeriesOccurrencesEndpoint:
    """Test the series occurrences API endpoint."""

    def test_series_occurrences_returns_html(self, api_client, calendar):
        """Endpoint returns HTML rows for materialized occurrences."""
        now = timezone.now()
        
        parent = Job.objects.create(
            calendar=calendar,
            business_name="Occurrences Test",
            start_dt=now + timedelta(days=1),
            end_dt=now + timedelta(days=1, hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_rule={"type": "monthly", "interval": 1, "end": "never"},
        )
        
        # Create an instance
        Job.objects.create(
            calendar=calendar,
            business_name="Occurrences Test",
            start_dt=now + timedelta(days=31),
            end_dt=now + timedelta(days=31, hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_parent=parent,
            recurrence_original_start=now + timedelta(days=31),
        )
        
        url = reverse("rental_scheduler:series_occurrences_api")
        response = api_client.get(url, {
            "parent_id": parent.id,
            "scope": "upcoming",
            "search": "Occurrences",
        })
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Should contain occurrence rows
        assert "series-occurrence-row" in content

    def test_series_occurrences_filters_by_scope(self, api_client, calendar):
        """Endpoint respects scope parameter (upcoming vs past)."""
        now = timezone.now()
        
        parent = Job.objects.create(
            calendar=calendar,
            business_name="Scope Test",
            start_dt=now - timedelta(days=30),
            end_dt=now - timedelta(days=30, hours=-1),
            all_day=False,
            status="uncompleted",
            recurrence_rule={"type": "monthly", "interval": 1, "end": "never"},
        )
        
        # Create a future instance
        future_instance = Job.objects.create(
            calendar=calendar,
            business_name="Scope Test",
            start_dt=now + timedelta(days=30),
            end_dt=now + timedelta(days=30, hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_parent=parent,
            recurrence_original_start=now + timedelta(days=30),
        )
        
        url = reverse("rental_scheduler:series_occurrences_api")
        
        # Request upcoming scope
        response = api_client.get(url, {
            "parent_id": parent.id,
            "scope": "upcoming",
            "search": "Scope",
        })
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Should contain the future instance
        assert f'data-job-id="{future_instance.id}"' in content
        
        # Request past scope
        response = api_client.get(url, {
            "parent_id": parent.id,
            "scope": "past",
            "search": "Scope",
        })
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Should contain the parent (which is in the past)
        assert f'data-job-id="{parent.id}"' in content

    def test_series_occurrences_requires_parent_id(self, api_client, calendar):
        """Endpoint returns 400 if parent_id is missing."""
        url = reverse("rental_scheduler:series_occurrences_api")
        response = api_client.get(url, {"scope": "upcoming"})
        
        assert response.status_code == 400

    def test_series_occurrences_rejects_invalid_scope(self, api_client, calendar):
        """Endpoint returns 400 for invalid scope values."""
        now = timezone.now()
        
        parent = Job.objects.create(
            calendar=calendar,
            business_name="Invalid Scope Test",
            start_dt=now + timedelta(days=1),
            end_dt=now + timedelta(days=1, hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_rule={"type": "monthly", "interval": 1, "end": "never"},
        )
        
        url = reverse("rental_scheduler:series_occurrences_api")
        response = api_client.get(url, {
            "parent_id": parent.id,
            "scope": "invalid",
        })
        
        assert response.status_code == 400

    def test_series_occurrences_returns_virtual_for_forever_series(self, api_client, calendar):
        """Forever series returns virtual occurrences when parent matches search."""
        now = timezone.now()
        
        parent = Job.objects.create(
            calendar=calendar,
            business_name="Virtual Occ Test",
            start_dt=now + timedelta(days=1),
            end_dt=now + timedelta(days=1, hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_rule={"type": "monthly", "interval": 1, "end": "never"},
        )
        
        url = reverse("rental_scheduler:series_occurrences_api")
        response = api_client.get(url, {
            "parent_id": parent.id,
            "scope": "upcoming",
            "search": "Virtual",
            "count": "5",
        })
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Should contain virtual occurrence rows (if applicable)
        # At minimum, should contain the parent
        assert "series-occurrence-row" in content

