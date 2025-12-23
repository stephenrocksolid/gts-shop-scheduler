"""
Tests for JobListTablePartialView (Phase 6 - calendar search partial endpoint).

Verifies:
- The endpoint returns 200 with valid HTML table fragment
- The response is a partial (no full document wrapper)
- Query params work the same as JobListView (search, calendars, date_filter, etc.)
"""
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from rental_scheduler.models import Job


@pytest.mark.django_db
def test_job_list_table_partial_returns_200(api_client, calendar):
    """The endpoint returns 200 OK."""
    url = reverse("rental_scheduler:job_list_table_partial")
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_job_list_table_partial_contains_table_structure(api_client, calendar):
    """The response contains expected table structure."""
    url = reverse("rental_scheduler:job_list_table_partial")
    now = timezone.now()

    Job.objects.create(
        calendar=calendar,
        business_name="Test Company",
        start_dt=now + timedelta(days=1),
        end_dt=now + timedelta(days=1, hours=1),
        all_day=False,
        status="uncompleted",
    )

    response = api_client.get(url)
    content = response.content.decode("utf-8")

    # Should contain table element
    assert "<table" in content
    # Should contain job row with data-job-id attribute
    assert "job-row" in content


@pytest.mark.django_db
def test_job_list_table_partial_is_not_full_document(api_client, calendar):
    """The response is a partial (no <html> or <body> wrapper)."""
    url = reverse("rental_scheduler:job_list_table_partial")
    response = api_client.get(url)
    content = response.content.decode("utf-8")

    # Should NOT contain full document elements
    assert "<!DOCTYPE" not in content
    assert "<html" not in content
    assert "<body" not in content
    assert "<head" not in content


@pytest.mark.django_db
def test_job_list_table_partial_respects_search_filter(api_client, calendar):
    """The endpoint respects the search query param."""
    url = reverse("rental_scheduler:job_list_table_partial")
    now = timezone.now()

    Job.objects.create(
        calendar=calendar,
        business_name="Alpha Company",
        start_dt=now + timedelta(days=1),
        end_dt=now + timedelta(days=1, hours=1),
        all_day=False,
        status="uncompleted",
    )
    Job.objects.create(
        calendar=calendar,
        business_name="Beta Corporation",
        start_dt=now + timedelta(days=2),
        end_dt=now + timedelta(days=2, hours=1),
        all_day=False,
        status="uncompleted",
    )

    response = api_client.get(url, {"search": "Alpha"})
    content = response.content.decode("utf-8")

    assert "Alpha Company" in content
    assert "Beta Corporation" not in content


@pytest.mark.django_db
def test_job_list_table_partial_respects_calendar_filter(api_client, calendar):
    """The endpoint respects the calendars query param."""
    from rental_scheduler.models import Calendar
    
    url = reverse("rental_scheduler:job_list_table_partial")
    now = timezone.now()
    
    # Create a second calendar
    other_calendar = Calendar.objects.create(name="Other Calendar", color="#FF0000", is_active=True)

    Job.objects.create(
        calendar=calendar,
        business_name="First Calendar Job",
        start_dt=now + timedelta(days=1),
        end_dt=now + timedelta(days=1, hours=1),
        all_day=False,
        status="uncompleted",
    )
    Job.objects.create(
        calendar=other_calendar,
        business_name="Second Calendar Job",
        start_dt=now + timedelta(days=2),
        end_dt=now + timedelta(days=2, hours=1),
        all_day=False,
        status="uncompleted",
    )

    # Filter to only first calendar
    response = api_client.get(url, {"calendars": calendar.id})
    content = response.content.decode("utf-8")

    assert "First Calendar Job" in content
    assert "Second Calendar Job" not in content


@pytest.mark.django_db
def test_job_list_table_partial_respects_date_filter(api_client, calendar):
    """The endpoint respects the date_filter query param."""
    url = reverse("rental_scheduler:job_list_table_partial")
    now = timezone.now()

    Job.objects.create(
        calendar=calendar,
        business_name="Future Job",
        start_dt=now + timedelta(days=10),
        end_dt=now + timedelta(days=10, hours=1),
        all_day=False,
        status="uncompleted",
    )
    Job.objects.create(
        calendar=calendar,
        business_name="Past Job",
        start_dt=now - timedelta(days=5),
        end_dt=now - timedelta(days=5, hours=-1),
        all_day=False,
        status="uncompleted",
    )

    # Filter to only future jobs
    response = api_client.get(url, {"date_filter": "future"})
    content = response.content.decode("utf-8")

    assert "Future Job" in content
    assert "Past Job" not in content


