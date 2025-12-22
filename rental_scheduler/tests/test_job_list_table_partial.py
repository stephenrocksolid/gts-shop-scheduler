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

