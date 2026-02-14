import json
import re
from decimal import Decimal

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_workorder_new_prefills_from_job(api_client, job):
    # Arrange: put data on the job that should prefill WO fields
    job.repair_notes = "Fix brakes"
    job.trailer_details = "2020 Great Dane"
    job.trailer_color = "Blue"
    job.trailer_serial = "SN-123"
    job.save()

    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}"

    # Act
    resp = api_client.get(url)

    # Assert
    assert resp.status_code == 200
    html = resp.content.decode("utf-8")
    assert "Fix brakes" in html
    assert "2020 Great Dane" in html
    assert "Blue" in html
    assert "SN-123" in html
    
    # Assert: State field is now a select dropdown with state options
    assert '<select' in html and 'data-wo-cust-state' in html
    assert '<option value="TN">TN — Tennessee</option>' in html
    assert '<option value="PR">PR — Puerto Rico</option>' in html
    assert '<option value="">Select…</option>' in html


@pytest.mark.django_db
def test_workorder_new_post_creates_work_order_v2_and_lines(api_client, job):
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=1000)

    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}"

    resp = api_client.post(
        url,
        data={
            "notes": "Repair notes",
            "trailer_make_model": "Model X",
            "trailer_color": "Red",
            "trailer_serial": "SER-1",
            "customer_org_id": "123",
            "job_by_rep_id": "",
            "discount_type": "amount",
            "discount_value": "0.00",
            # Single line item
            "line_itemid": ["123"],
            "line_itemnumber_snapshot": ["PN-123"],
            "line_description_snapshot": ["Brake pads"],
            "line_qty": ["2.00"],
            "line_price": ["50.00"],
        },
    )

    assert resp.status_code == 302

    wo = WorkOrderV2.objects.get(job=job)
    assert wo.number == 1000
    assert wo.subtotal == Decimal("100.00")
    assert wo.discount_amount == Decimal("0.00")
    assert wo.tax_amount == Decimal("0.00")
    assert wo.tax_rate_snapshot == Decimal("0.0000")
    assert wo.total == Decimal("100.00")

    lines = list(wo.lines.all())
    assert len(lines) == 1
    assert lines[0].itemid == 123
    assert lines[0].amount == Decimal("100.00")


@pytest.mark.django_db
def test_workorder_edit_updates_lines_and_discount(api_client, job):
    from rental_scheduler.models import WorkOrderLineV2, WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=200)
    wo = WorkOrderV2.objects.create(job=job, discount_type="amount", discount_value=Decimal("0.00"))
    WorkOrderLineV2.objects.create(work_order=wo, itemid=1, qty=Decimal("1.00"), price=Decimal("10.00"))

    url = reverse("rental_scheduler:workorder_edit", args=[wo.pk])

    resp = api_client.post(
        url,
        data={
            "notes": "Updated",
            "trailer_make_model": "",
            "trailer_color": "",
            "trailer_serial": "",
            "customer_org_id": "456",
            "job_by_rep_id": "",
            "discount_type": "percent",
            "discount_value": "10.00",
            # Replace lines (2 lines now)
            "line_itemid": ["10", "11"],
            "line_itemnumber_snapshot": ["PN-10", "PN-11"],
            "line_description_snapshot": ["Item 10", "Item 11"],
            "line_qty": ["1.00", "2.00"],
            "line_price": ["100.00", "50.00"],
        },
    )

    assert resp.status_code == 302

    wo.refresh_from_db()
    assert wo.discount_type == "percent"
    assert wo.subtotal == Decimal("200.00")
    assert wo.discount_amount == Decimal("20.00")
    assert wo.tax_amount == Decimal("0.00")
    assert wo.total == Decimal("180.00")
    assert wo.notes == "Updated"

    assert list(wo.lines.values_list("itemid", flat=True)) == [10, 11]


@pytest.mark.django_db
def test_workorder_edit_includes_initial_customer_json(api_client, job):
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=300)
    wo = WorkOrderV2.objects.create(
        job=job,
        discount_type="amount",
        discount_value=Decimal("0.00"),
        customer_org_id=123,
    )

    url = reverse("rental_scheduler:workorder_edit", args=[wo.pk])
    resp = api_client.get(url)

    assert resp.status_code == 200
    html = resp.content.decode("utf-8")
    assert 'id="wo-initial-customer"' in html
    assert re.search(r'"org_id"\s*:\s*123', html)