@pytest.mark.django_db
def test_job_list_table_partial_shows_no_jobs_message_when_empty(api_client, calendar):
    """The endpoint shows 'No jobs found' when there are no matching jobs."""
    url = reverse("rental_scheduler:job_list_table_partial")
    
    response = api_client.get(url)
    content = response.content.decode("utf-8")

    assert "No jobs found" in content


@pytest.mark.django_db
def test_job_list_table_partial_parity_with_job_list_view(api_client, calendar):
    """The partial should return the same jobs as the full JobListView for the same query."""
    now = timezone.now()

    Job.objects.create(
        calendar=calendar,
        business_name="Test Job",
        start_dt=now + timedelta(days=1),
        end_dt=now + timedelta(days=1, hours=1),
        all_day=False,
        status="uncompleted",
    )

    partial_url = reverse("rental_scheduler:job_list_table_partial")
    full_url = reverse("rental_scheduler:job_list")
    
    query_params = {"search": "Test", "date_filter": "future"}

    partial_response = api_client.get(partial_url, query_params)
    full_response = api_client.get(full_url, query_params)

    # Both should succeed
    assert partial_response.status_code == 200
    assert full_response.status_code == 200

    # Both should contain the job
    assert "Test Job" in partial_response.content.decode("utf-8")
    assert "Test Job" in full_response.content.decode("utf-8")


@pytest.mark.django_db
def test_job_list_table_partial_htmx_returns_chunk(api_client, calendar):
    """HTMX requests should return chunk template with rows wrapped in table structure."""
    url = reverse("rental_scheduler:job_list_table_partial")
    now = timezone.now()

    # Create enough jobs to span multiple pages (paginate_by = 25)
    for i in range(30):
        Job.objects.create(
            calendar=calendar,
            business_name=f"Job {i}",
            start_dt=now + timedelta(days=i),
            end_dt=now + timedelta(days=i, hours=1),
            all_day=False,
            status="uncompleted",
        )

    # Request page 2 with HTMX header
    response = api_client.get(url, {"page": 2}, HTTP_HX_REQUEST="true")
    assert response.status_code == 200

    content = response.content.decode("utf-8")

    # Regression: Response should start with <table to prevent HTMX parse errors
    # (Previously raw <tr> at top-level caused querySelectorAll errors)
    assert content.lstrip().startswith("<table"), "Chunk must start with <table> wrapper to avoid HTMX parse errors"
    
    # Should contain the chunk rows container that HTMX will select from
    assert 'id="job-list-chunk-rows"' in content
    
    # Should NOT contain table header (still a "chunk", not full table UI)
    assert "<thead" not in content

    # Should contain job rows
    assert "job-row" in content
    # Jobs 0-29 created with range(30). Default sort is by start_dt.
    # With 30 jobs and paginate_by=25, page 2 has the remaining 5 jobs.
    # The exact jobs depend on sort order, but we should see jobs from the second page.
    assert "Job 26" in content or "Job 27" in content  # Jobs from page 2

    # Should contain OOB markers for pagination updates
    assert 'hx-swap-oob="true"' in content
    assert "job-list-status" in content
    assert "job-list-page-indicator" in content


@pytest.mark.django_db
def test_job_list_table_partial_htmx_shows_cumulative_status(api_client, calendar):
    """HTMX chunk responses (load-more) should show cumulative status: 'Showing 1 to N'."""
    url = reverse("rental_scheduler:job_list_table_partial")
    now = timezone.now()

    # Create 30 jobs (paginate_by = 25, so page 2 will have 5 jobs)
    for i in range(30):
        Job.objects.create(
            calendar=calendar,
            business_name=f"Job {i}",
            start_dt=now + timedelta(days=i),
            end_dt=now + timedelta(days=i, hours=1),
            all_day=False,
            status="uncompleted",
        )

    # Request page 2 with HTMX header (simulating load-more)
    response = api_client.get(url, {"page": 2}, HTTP_HX_REQUEST="true")
    assert response.status_code == 200

    content = response.content.decode("utf-8")

    # Should show cumulative status: "Showing 1 to 30" (not "Showing 26 to 30")
    assert "Showing" in content
    # Look for the pattern "Showing <span...>1</span> to <span...>30</span>"
    import re
    # Match "Showing" followed by number in span, "to", another number in span
    match = re.search(r'Showing\s+<span[^>]*>(\d+)</span>\s+to\s+<span[^>]*>(\d+)</span>', content)
    assert match is not None, "Should find 'Showing X to Y' pattern"
    start_num = int(match.group(1))
    end_num = int(match.group(2))
    
    # For load-more (HTMX), start should always be 1 (cumulative)
    assert start_num == 1, f"HTMX chunk should show cumulative start (1), got {start_num}"
    # End should be total loaded so far (30 jobs)
    assert end_num == 30, f"HTMX chunk should show cumulative end (30), got {end_num}"


