import json
from decimal import Decimal

import pytest
from django.db import connections
from django.urls import reverse
from django.utils import timezone


@pytest.fixture
def classic_accounting_db(settings, monkeypatch, tmp_path):
    from rental_scheduler import views as views_module
    from accounting_integration.models import Org, OrgAddress

    db_path = tmp_path / "accounting.sqlite3"
    settings.DATABASES["accounting"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(db_path),
    }
    connections.databases["accounting"] = settings.DATABASES["accounting"]
    connections["accounting"].close()
    monkeypatch.setattr(views_module, "_accounting_is_configured", lambda: True)

    conn = connections["accounting"]
    with conn.schema_editor() as schema:
        schema.create_model(Org)
        schema.create_model(OrgAddress)

    yield conn

    with conn.schema_editor() as schema:
        schema.delete_model(OrgAddress)
        schema.delete_model(Org)


def _seed_customer(*, name, phone, address_line1, city, state, zip_code):
    from accounting_integration.models import Org, OrgAddress

    now = timezone.now()
    org = Org.objects.using("accounting").create(
        orgdiscriminator="CUST",
        orgname=name,
        org_name_extension="",
        active=True,
        autoactive=False,
        balance=Decimal("0.00"),
        createdate=now,
        phone1=phone,
        contact1="",
        email="",
        fax1="",
        is_cash_customer=False,
        taxable=True,
        is_no_charge_sales=False,
        notes=None,
        alertnotes=None,
        exported=None,
        fiscalmonth=None,
        taxmonth=None,
        logo=None,
        companyname="",
        creditlimit=Decimal("0.0000"),
        tax_exempt_expiration_date=None,
        tax_exempt_number="",
        eligible1099=False,
        taxidno=None,
        lastfcdate=None,
    )

    OrgAddress.objects.using("accounting").create(
        addresstype="BILLTO",
        active=True,
        addrname=None,
        streetone=address_line1,
        streettwo="",
        txtcity=city,
        txtstate=state,
        txtzip=zip_code,
        txtcountry=None,
        createdate=now,
        moddate=None,
        is_default=True,
        orgid=org,
    )

    return org


@pytest.mark.django_db(databases=["default", "accounting"])
def test_accounting_customers_create_blocks_possible_duplicates(api_client, classic_accounting_db):
    _seed_customer(
        name="Acme Transport",
        phone="615-555-1234",
        address_line1="123 Main St",
        city="Nashville",
        state="TN",
        zip_code="37201",
    )

    url = reverse("rental_scheduler:accounting_customers_create")
    resp = api_client.post(
        url,
        data=json.dumps(
            {
                "name": "Acme Transportation",
                "phone": "(615) 555-1234",
                "address_line1": "123 Main St",
                "city": "Nashville",
                "state": "TN",
                "zip": "37201",
            }
        ),
        content_type="application/json",
    )

    assert resp.status_code == 409
    payload = resp.json()
    assert payload.get("duplicates")
    match = payload["duplicates"][0]
    assert "org_id" in match
    assert "match_reasons" in match
    assert "phone" in match["match_reasons"] or "address" in match["match_reasons"]


@pytest.mark.django_db(databases=["default", "accounting"])
def test_accounting_customers_create_allows_override(api_client, classic_accounting_db):
    _seed_customer(
        name="Acme Transport",
        phone="615-555-1234",
        address_line1="123 Main St",
        city="Nashville",
        state="TN",
        zip_code="37201",
    )

    url = reverse("rental_scheduler:accounting_customers_create")
    resp = api_client.post(
        url,
        data=json.dumps(
            {
                "name": "Acme Transport",
                "phone": "615-555-1234",
                "address_line1": "123 Main St",
                "city": "Nashville",
                "state": "TN",
                "zip": "37201",
                "allow_duplicate": True,
            }
        ),
        content_type="application/json",
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data.get("org_id")