@pytest.mark.django_db
def test_accounting_customers_search_returns_503_when_not_configured(api_client):
    url = reverse("rental_scheduler:accounting_customers_search")
    resp = api_client.get(url, data={"q": "test"})
    assert resp.status_code == 503
    assert "error" in resp.json()


@pytest.mark.django_db
def test_accounting_items_search_returns_503_when_not_configured(api_client):
    url = reverse("rental_scheduler:accounting_items_search")
    resp = api_client.get(url, data={"q": "test"})
    assert resp.status_code == 503
    assert "error" in resp.json()


@pytest.mark.django_db
def test_accounting_customers_create_returns_503_when_not_configured(api_client):
    url = reverse("rental_scheduler:accounting_customers_create")
    resp = api_client.post(
        url,
        data=json.dumps({"name": "New Customer"}),
        content_type="application/json",
    )
    assert resp.status_code == 503
    assert "error" in resp.json()


@pytest.mark.django_db
def test_accounting_customers_update_returns_503_when_not_configured(api_client):
    url = reverse("rental_scheduler:accounting_customers_update", args=[123])
    resp = api_client.post(
        url,
        data=json.dumps({"name": "Updated Customer"}),
        content_type="application/json",
    )
    assert resp.status_code == 503
    assert "error" in resp.json()


# =============================================================================
# Work Order page UI exclusion tests (Job Panel / Workspace bar)
# =============================================================================


@pytest.mark.django_db
def test_workorder_new_excludes_job_panel_and_workspace_bar(api_client, job):
    """Work Order new page should NOT render Job Panel or Workspace bar."""
    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}"
    resp = api_client.get(url)
    html = resp.content.decode("utf-8")

    # These IDs are present in the includes when rendered
    assert 'id="job-panel"' not in html
    assert 'id="workspace-bar"' not in html


@pytest.mark.django_db
def test_workorder_edit_excludes_job_panel_and_workspace_bar(api_client, job):
    """Work Order edit page should NOT render Job Panel or Workspace bar."""
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=500)
    wo = WorkOrderV2.objects.create(job=job, discount_type="amount", discount_value=Decimal("0.00"))

    url = reverse("rental_scheduler:workorder_edit", args=[wo.pk])
    resp = api_client.get(url)
    html = resp.content.decode("utf-8")

    assert 'id="job-panel"' not in html
    assert 'id="workspace-bar"' not in html


# =============================================================================
# Back navigation tests (next param)
# =============================================================================


@pytest.mark.django_db
def test_workorder_new_back_link_defaults_to_job_list(api_client, job):
    """Without next param, back link should default to job list."""
    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}"
    resp = api_client.get(url)
    html = resp.content.decode("utf-8")

    job_list_url = reverse("rental_scheduler:job_list")
    assert f'href="{job_list_url}?open_job={job.id}"' in html
    assert "Back to Jobs" in html


@pytest.mark.django_db
def test_workorder_new_back_link_uses_next_param_for_calendar(api_client, job):
    """With next param pointing to calendar, back link should go to calendar."""
    calendar_url = reverse("rental_scheduler:calendar")
    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}&next={calendar_url}"
    resp = api_client.get(url)
    html = resp.content.decode("utf-8")

    assert f'href="{calendar_url}?open_job={job.id}"' in html
    assert "Back to Calendar" in html


@pytest.mark.django_db
def test_workorder_new_rejects_external_next_url(api_client, job):
    """External URLs in next param should be rejected (open redirect prevention)."""
    evil_url = "https://evil.test/phish"
    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}&next={evil_url}"
    resp = api_client.get(url)
    html = resp.content.decode("utf-8")

    # Should fall back to job list, not use the evil URL
    job_list_url = reverse("rental_scheduler:job_list")
    assert f'href="{job_list_url}?open_job={job.id}"' in html
    assert evil_url not in html


@pytest.mark.django_db
def test_workorder_new_existing_wo_redirect_preserves_next(api_client, job):
    """When a WO already exists, redirect to edit should preserve the next param."""
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=600)
    # Pre-create a WO so the new endpoint redirects to edit
    wo = WorkOrderV2.objects.create(job=job, discount_type="amount", discount_value=Decimal("0.00"))

    calendar_url = reverse("rental_scheduler:calendar")
    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}&next={calendar_url}"

    # GET request should redirect to edit with next preserved
    resp = api_client.get(url)

    assert resp.status_code == 302
    assert "next=" in resp.url
    assert str(wo.pk) in resp.url


