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


