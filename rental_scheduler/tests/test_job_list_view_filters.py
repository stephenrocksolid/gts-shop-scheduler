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


