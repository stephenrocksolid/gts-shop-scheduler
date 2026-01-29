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


# =========================================================================
# HTMX-specific tests
# =========================================================================


@pytest.mark.django_db
def test_workorder_employee_settings_htmx_get_returns_modal_body(api_client):
    """HTMX GET should return modal body partial, not full page"""
    from rental_scheduler.models import WorkOrderEmployee

    WorkOrderEmployee.objects.create(name="Test Employee", is_active=True)
    
    url = reverse("rental_scheduler:workorder_employee_settings")
    resp = api_client.get(url, HTTP_HX_REQUEST='true')
    
    assert resp.status_code == 200
    html = resp.content.decode("utf-8")
    
    # Should contain modal body content
    assert "data-wo-emp-name-input" in html
    assert "Add employee" in html
    assert "Test Employee" in html
    
    # Should NOT contain full page layout elements
    assert "{% extends" not in html
    assert "{% block page_title %}" not in html


@pytest.mark.django_db
def test_workorder_employee_settings_htmx_post_add_returns_200(api_client):
    """HTMX POST should return 200 with updated modal body, not redirect"""
    from rental_scheduler.models import WorkOrderEmployee

    url = reverse("rental_scheduler:workorder_employee_settings")
    resp = api_client.post(
        url,
        data={"action": "add", "name": "HTMX Employee"},
        HTTP_HX_REQUEST='true'
    )
    
    # Should return 200 (not 302 redirect)
    assert resp.status_code == 200
    
    # Employee should be created
    assert WorkOrderEmployee.objects.filter(name="HTMX Employee", is_active=True).exists()
    
    # Response should contain modal body with the new employee
    html = resp.content.decode("utf-8")
    assert "HTMX Employee" in html
    assert "data-wo-emp-name-input" in html


@pytest.mark.django_db
def test_workorder_employee_settings_htmx_post_set_active_returns_200(api_client):
    """HTMX POST for set_active should return 200 with updated modal body, not redirect"""
    from rental_scheduler.models import WorkOrderEmployee

    employee = WorkOrderEmployee.objects.create(name="Toggle Employee", is_active=True)
    url = reverse("rental_scheduler:workorder_employee_settings")
    
    resp = api_client.post(
        url,
        data={
            "action": "set_active",
            "employee_id": str(employee.id),
            "is_active": "0",
        },
        HTTP_HX_REQUEST='true'
    )
    
    # Should return 200 (not 302 redirect)
    assert resp.status_code == 200
    
    # Employee should be deactivated
    employee.refresh_from_db()
    assert employee.is_active is False
    
    # Response should contain modal body
    html = resp.content.decode("utf-8")
    assert "Toggle Employee" in html
    assert "data-wo-emp-name-input" in html


@pytest.mark.django_db
def test_workorder_employee_settings_htmx_response_includes_oob_swap(api_client):
    """HTMX response should include OOB swap for Job By field"""
    from rental_scheduler.models import WorkOrderEmployee

    WorkOrderEmployee.objects.create(name="OOB Test Employee", is_active=True)
    
    url = reverse("rental_scheduler:workorder_employee_settings")
    resp = api_client.get(url, HTTP_HX_REQUEST='true')
    
    assert resp.status_code == 200
    html = resp.content.decode("utf-8")
    
    # Should contain OOB swap target
    assert 'id="wo-job-by-field"' in html
    assert 'hx-swap-oob="true"' in html
    
    # OOB section should contain the Job By select
    assert 'id="wo-job-by"' in html
    assert 'name="job_by_id"' in html
    assert "OOB Test Employee" in html


@pytest.mark.django_db
def test_workorder_employee_settings_htmx_post_rename_returns_200(api_client):
    """HTMX POST for rename should return 200 with updated modal body, not redirect"""
    from rental_scheduler.models import WorkOrderEmployee

    employee = WorkOrderEmployee.objects.create(name="Original Name", is_active=True)
    url = reverse("rental_scheduler:workorder_employee_settings")
    
    resp = api_client.post(
        url,
        data={
            "action": "rename",
            "employee_id": str(employee.id),
            "name": "Renamed Employee",
        },
        HTTP_HX_REQUEST='true'
    )
    
    # Should return 200 (not 302 redirect)
    assert resp.status_code == 200
    
    # Employee should be renamed
    employee.refresh_from_db()
    assert employee.name == "Renamed Employee"
    
    # Response should contain modal body with the renamed employee
    html = resp.content.decode("utf-8")
    assert "Renamed Employee" in html
    assert "data-wo-emp-name-input" in html


