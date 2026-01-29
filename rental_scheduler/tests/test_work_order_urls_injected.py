import re

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_work_order_and_accounting_urls_injected_into_gts_urls(api_client):
    """
    Work Order editor JS relies on these being present on every page.
    """
    url = reverse("rental_scheduler:calendar")
    resp = api_client.get(url)
    content = resp.content.decode("utf-8")

    # Work Order
    assert "GTS.urls.workOrderNewBase" in content
    assert "workorders/new" in content

    assert "GTS.urls.workOrderEditTemplate" in content
    assert "{pk}" in content

    assert "GTS.urls.workOrderPdfTemplate" in content
    assert "{pk}" in content

    # Accounting
    assert "GTS.urls.accountingCustomerSearch" in content
    assert "api/accounting/customers/search" in content

    assert "GTS.urls.accountingCustomerCreate" in content
    assert "api/accounting/customers/create" in content

    assert "GTS.urls.accountingCustomerUpdateTemplate" in content
    assert "{orgid}" in content

    assert "GTS.urls.accountingItemSearch" in content
    assert "api/accounting/items/search" in content

    # Sanity: ensure these are assigned to strings, not left blank
    match = re.search(r"GTS\.urls\.workOrderNewBase\s*=\s*['\"]([^'\"]+)['\"]", content)
    assert match and match.group(1)
