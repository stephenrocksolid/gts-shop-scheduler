import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_job_detail_api_includes_calendar_name(api_client, job):
    url = reverse("rental_scheduler:job_detail_api", args=[job.id])
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert data["calendar_name"] == job.calendar.name