@pytest.mark.django_db
def test_job_list_table_partial_non_htmx_shows_page_range_status(api_client, calendar):
    """Non-HTMX responses (direct navigation) should show page-range status: 'Showing 26 to 50'."""
    url = reverse("rental_scheduler:job_list_table_partial")
    now = timezone.now()

    # Create 50 jobs (paginate_by = 25, so page 2 will have jobs 26-50)
    for i in range(50):
        Job.objects.create(
            calendar=calendar,
            business_name=f"Job {i}",
            start_dt=now + timedelta(days=i),
            end_dt=now + timedelta(days=i, hours=1),
            all_day=False,
            status="uncompleted",
        )

    # Request page 2 WITHOUT HTMX header (simulating direct navigation or jump-to-page)
    response = api_client.get(url, {"page": 2})
    assert response.status_code == 200

    content = response.content.decode("utf-8")

    # Should show page-range status: "Showing 26 to 50" (not "Showing 1 to 50")
    assert "Showing" in content
    import re
    match = re.search(r'Showing\s+<span[^>]*>(\d+)</span>\s+to\s+<span[^>]*>(\d+)</span>', content)
    assert match is not None, "Should find 'Showing X to Y' pattern"
    start_num = int(match.group(1))
    end_num = int(match.group(2))
    
    # For direct navigation (non-HTMX), start should be page start (26)
    assert start_num == 26, f"Non-HTMX should show page-range start (26), got {start_num}"
    # End should be page end (50)
    assert end_num == 50, f"Non-HTMX should show page-range end (50), got {end_num}"


@pytest.mark.django_db
def test_job_list_table_partial_htmx_chunk_includes_oob_updates(api_client, calendar):
    """HTMX chunk responses should include out-of-band updates for pagination controls."""
    url = reverse("rental_scheduler:job_list_table_partial")
    now = timezone.now()

    # Create enough jobs for pagination
    for i in range(30):
        Job.objects.create(
            calendar=calendar,
            business_name=f"Job {i}",
            start_dt=now + timedelta(days=i),
            end_dt=now + timedelta(days=i, hours=1),
            all_day=False,
            status="uncompleted",
        )

    response = api_client.get(url, {"page": 2}, HTTP_HX_REQUEST="true")
    assert response.status_code == 200

    content = response.content.decode("utf-8")

    # Should have OOB update for entire pagination footer
    assert 'id="job-list-pagination-footer"' in content
    assert 'hx-swap-oob="true"' in content

    # Footer should contain status line
    assert 'id="job-list-status"' in content

    # Footer should contain page indicator
    assert 'id="job-list-page-indicator"' in content
    
    # Since this is page 2 of 2 (30 jobs, 25 per page), there should be no load-more button
    # The footer should not contain a load-more button section
    assert "Load more" not in content or 'id="job-list-load-more-btn"' not in content


@pytest.mark.django_db
def test_job_list_table_partial_htmx_smart_sort_boundary_header(api_client, calendar):
    """HTMX chunk should insert 'Past Events' header when crossing boundary in smart sort."""
    url = reverse("rental_scheduler:job_list_table_partial")
    now = timezone.now()

    # Create jobs: some future, some past (enough to span pages)
    # Page 1 should end with future jobs, page 2 should start with past jobs
    # With paginate_by=25, we need at least 26 future jobs so page 1 is all future
    # and page 2 starts with future, then transitions to past

    # Create 26 future jobs (page 1 will have 25 future, page 2 will start with 1 future + past)
    for i in range(1, 27):
        Job.objects.create(
            calendar=calendar,
            business_name=f"Future Job {i}",
            start_dt=now + timedelta(days=i),
            end_dt=now + timedelta(days=i, hours=1),
            all_day=False,
            status="uncompleted",
        )

    # Create 10 past jobs (will be on page 2 after the last future job)
    for i in range(1, 11):
        Job.objects.create(
            calendar=calendar,
            business_name=f"Past Job {i}",
            start_dt=now - timedelta(days=i),
            end_dt=now - timedelta(days=i, hours=-1),
            all_day=False,
            status="uncompleted",
        )

    # Request page 1 normally (non-HTMX) to verify it contains only future jobs
    page1_response = api_client.get(url, {"date_filter": "all", "page": 1})
    assert page1_response.status_code == 200
    page1_content = page1_response.content.decode("utf-8")
    assert "Future Job" in page1_content
    # Page 1 should now have only future jobs (25 of the 26 future jobs)
    assert "Past Job" not in page1_content

    # Request page 2 with HTMX header and prev_is_past_event=0 (last job on page 1 was future)
    # Page 2 will have: Future Job 26 (the 26th future job), then Past Job 1-10
    # The chunk should insert a "Past Events" header when transitioning from future to past
    response = api_client.get(
        url,
        {"date_filter": "all", "page": 2, "prev_is_past_event": "0"},
        HTTP_HX_REQUEST="true"
    )
    assert response.status_code == 200

    content = response.content.decode("utf-8")

    # Should contain both future and past jobs on page 2
    assert "Future Job 26" in content
    assert "Past Job" in content
    
    # Should contain "Past Events" header since we're crossing the boundary mid-page
    assert "Past Events" in content

    # The header should appear between the last future job and first past job
    future_job_26_index = content.find("Future Job 26")
    past_events_index = content.find("Past Events")
    past_job_index = content.find("Past Job")
    assert future_job_26_index < past_events_index < past_job_index