@pytest.mark.django_db
def test_workorder_edit_renders_next_in_hidden_field(api_client, job):
    """Edit page should include next value in hidden form field for POST round-trip."""
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=700)
    wo = WorkOrderV2.objects.create(job=job, discount_type="amount", discount_value=Decimal("0.00"))

    calendar_url = reverse("rental_scheduler:calendar")
    url = reverse("rental_scheduler:workorder_edit", args=[wo.pk]) + f"?next={calendar_url}"

    resp = api_client.get(url)
    html = resp.content.decode("utf-8")

    # Should have hidden input with next value
    assert f'name="next" value="{calendar_url}?open_job={job.id}"' in html


@pytest.mark.django_db
def test_workorder_edit_renders_next_in_hidden_field_for_job_list(api_client, job):
    """Edit page should append open_job when next points to job list."""
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=701)
    wo = WorkOrderV2.objects.create(job=job, discount_type="amount", discount_value=Decimal("0.00"))

    job_list_url = reverse("rental_scheduler:job_list")
    url = reverse("rental_scheduler:workorder_edit", args=[wo.pk]) + f"?next={job_list_url}"

    resp = api_client.get(url)
    html = resp.content.decode("utf-8")
    assert f'name="next" value="{job_list_url}?open_job={job.id}"' in html


# =============================================================================
# Customer requirement tests
# =============================================================================


@pytest.mark.django_db
def test_workorder_new_requires_customer(api_client, job):
    """POST without customer_org_id should re-render with error."""
    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}"

    resp = api_client.post(
        url,
        data={
            "notes": "Test",
            "trailer_make_model": "",
            "trailer_color": "",
            "trailer_serial": "",
            "customer_org_id": "",
            "job_by_rep_id": "",
            "discount_type": "amount",
            "discount_value": "0.00",
            "line_itemid": ["123"],
            "line_itemnumber_snapshot": ["PN-123"],
            "line_description_snapshot": ["Test"],
            "line_qty": ["1.00"],
            "line_price": ["10.00"],
        },
    )

    assert resp.status_code == 200
    html = resp.content.decode("utf-8")
    assert "Customer is required" in html


@pytest.mark.django_db
def test_workorder_edit_requires_customer(api_client, job):
    """POST edit without customer_org_id should re-render with error."""
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=800)
    wo = WorkOrderV2.objects.create(
        job=job,
        customer_org_id=999,
        discount_type="amount",
        discount_value=Decimal("0.00"),
    )

    url = reverse("rental_scheduler:workorder_edit", args=[wo.pk])

    resp = api_client.post(
        url,
        data={
            "notes": "Updated",
            "trailer_make_model": "",
            "trailer_color": "",
            "trailer_serial": "",
            "customer_org_id": "",
            "job_by_rep_id": "",
            "discount_type": "amount",
            "discount_value": "0.00",
            "line_itemid": ["123"],
            "line_itemnumber_snapshot": ["PN-123"],
            "line_description_snapshot": ["Test"],
            "line_qty": ["1.00"],
            "line_price": ["10.00"],
        },
    )

    assert resp.status_code == 200
    html = resp.content.decode("utf-8")
    assert "Customer is required" in html


# =============================================================================
# Save & go back redirect tests
# =============================================================================


@pytest.mark.django_db
def test_workorder_new_save_and_go_back_redirects_to_back_url(api_client, job):
    """POST with after_save=back should redirect to back_url."""
    from rental_scheduler.models import WorkOrderNumberSequence

    WorkOrderNumberSequence.get_solo(start_number=900)
    calendar_url = reverse("rental_scheduler:calendar")
    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}&next={calendar_url}"

    resp = api_client.post(
        url,
        data={
            "notes": "Test",
            "trailer_make_model": "",
            "trailer_color": "",
            "trailer_serial": "",
            "customer_org_id": "789",
            "job_by_rep_id": "",
            "discount_type": "amount",
            "discount_value": "0.00",
            "after_save": "back",
            "line_itemid": ["123"],
            "line_itemnumber_snapshot": ["PN-123"],
            "line_description_snapshot": ["Test"],
            "line_qty": ["1.00"],
            "line_price": ["10.00"],
        },
    )

    assert resp.status_code == 302
    # Should redirect to calendar with open_job param
    assert calendar_url in resp.url
    assert f"open_job={job.id}" in resp.url


