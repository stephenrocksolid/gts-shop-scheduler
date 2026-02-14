import re

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_workorder_pdf_returns_pdf_response(api_client, job):
    from rental_scheduler.models import WorkOrderLineV2, WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=900)
    wo = WorkOrderV2.objects.create(job=job)
    WorkOrderLineV2.objects.create(work_order=wo, itemid=1, qty=1, price=10)

    url = reverse("rental_scheduler:workorder_pdf", args=[wo.pk])
    resp = api_client.get(url)

    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")
    assert len(resp.content) > 100


@pytest.mark.django_db
def test_workorder_pdf_contains_work_order_number_in_html(api_client, job):
    """
    WeasyPrint compresses content streams, so checking raw PDF bytes for a
    specific string is unreliable. Instead, validate the HTML template renders
    the work order number before conversion.
    """
    from django.template.loader import render_to_string
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=901)
    wo = WorkOrderV2.objects.create(job=job)

    html = render_to_string(
        "rental_scheduler/workorders_v2/workorder_pdf.html",
        {
            "work_order": wo,
            "lines": [],
            "customer_name": "",
            "customer_phone": "",
            "customer_contact": "",
            "customer_email": "",
        },
    )

    assert "Work Order" in html
    assert "901" in html
