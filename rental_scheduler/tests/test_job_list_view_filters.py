from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from rental_scheduler.models import Job


@pytest.mark.django_db
def test_job_list_two_years_filter_limits_results(api_client, calendar):
    url = reverse("rental_scheduler:job_list")
    now = timezone.now()

    in_range = Job.objects.create(
        calendar=calendar,
        business_name="IN_RANGE",
        start_dt=now + timedelta(days=10),
        end_dt=now + timedelta(days=10, hours=1),
        all_day=False,
        status="uncompleted",
    )
    Job.objects.create(
        calendar=calendar,
        business_name="TOO_FAR",
        start_dt=now + timedelta(days=800),
        end_dt=now + timedelta(days=800, hours=1),
        all_day=False,
        status="uncompleted",
    )
    Job.objects.create(
        calendar=calendar,
        business_name="PAST",
        start_dt=now - timedelta(days=5),
        end_dt=now - timedelta(days=5, hours=-1),
        all_day=False,
        status="uncompleted",
    )

    response = api_client.get(url, {"date_filter": "two_years"})
    assert response.status_code == 200

    jobs = list(response.context["jobs"])
    assert in_range in jobs
    assert all(j.business_name != "TOO_FAR" for j in jobs)
    assert all(j.business_name != "PAST" for j in jobs)


@pytest.mark.django_db
def test_job_list_search_matches_phone_digits(api_client, calendar):
    url = reverse("rental_scheduler:job_list")
    now = timezone.now()

    job = Job.objects.create(
        calendar=calendar,
        business_name="PHONE_MATCH",
        phone="(620) 888-7050",
        start_dt=now + timedelta(days=1),
        end_dt=now + timedelta(days=1, hours=1),
        all_day=False,
        status="uncompleted",
    )

    response = api_client.get(url, {"search": "6208887050"})
    assert response.status_code == 200

    jobs = list(response.context["jobs"])
    assert job in jobs


@pytest.mark.django_db
def test_job_list_future_default_sort_is_ascending(api_client, calendar):
    url = reverse("rental_scheduler:job_list")
    now = timezone.now()

    Job.objects.create(
        calendar=calendar,
        business_name="FUTURE_10",
        start_dt=now + timedelta(days=10),
        end_dt=now + timedelta(days=10, hours=1),
        all_day=False,
        status="uncompleted",
    )
    Job.objects.create(
        calendar=calendar,
        business_name="FUTURE_2",
        start_dt=now + timedelta(days=2),
        end_dt=now + timedelta(days=2, hours=1),
        all_day=False,
        status="uncompleted",
    )
    Job.objects.create(
        calendar=calendar,
        business_name="FUTURE_5",
        start_dt=now + timedelta(days=5),
        end_dt=now + timedelta(days=5, hours=1),
        all_day=False,
        status="uncompleted",
    )

    response = api_client.get(url, {"date_filter": "future"})
    assert response.status_code == 200

    jobs = list(response.context["jobs"])
    assert [j.business_name for j in jobs] == ["FUTURE_2", "FUTURE_5", "FUTURE_10"]


@pytest.mark.django_db
def test_job_list_past_default_sort_is_descending(api_client, calendar):
    url = reverse("rental_scheduler:job_list")
    now = timezone.now()

    Job.objects.create(
        calendar=calendar,
        business_name="PAST_10",
        start_dt=now - timedelta(days=10),
        end_dt=now - timedelta(days=10, hours=-1),
        all_day=False,
        status="uncompleted",
    )
    Job.objects.create(
        calendar=calendar,
        business_name="PAST_1",
        start_dt=now - timedelta(days=1),
        end_dt=now - timedelta(days=1, hours=-1),
        all_day=False,
        status="uncompleted",
    )
    Job.objects.create(
        calendar=calendar,
        business_name="PAST_5",
        start_dt=now - timedelta(days=5),
        end_dt=now - timedelta(days=5, hours=-1),
        all_day=False,
        status="uncompleted",
    )

    response = api_client.get(url, {"date_filter": "past"})
    assert response.status_code == 200

    jobs = list(response.context["jobs"])
    assert [j.business_name for j in jobs] == ["PAST_1", "PAST_5", "PAST_10"]


