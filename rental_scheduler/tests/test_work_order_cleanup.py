import pytest
from django.urls import NoReverseMatch, reverse


def _assert_no_reverse(name: str, args=None):
    with pytest.raises(NoReverseMatch):
        reverse(name, args=args or [])


@pytest.mark.django_db
def test_legacy_job_print_urls_removed():
    _assert_no_reverse("rental_scheduler:job_print_wo", args=[1])
    _assert_no_reverse("rental_scheduler:job_print_wo_customer", args=[1])


@pytest.mark.django_db
def test_legacy_workorder_crud_urls_removed():
    _assert_no_reverse("rental_scheduler:workorder_list")
    _assert_no_reverse("rental_scheduler:workorder_create")
    _assert_no_reverse("rental_scheduler:workorder_detail", args=[1])
    _assert_no_reverse("rental_scheduler:workorder_update", args=[1])
    _assert_no_reverse("rental_scheduler:workorder_delete", args=[1])
    _assert_no_reverse("rental_scheduler:workorder_print", args=[1])
    _assert_no_reverse("rental_scheduler:workorder_customer_print", args=[1])
    _assert_no_reverse("rental_scheduler:workorder_add_line_api", args=[1])


@pytest.mark.django_db
def test_legacy_job_print_urls_not_in_gts_urls(api_client):
    url = reverse("rental_scheduler:calendar")
    resp = api_client.get(url)
    content = resp.content.decode("utf-8")

    assert "GTS.urls.jobPrintWoTemplate" not in content
    assert "GTS.urls.jobPrintWoCustomerTemplate" not in content
    assert "GTS.urls.jobPrintInvoiceTemplate" in content
