from __future__ import annotations

from decimal import Decimal
from typing import List, Tuple

from accounting_integration.models import (
    IncIncomeSettings,
    IncIncomeSettingsDefTaxRegions,
    ItmItems,
    Org,
    OrgItemLink,
)


def get_customer_selected_tax_items(
    customer_org: Org, using: str = "accounting"
) -> List[ItmItems]:
    customer_links = (
        OrgItemLink.objects.using(using)
        .filter(orgid=customer_org, linktype="TAX", exempt=False)
        .select_related("itemid", "itemid__itemtypecode")
        .order_by("id")
    )

    if customer_links.exists():
        return [
            link.itemid
            for link in customer_links
            if link.itemid.itemtypecode.itemtypecode == "SALESTAX"
            and link.itemid.active
        ]

    try:
        inc_settings = IncIncomeSettings.objects.using(using).first()
        if not inc_settings:
            return []

        default_tax_regions = (
            IncIncomeSettingsDefTaxRegions.objects.using(using)
            .filter(inc_settings=inc_settings)
            .select_related("tax_item", "tax_item__itemtypecode")
            .order_by("order_seq")
        )

        return [
            region.tax_item
            for region in default_tax_regions
            if region.tax_item.itemtypecode.itemtypecode == "SALESTAX"
            and region.tax_item.active
        ]
    except Exception:
        return []


def get_effective_tax_rate(
    customer_org_id: int, using: str = "accounting"
) -> Tuple[Decimal, bool]:
    try:
        org = Org.objects.using(using).filter(org_id=customer_org_id).first()
    except Exception:
        return Decimal("0.00"), True

    if not org:
        return Decimal("0.00"), True

    if org.taxable is False:
        return Decimal("0.00"), True

    tax_items = get_customer_selected_tax_items(org, using=using)
    if not tax_items:
        return Decimal("0.00"), True

    rate = sum(item.price for item in tax_items)
    rate = Decimal(str(rate)).quantize(Decimal("0.0001"))
    return rate, False