@pytest.mark.django_db
def test_workorder_employee_settings_post_rename_redirects(api_client):
    """Non-HTMX POST for rename should redirect (302)"""
    from rental_scheduler.models import WorkOrderEmployee

    employee = WorkOrderEmployee.objects.create(name="Original Name", is_active=True)
    url = reverse("rental_scheduler:workorder_employee_settings")
    
    resp = api_client.post(
        url,
        data={
            "action": "rename",
            "employee_id": str(employee.id),
            "name": "Renamed Employee",
        },
    )
    
    # Should redirect (not return 200)
    assert resp.status_code == 302
    
    # Employee should be renamed
    employee.refresh_from_db()
    assert employee.name == "Renamed Employee"


@pytest.mark.django_db
def test_workorder_employee_settings_rename_duplicate_name_error(api_client):
    """Rename should fail with error if new name already exists (case-insensitive)"""
    from rental_scheduler.models import WorkOrderEmployee

    existing_employee = WorkOrderEmployee.objects.create(name="Existing Employee", is_active=True)
    employee_to_rename = WorkOrderEmployee.objects.create(name="Different Name", is_active=True)
    url = reverse("rental_scheduler:workorder_employee_settings")
    
    resp = api_client.post(
        url,
        data={
            "action": "rename",
            "employee_id": str(employee_to_rename.id),
            "name": "Existing Employee",  # Exact match
        },
        HTTP_HX_REQUEST='true'
    )
    
    assert resp.status_code == 200
    
    # Employee should NOT be renamed
    employee_to_rename.refresh_from_db()
    assert employee_to_rename.name == "Different Name"
    
    # Response should contain error message
    html = resp.content.decode("utf-8")
    assert "Employee already exists" in html


@pytest.mark.django_db
def test_workorder_employee_settings_rename_duplicate_name_case_insensitive(api_client):
    """Rename should fail with error if new name already exists (case-insensitive check)"""
    from rental_scheduler.models import WorkOrderEmployee

    existing_employee = WorkOrderEmployee.objects.create(name="Existing Employee", is_active=True)
    employee_to_rename = WorkOrderEmployee.objects.create(name="Different Name", is_active=True)
    url = reverse("rental_scheduler:workorder_employee_settings")
    
    resp = api_client.post(
        url,
        data={
            "action": "rename",
            "employee_id": str(employee_to_rename.id),
            "name": "EXISTING EMPLOYEE",  # Different case
        },
        HTTP_HX_REQUEST='true'
    )
    
    assert resp.status_code == 200
    
    # Employee should NOT be renamed
    employee_to_rename.refresh_from_db()
    assert employee_to_rename.name == "Different Name"
    
    # Response should contain error message
    html = resp.content.decode("utf-8")
    assert "Employee already exists" in html


@pytest.mark.django_db
def test_workorder_employee_settings_rename_no_change_info_message(api_client):
    """Rename with same name should show info message and not update"""
    from rental_scheduler.models import WorkOrderEmployee

    employee = WorkOrderEmployee.objects.create(name="Same Name", is_active=True)
    original_updated_at = employee.updated_at
    url = reverse("rental_scheduler:workorder_employee_settings")
    
    resp = api_client.post(
        url,
        data={
            "action": "rename",
            "employee_id": str(employee.id),
            "name": "Same Name",  # Same name
        },
        HTTP_HX_REQUEST='true'
    )
    
    assert resp.status_code == 200
    
    # Employee name should remain the same
    employee.refresh_from_db()
    assert employee.name == "Same Name"
    
    # Response should contain info message
    html = resp.content.decode("utf-8")
    assert "No changes made" in html