@pytest.mark.django_db
def test_workorder_edit_save_and_go_back_redirects_to_back_url(api_client, job):
    """POST edit with after_save=back should redirect to back_url."""
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=1000)
    wo = WorkOrderV2.objects.create(
        job=job,
        customer_org_id=111,
        discount_type="amount",
        discount_value=Decimal("0.00"),
    )

    job_list_url = reverse("rental_scheduler:job_list")
    url = reverse("rental_scheduler:workorder_edit", args=[wo.pk]) + f"?next={job_list_url}"

    resp = api_client.post(
        url,
        data={
            "notes": "Updated",
            "trailer_make_model": "",
            "trailer_color": "",
            "trailer_serial": "",
            "customer_org_id": "222",
            "job_by_rep_id": "",
            "discount_type": "amount",
            "discount_value": "0.00",
            "after_save": "back",
            "line_itemid": ["123"],
            "line_itemnumber_snapshot": ["PN-123"],
            "line_description_snapshot": ["Test"],
            "line_qty": ["1.00"],
            "line_price": ["10.00"],
        },
    )

    assert resp.status_code == 302
    # Should redirect to job list (back_url)
    assert job_list_url in resp.url
    assert f"open_job={job.id}" in resp.url


# =============================================================================
# Tax-related tests
# =============================================================================


@pytest.mark.django_db
def test_work_order_customer_tax_rate_returns_zero_when_not_configured(api_client):
    url = reverse("rental_scheduler:work_order_customer_tax_rate")
    resp = api_client.get(url, data={"customer_org_id": "123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["tax_rate"] == "0.00"
    assert data["exempt"] is True


@pytest.mark.django_db
def test_work_order_customer_tax_rate_requires_customer_org_id(api_client):
    url = reverse("rental_scheduler:work_order_customer_tax_rate")
    resp = api_client.get(url)
    assert resp.status_code == 400
    assert "customer_org_id" in resp.json().get("error", "")


@pytest.mark.django_db
def test_work_order_customer_tax_rate_rejects_non_integer(api_client):
    url = reverse("rental_scheduler:work_order_customer_tax_rate")
    resp = api_client.get(url, data={"customer_org_id": "abc"})
    assert resp.status_code == 400


@pytest.mark.django_db
def test_compute_work_order_totals_with_tax():
    from rental_scheduler.utils.work_orders import compute_work_order_totals

    subtotal, discount_amount, tax_amount, total = compute_work_order_totals(
        line_items=[{"qty": Decimal("2.00"), "price": Decimal("50.00")}],
        discount_type="amount",
        discount_value=Decimal("0.00"),
        tax_rate=Decimal("7.00"),
    )

    assert subtotal == Decimal("100.00")
    assert discount_amount == Decimal("0.00")
    assert tax_amount == Decimal("7.00")
    assert total == Decimal("107.00")


@pytest.mark.django_db
def test_compute_work_order_totals_tax_after_discount():
    from rental_scheduler.utils.work_orders import compute_work_order_totals

    subtotal, discount_amount, tax_amount, total = compute_work_order_totals(
        line_items=[{"qty": Decimal("1.00"), "price": Decimal("200.00")}],
        discount_type="percent",
        discount_value=Decimal("10.00"),
        tax_rate=Decimal("7.00"),
    )

    assert subtotal == Decimal("200.00")
    assert discount_amount == Decimal("20.00")
    assert tax_amount == Decimal("12.60")
    assert total == Decimal("192.60")


@pytest.mark.django_db
def test_compute_work_order_totals_zero_tax():
    from rental_scheduler.utils.work_orders import compute_work_order_totals

    subtotal, discount_amount, tax_amount, total = compute_work_order_totals(
        line_items=[{"qty": Decimal("1.00"), "price": Decimal("100.00")}],
        discount_type="amount",
        discount_value=Decimal("0.00"),
        tax_rate=Decimal("0.00"),
    )

    assert subtotal == Decimal("100.00")
    assert tax_amount == Decimal("0.00")
    assert total == Decimal("100.00")


@pytest.mark.django_db
def test_workorder_model_recalculate_totals_with_tax(job):
    from rental_scheduler.models import WorkOrderLineV2, WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=2000)
    wo = WorkOrderV2.objects.create(
        job=job,
        customer_org_id=123,
        discount_type="amount",
        discount_value=Decimal("0.00"),
    )
    WorkOrderLineV2.objects.create(work_order=wo, itemid=1, qty=Decimal("1.00"), price=Decimal("100.00"))

    wo.recalculate_totals(tax_rate=Decimal("7.00"), save=True)
    wo.refresh_from_db()

    assert wo.tax_rate_snapshot == Decimal("7.0000")
    assert wo.tax_amount == Decimal("7.00")
    assert wo.total == Decimal("107.00")


@pytest.mark.django_db
def test_workorder_new_with_user_specified_number(api_client, job):
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=100)

    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}"
    resp = api_client.post(
        url,
        data={
            "number": "500",
            "notes": "",
            "customer_org_id": "1",
            "job_by_rep_id": "",
            "discount_type": "amount",
            "discount_value": "0.00",
        },
    )

    assert resp.status_code == 302
    wo = WorkOrderV2.objects.get(job=job)
    assert wo.number == 500