@pytest.mark.django_db
def test_job_list_all_default_sort_is_upcoming_then_past(api_client, calendar):
    url = reverse("rental_scheduler:job_list")
    now = timezone.now()

    # Past jobs (should appear after future, in reverse chronological order)
    Job.objects.create(
        calendar=calendar,
        business_name="PAST_10",
        start_dt=now - timedelta(days=10),
        end_dt=now - timedelta(days=10, hours=-1),
        all_day=False,
        status="uncompleted",
    )
    Job.objects.create(
        calendar=calendar,
        business_name="PAST_1",
        start_dt=now - timedelta(days=1),
        end_dt=now - timedelta(days=1, hours=-1),
        all_day=False,
        status="uncompleted",
    )

    # Future jobs (should appear first, in chronological order)
    Job.objects.create(
        calendar=calendar,
        business_name="FUTURE_20",
        start_dt=now + timedelta(days=20),
        end_dt=now + timedelta(days=20, hours=1),
        all_day=False,
        status="uncompleted",
    )
    Job.objects.create(
        calendar=calendar,
        business_name="FUTURE_2",
        start_dt=now + timedelta(days=2),
        end_dt=now + timedelta(days=2, hours=1),
        all_day=False,
        status="uncompleted",
    )

    response = api_client.get(url)
    assert response.status_code == 200

    jobs = list(response.context["jobs"])
    assert [j.business_name for j in jobs] == ["FUTURE_2", "FUTURE_20", "PAST_1", "PAST_10"]


@pytest.mark.django_db
def test_job_list_search_punctuation_insensitive(api_client, calendar):
    """Search should match regardless of punctuation and spacing differences."""
    url = reverse("rental_scheduler:job_list")
    now = timezone.now()

    # Create a job with punctuated name
    job = Job.objects.create(
        calendar=calendar,
        business_name="Mt.Hope Fence",
        start_dt=now + timedelta(days=1),
        end_dt=now + timedelta(days=1, hours=1),
        all_day=False,
        status="uncompleted",
    )

    # All these variations should find the job
    search_variations = [
        "Mt. Hope",      # With period and space
        "Mt.Hope",       # With period, no space
        "Mt Hope",       # No period, with space
        "MTHOPE",        # No punctuation, uppercase
        "mthope",        # No punctuation, lowercase
        "mt hope fence", # Multiple words
    ]

    for query in search_variations:
        response = api_client.get(url, {"search": query})
        assert response.status_code == 200, f"Failed for query: {query}"
        jobs = list(response.context["jobs"])
        assert job in jobs, f"Job not found for query: '{query}'"


@pytest.mark.django_db
def test_job_list_search_strict_and_matching(api_client, calendar):
    """When all search terms match, should use strict AND (no widening)."""
    url = reverse("rental_scheduler:job_list")
    now = timezone.now()

    job = Job.objects.create(
        calendar=calendar,
        business_name="Mt.Hope Fence Company",
        start_dt=now + timedelta(days=1),
        end_dt=now + timedelta(days=1, hours=1),
        all_day=False,
        status="uncompleted",
    )

    # This should match strictly (all words present)
    response = api_client.get(url, {"search": "Hope Fence"})
    assert response.status_code == 200

    jobs = list(response.context["jobs"])
    assert job in jobs
    assert response.context.get("search_widened") is False


