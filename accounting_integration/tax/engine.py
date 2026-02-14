from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Iterable, List, Mapping, Sequence

from .context import ItemTaxLinkInfo


@dataclass(frozen=True)
class TaxPlan:
    selected_tax_items: Sequence[object]
    applicable_tax_item_ids_by_entry_id: Dict[int, List[int]]
    taxable_base_by_tax_item_id: Dict[int, Decimal]
    tax_amount_by_tax_item_id: Dict[int, Decimal]


def compute_tax_plan(
    entries: Iterable[object],
    selected_tax_items: Sequence[object],
    item_tax_link_map: Mapping[int, ItemTaxLinkInfo],
    *,
    fallback_apply_none: bool = True,
    rounding: Decimal = Decimal("0.01"),
) -> TaxPlan:
    selected_tax_ids = [tax.itemid for tax in selected_tax_items]
    applicable_by_entry_id: Dict[int, List[int]] = {}

    taxable_base_by_tax_id: Dict[int, Decimal] = {
        tax_id: Decimal("0.00") for tax_id in selected_tax_ids
    }

    for entry in entries:
        item = getattr(entry, "itemid", None)
        entry_id = getattr(entry, "entryid", None)
        if not item or entry_id is None:
            continue

        item_id = item.itemid
        link_info = item_tax_link_map.get(item_id)
        if not link_info or not link_info.has_links:
            applicable_ids = [] if fallback_apply_none else list(selected_tax_ids)
        else:
            applicable_ids = [
                tax_id for tax_id in selected_tax_ids if tax_id in link_info.non_exempt_tax_ids
            ]

        applicable_by_entry_id[entry_id] = applicable_ids

        entry_total = getattr(entry, "entrytotal", Decimal("0.00"))
        for tax_id in applicable_ids:
            taxable_base_by_tax_id[tax_id] += entry_total

    tax_amount_by_tax_id: Dict[int, Decimal] = {}
    for tax in selected_tax_items:
        base = taxable_base_by_tax_id.get(tax.itemid, Decimal("0.00"))
        if base <= 0:
            tax_amount_by_tax_id[tax.itemid] = Decimal("0.00")
            continue
        tax_rate = tax.price
        tax_amount_by_tax_id[tax.itemid] = (base * tax_rate / Decimal("100")).quantize(rounding)

    return TaxPlan(
        selected_tax_items=selected_tax_items,
        applicable_tax_item_ids_by_entry_id=applicable_by_entry_id,
        taxable_base_by_tax_item_id=taxable_base_by_tax_id,
        tax_amount_by_tax_item_id=tax_amount_by_tax_id,
    )