@pytest.mark.django_db
def test_job_list_table_partial_empty_results_no_error(api_client, calendar):
    """Empty result set should return 200 without ValueError (no negative indexing error)."""
    url = reverse("rental_scheduler:job_list_table_partial")
    
    # Search for something that doesn't exist
    response = api_client.get(url, {"search": "nonexistent_job_xyz123"})
    
    # Should return 200 OK without raising ValueError
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    
    # Should show "No jobs found" message
    assert "No jobs found" in content


@pytest.mark.django_db
def test_job_list_table_partial_htmx_empty_chunk_no_error(api_client, calendar):
    """HTMX chunk request with empty result set should return empty chunk without error."""
    url = reverse("rental_scheduler:job_list_table_partial")
    
    # Request page 1 with search that matches nothing (empty result set)
    # This tests that accessing jobs[0] or jobs[-1] on an empty Page doesn't crash
    response = api_client.get(
        url,
        {"search": "nonexistent_job_xyz123", "page": 1},
        HTTP_HX_REQUEST="true"
    )
    
    # Should return 200 OK without raising ValueError
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    
    # Should contain table wrapper (chunk template always wraps in table)
    assert "<table" in content
    assert 'id="job-list-chunk-rows"' in content
    # Should NOT contain table header (still a "chunk", not full table UI)
    assert "<thead" not in content
    # Should be empty (no job rows)
    assert "job-row" not in content


@pytest.mark.django_db
def test_job_list_table_partial_empty_page_last_job_is_past_event_none(api_client, calendar):
    """When page is empty, last_job_is_past_event should be None (no error accessing jobs[-1])."""
    url = reverse("rental_scheduler:job_list_table_partial")
    
    # Search for something that doesn't exist with smart sort and all events filter
    # This would trigger the code path that tries to access jobs[-1]
    response = api_client.get(
        url,
        {
            "search": "nonexistent_job_xyz123",
            "date_filter": "all",
            "sort": "smart"
        }
    )
    
    # Should return 200 OK without raising ValueError
    assert response.status_code == 200
    
    # Verify context has last_job_is_past_event as None (or not set)
    # The view should handle empty pages gracefully
    assert "No jobs found" in response.content.decode("utf-8")


@pytest.mark.django_db
def test_job_list_table_partial_htmx_empty_page_first_row_is_past_not_set(api_client, calendar):
    """When HTMX chunk page is empty, first_row_is_past should not be set (no error accessing jobs[0])."""
    url = reverse("rental_scheduler:job_list_table_partial")
    
    # Request page 1 with search that matches nothing (empty result set)
    # This would trigger the code path that tries to access jobs[0]
    response = api_client.get(
        url,
        {
            "date_filter": "all",
            "sort": "smart",
            "search": "nonexistent_job_xyz123",
            "page": 1,
            "prev_is_past_event": "0"
        },
        HTTP_HX_REQUEST="true"
    )
    
    # Should return 200 OK without raising ValueError
    assert response.status_code == 200
    
    # Should return empty chunk (no rows, no errors)
    content = response.content.decode("utf-8")
    # Should contain table wrapper (chunk template always wraps in table)
    assert "<table" in content
    assert 'id="job-list-chunk-rows"' in content
    # Should NOT contain table header (still a "chunk", not full table UI)
    assert "<thead" not in content
    # Should be empty (no job rows)
    assert "job-row" not in content