from decimal import Decimal
from typing import Dict, Iterable, List, Sequence

from accounting_integration.models import (
    AcctEntry,
    AcctEntryApplicTaxes,
    AcctTrans,
    AcctTransTaxRegions,
    ItmItemUnit,
)
from accounting_integration.services.transaction_builder import create_item_entry


def replace_trans_tax_regions(
    trans: AcctTrans,
    selected_tax_items: Sequence[object],
    *,
    using: str = "accounting",
) -> None:
    AcctTransTaxRegions.objects.using(using).filter(trans=trans).delete()

    rows = [
        AcctTransTaxRegions(trans=trans, tax_item=tax_item, order_seq=idx)
        for idx, tax_item in enumerate(selected_tax_items)
    ]
    if rows:
        AcctTransTaxRegions.objects.using(using).bulk_create(rows)


def replace_entry_applic_taxes(
    entries: Iterable[AcctEntry],
    applicable_tax_item_ids_by_entry_id: Dict[int, List[int]],
    *,
    using: str = "accounting",
) -> None:
    entry_ids = [entry.entryid for entry in entries]
    if not entry_ids:
        return

    AcctEntryApplicTaxes.objects.using(using).filter(entry_id__in=entry_ids).delete()

    rows: List[AcctEntryApplicTaxes] = []
    for entry in entries:
        applicable_ids = applicable_tax_item_ids_by_entry_id.get(entry.entryid, [])
        for idx, tax_item_id in enumerate(applicable_ids):
            rows.append(
                AcctEntryApplicTaxes(
                    entry=entry,
                    tax_item_id=tax_item_id,
                    order_seq=idx,
                )
            )

    if rows:
        AcctEntryApplicTaxes.objects.using(using).bulk_create(rows)


def create_salestax_entries(
    trans: AcctTrans,
    tax_amount_by_tax_item_id: Dict[int, Decimal],
    selected_tax_items: Sequence[object],
    starting_order_seq: int,
    *,
    using: str = "accounting",
) -> List[AcctEntry]:
    entries: List[AcctEntry] = []
    current_seq = starting_order_seq

    for tax_item in selected_tax_items:
        tax_amount = tax_amount_by_tax_item_id.get(tax_item.itemid, Decimal("0.00"))
        if tax_amount <= 0:
            continue

        tax_unit = ItmItemUnit.objects.using(using).get(
            itemid=tax_item,
            mainunit=True,
        )
        tax_rate = tax_item.price

        tax_entry = create_item_entry(
            trans=trans,
            item=tax_item,
            item_unit=tax_unit,
            quantity=Decimal("1.0"),
            unit_price=tax_rate,
            memo=f"{tax_item.itemname}",
            order_seq=current_seq,
            entrytotal=tax_amount,
        )
        entries.append(tax_entry)
        current_seq += 1

    return entries
