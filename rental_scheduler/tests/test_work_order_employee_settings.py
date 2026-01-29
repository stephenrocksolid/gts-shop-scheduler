import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_workorder_employee_settings_get(api_client):
    url = reverse("rental_scheduler:workorder_employee_settings")
    resp = api_client.get(url)
    assert resp.status_code == 200


@pytest.mark.django_db
def test_workorder_employee_settings_add_and_list(api_client):
    from rental_scheduler.models import WorkOrderEmployee

    url = reverse("rental_scheduler:workorder_employee_settings")
    resp = api_client.post(url, data={"action": "add", "name": "Alex Smith"})
    assert resp.status_code == 302
    assert WorkOrderEmployee.objects.filter(name="Alex Smith", is_active=True).exists()

    resp = api_client.get(url)
    assert resp.status_code == 200
    assert "Alex Smith" in resp.content.decode("utf-8")


@pytest.mark.django_db
def test_workorder_employee_settings_deactivate(api_client):
    from rental_scheduler.models import WorkOrderEmployee

    employee = WorkOrderEmployee.objects.create(name="Taylor Onsite", is_active=True)
    url = reverse("rental_scheduler:workorder_employee_settings")

    resp = api_client.post(
        url,
        data={
            "action": "set_active",
            "employee_id": str(employee.id),
            "is_active": "0",
        },
    )
    assert resp.status_code == 302

    employee.refresh_from_db()
    assert employee.is_active is False


@pytest.mark.django_db
def test_workorder_new_shows_only_active_employees(api_client, job):
    from rental_scheduler.models import WorkOrderEmployee

    active_employee = WorkOrderEmployee.objects.create(name="Employee Active 01", is_active=True)
    inactive_employee = WorkOrderEmployee.objects.create(name="Employee Inactive 01", is_active=False)

    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}"
    resp = api_client.get(url)
    assert resp.status_code == 200
    html = resp.content.decode("utf-8")

    assert active_employee.name in html
    assert inactive_employee.name not in html