@pytest.mark.django_db
def test_job_list_search_fallback_to_or_when_no_strict_match(api_client, calendar):
    """When strict AND returns nothing, should fall back to OR matching."""
    url = reverse("rental_scheduler:job_list")
    now = timezone.now()

    # Create jobs that each match only one word
    job_hope = Job.objects.create(
        calendar=calendar,
        business_name="Hope Industries",
        start_dt=now + timedelta(days=1),
        end_dt=now + timedelta(days=1, hours=1),
        all_day=False,
        status="uncompleted",
    )
    job_smith = Job.objects.create(
        calendar=calendar,
        business_name="Smith Corporation",
        start_dt=now + timedelta(days=2),
        end_dt=now + timedelta(days=2, hours=1),
        all_day=False,
        status="uncompleted",
    )

    # Search for "Hope Smith" - no single job matches both, so should fall back to OR
    response = api_client.get(url, {"search": "Hope Smith"})
    assert response.status_code == 200

    jobs = list(response.context["jobs"])
    # Both jobs should be returned via OR fallback
    assert job_hope in jobs
    assert job_smith in jobs
    # The search_widened flag should be True
    assert response.context.get("search_widened") is True


@pytest.mark.django_db
def test_job_list_search_single_token_no_fallback(api_client, calendar):
    """Single token search should not trigger fallback (nothing to broaden to)."""
    url = reverse("rental_scheduler:job_list")
    now = timezone.now()

    Job.objects.create(
        calendar=calendar,
        business_name="Acme Corp",
        start_dt=now + timedelta(days=1),
        end_dt=now + timedelta(days=1, hours=1),
        all_day=False,
        status="uncompleted",
    )

    # Search for a term that won't match anything
    response = api_client.get(url, {"search": "nonexistent"})
    assert response.status_code == 200

    jobs = list(response.context["jobs"])
    assert len(jobs) == 0
    # No widening for single term
    assert response.context.get("search_widened") is False


@pytest.mark.django_db
def test_job_list_future_filter_includes_forever_parents(api_client, calendar):
    """Future date filter should include forever recurring parents even if their start_dt is in the past."""
    url = reverse("rental_scheduler:job_list")
    now = timezone.now()

    # Forever parent that started in the past (but has future occurrences)
    forever_parent = Job.objects.create(
        calendar=calendar,
        business_name="Forever Series",
        start_dt=now - timedelta(days=30),  # Started in the past
        end_dt=now - timedelta(days=30) + timedelta(hours=1),
        all_day=False,
        status="uncompleted",
        recurrence_rule={"type": "weekly", "interval": 1, "end": "never"},
    )

    # Regular job in the future
    future_job = Job.objects.create(
        calendar=calendar,
        business_name="Future Job",
        start_dt=now + timedelta(days=10),
        end_dt=now + timedelta(days=10, hours=1),
        all_day=False,
        status="uncompleted",
    )

    # Regular job in the past (should not appear)
    past_job = Job.objects.create(
        calendar=calendar,
        business_name="Past Job",
        start_dt=now - timedelta(days=5),
        end_dt=now - timedelta(days=5) + timedelta(hours=1),
        all_day=False,
        status="uncompleted",
    )

    response = api_client.get(url, {"date_filter": "future"})
    assert response.status_code == 200

    jobs = list(response.context["jobs"])
    # Forever parent should be included (has future occurrences)
    assert forever_parent in jobs
    # Future job should be included
    assert future_job in jobs
    # Past job should NOT be included
    assert past_job not in jobs
    # Context should indicate forever parents were included
    assert response.context.get("includes_forever_parents") is True


@pytest.mark.django_db
def test_job_list_two_years_filter_includes_forever_parents(api_client, calendar):
    """Two years filter should include forever recurring parents."""
    url = reverse("rental_scheduler:job_list")
    now = timezone.now()

    # Forever parent that started in the past
    forever_parent = Job.objects.create(
        calendar=calendar,
        business_name="Forever Monthly Series",
        start_dt=now - timedelta(days=60),
        end_dt=now - timedelta(days=60) + timedelta(hours=2),
        all_day=False,
        status="uncompleted",
        recurrence_rule={"type": "monthly", "interval": 1, "end": "never"},
    )

    response = api_client.get(url, {"date_filter": "two_years"})
    assert response.status_code == 200

    jobs = list(response.context["jobs"])
    # Forever parent should be included
    assert forever_parent in jobs
    assert response.context.get("includes_forever_parents") is True


