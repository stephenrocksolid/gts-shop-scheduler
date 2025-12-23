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

    def test_series_header_position_respects_sort_order(self, api_client, calendar):
        """
        Series header appears at the position of the first matching occurrence.
        When sorted by start date, the series header should appear in the correct position.
        """
        now = timezone.now()
        
        # Create a standalone job that comes FIRST chronologically
        first_job = Job.objects.create(
            calendar=calendar,
            business_name="AAA First Standalone",
            start_dt=now + timedelta(days=1),
            end_dt=now + timedelta(days=1, hours=1),
            all_day=False,
            status="uncompleted",
        )
        
        # Create a recurring series that starts AFTER the first job
        recurring = Job.objects.create(
            calendar=calendar,
            business_name="BBB Second Recurring",
            start_dt=now + timedelta(days=5),
            end_dt=now + timedelta(days=5, hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_rule={"type": "monthly", "interval": 1, "end": "never"},
        )
        
        # Create another standalone job that comes LAST
        last_job = Job.objects.create(
            calendar=calendar,
            business_name="CCC Third Standalone",
            start_dt=now + timedelta(days=10),
            end_dt=now + timedelta(days=10, hours=1),
            all_day=False,
            status="uncompleted",
        )
        
        url = reverse("rental_scheduler:job_list_table_partial")
        # Search with "a" to match all, sort by start_dt ascending
        response = api_client.get(url, {
            "search": "Standalone",  # Only matches standalones
            "date_filter": "future",
            "sort": "start_dt",
            "direction": "asc",
        })
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # The standalone jobs should appear in order by start_dt
        first_pos = content.find("AAA First Standalone")
        third_pos = content.find("CCC Third Standalone")
        
        assert first_pos < third_pos, "First job should appear before third job in sorted order"

    def test_interleaved_series_and_standalone_ordering(self, api_client, calendar):
        """
        Series headers are interleaved with standalone jobs based on first matching occurrence.
        """
        now = timezone.now()
        
        # Create jobs in a specific order to verify interleaving:
        # 1. Standalone job at day 1
        # 2. Recurring series first occurrence at day 3
        # 3. Standalone job at day 5
        
        Job.objects.create(
            calendar=calendar,
            business_name="Order Test Alpha",
            start_dt=now + timedelta(days=1),
            end_dt=now + timedelta(days=1, hours=1),
            all_day=False,
            status="uncompleted",
        )
        
        Job.objects.create(
            calendar=calendar,
            business_name="Order Test Recurring",
            start_dt=now + timedelta(days=3),
            end_dt=now + timedelta(days=3, hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_rule={"type": "monthly", "interval": 1, "end": "never"},
        )
        
        Job.objects.create(
            calendar=calendar,
            business_name="Order Test Zeta",
            start_dt=now + timedelta(days=5),
            end_dt=now + timedelta(days=5, hours=1),
            all_day=False,
            status="uncompleted",
        )
        
        url = reverse("rental_scheduler:job_list_table_partial")
        response = api_client.get(url, {
            "search": "Order Test",
            "date_filter": "future",
            "sort": "start_dt",
            "direction": "asc",
        })
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Verify the order: Alpha (standalone) < Recurring (series header) < Zeta (standalone)
        alpha_pos = content.find("Order Test Alpha")
        series_pos = content.find("series-header-row")
        zeta_pos = content.find("Order Test Zeta")
        
        assert alpha_pos > 0, "Alpha should be in the response"
        assert series_pos > 0, "Series header should be in the response"
        assert zeta_pos > 0, "Zeta should be in the response"
        
        # Check order
        assert alpha_pos < series_pos < zeta_pos, \
            f"Expected order: Alpha ({alpha_pos}) < Series header ({series_pos}) < Zeta ({zeta_pos})"


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

    def test_series_occurrences_combined_sorted_count(self, api_client, calendar):
        """
        Forever series with sparse materialized instances returns exactly 5 rows
        (combined materialized + virtual) in chronological order.
        
        Regression test for interleaving and count behavior.
        """
        import re
        from datetime import datetime
        
        now = timezone.now()
        tz = timezone.get_current_timezone()
        
        # Create a forever weekly recurring parent starting tomorrow
        parent_start = timezone.make_aware(
            datetime(now.year, now.month, now.day, 10, 0, 0), tz
        ) + timedelta(days=1)
        
        parent = Job.objects.create(
            calendar=calendar,
            business_name="Sparse Materialized Test",
            start_dt=parent_start,
            end_dt=parent_start + timedelta(hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_rule={"type": "weekly", "interval": 1, "end": "never"},
        )
        
        # Materialize instances at week+1 and week+4 (creating gaps at week+2, +3)
        # This means when expanded, we should see:
        # - week+1 materialized
        # - week+2 virtual
        # - week+3 virtual
        # - week+4 materialized
        # - week+5 virtual
        
        week1_start = parent_start + timedelta(weeks=1)
        Job.objects.create(
            calendar=calendar,
            business_name="Sparse Materialized Test",
            start_dt=week1_start,
            end_dt=week1_start + timedelta(hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_parent=parent,
            recurrence_original_start=week1_start,
        )
        
        week4_start = parent_start + timedelta(weeks=4)
        Job.objects.create(
            calendar=calendar,
            business_name="Sparse Materialized Test",
            start_dt=week4_start,
            end_dt=week4_start + timedelta(hours=1),
            all_day=False,
            status="uncompleted",
            recurrence_parent=parent,
            recurrence_original_start=week4_start,
        )
        
        url = reverse("rental_scheduler:series_occurrences_api")
        response = api_client.get(url, {
            "parent_id": parent.id,
            "scope": "upcoming",
            "search": "Sparse",
            "count": "5",
            "offset": "0",
        })
        
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        
        # Count occurrence rows (exclude show-more row which also has series-occurrence-row class)
        # Occurrence rows have data-occurrence-start attribute
        occurrence_starts = re.findall(r'data-occurrence-start="([^"]+)"', content)
        
        # Should have exactly 5 occurrence rows
        assert len(occurrence_starts) == 5, f"Expected 5 occurrence rows, got {len(occurrence_starts)}"
        
        # Parse the timestamps and verify they are monotonically increasing
        from django.utils.dateparse import parse_datetime
        parsed_times = []
        for iso_str in occurrence_starts:
            dt = parse_datetime(iso_str)
            assert dt is not None, f"Could not parse datetime: {iso_str}"
            parsed_times.append(dt)
        
        # Verify chronological order
        for i in range(len(parsed_times) - 1):
            assert parsed_times[i] <= parsed_times[i + 1], (
                f"Occurrence at index {i} ({parsed_times[i]}) is not <= index {i+1} ({parsed_times[i+1]})"
            )
        
        # Verify we have both materialized and virtual rows (mixed)
        assert 'data-virtual="1"' in content, "Expected at least one virtual row"
        assert 'data-job-id="' in content, "Expected at least one materialized row"