@pytest.mark.django_db
def test_workorder_new_user_number_advances_sequence(api_client, job):
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=100)

    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}"
    api_client.post(
        url,
        data={
            "number": "500",
            "notes": "",
            "customer_org_id": "1",
            "job_by_rep_id": "",
            "discount_type": "amount",
            "discount_value": "0.00",
        },
    )

    seq = WorkOrderNumberSequence.get_solo()
    assert seq.next_number == 501


@pytest.mark.django_db
def test_workorder_new_duplicate_number_shows_error(api_client, job):
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=100)

    from rental_scheduler.models import Job
    other_job = Job.objects.create(
        display_name="Other Job",
        start=job.start,
        end=job.end,
    )
    WorkOrderV2.objects.create(
        job=other_job,
        number=500,
        customer_org_id=1,
        discount_type="amount",
        discount_value=Decimal("0.00"),
    )

    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}"
    resp = api_client.post(
        url,
        data={
            "number": "500",
            "notes": "",
            "customer_org_id": "1",
            "job_by_rep_id": "",
            "discount_type": "amount",
            "discount_value": "0.00",
        },
    )

    assert resp.status_code == 200
    html = resp.content.decode("utf-8")
    assert "already in use" in html


@pytest.mark.django_db
def test_workorder_edit_change_number(api_client, job):
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=100)
    wo = WorkOrderV2.objects.create(
        job=job,
        customer_org_id=1,
        discount_type="amount",
        discount_value=Decimal("0.00"),
    )
    original_number = wo.number

    url = reverse("rental_scheduler:workorder_edit", args=[wo.pk])
    resp = api_client.post(
        url,
        data={
            "number": "999",
            "notes": "",
            "customer_org_id": "1",
            "job_by_rep_id": "",
            "discount_type": "amount",
            "discount_value": "0.00",
        },
    )

    assert resp.status_code == 302
    wo.refresh_from_db()
    assert wo.number == 999
    assert wo.number != original_number


@pytest.mark.django_db
def test_workorder_edit_duplicate_number_shows_error(api_client, job):
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=100)
    wo1 = WorkOrderV2.objects.create(
        job=job,
        customer_org_id=1,
        discount_type="amount",
        discount_value=Decimal("0.00"),
    )

    from rental_scheduler.models import Job
    other_job = Job.objects.create(
        display_name="Other Job",
        start=job.start,
        end=job.end,
    )
    wo2 = WorkOrderV2.objects.create(
        job=other_job,
        customer_org_id=2,
        discount_type="amount",
        discount_value=Decimal("0.00"),
    )

    url = reverse("rental_scheduler:workorder_edit", args=[wo2.pk])
    resp = api_client.post(
        url,
        data={
            "number": str(wo1.number),
            "notes": "",
            "customer_org_id": "2",
            "job_by_rep_id": "",
            "discount_type": "amount",
            "discount_value": "0.00",
        },
    )

    assert resp.status_code == 200
    html = resp.content.decode("utf-8")
    assert "already in use" in html
    wo2.refresh_from_db()
    assert wo2.number != wo1.number


@pytest.mark.django_db
def test_workorder_new_form_shows_next_number(api_client, job):
    from rental_scheduler.models import WorkOrderNumberSequence

    WorkOrderNumberSequence.get_solo(start_number=42)

    url = reverse("rental_scheduler:workorder_new") + f"?job={job.id}"
    resp = api_client.get(url)

    assert resp.status_code == 200
    html = resp.content.decode("utf-8")
    assert 'value="42"' in html