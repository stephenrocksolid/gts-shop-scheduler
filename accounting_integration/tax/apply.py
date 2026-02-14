from typing import Iterable, List, Tuple

from accounting_integration.models import AcctEntry, AcctTrans
from accounting_integration.tax.context import load_item_tax_link_map, load_selected_tax_items
from accounting_integration.tax.engine import TaxPlan, compute_tax_plan
from accounting_integration.tax.writer import (
    create_salestax_entries,
    replace_entry_applic_taxes,
    replace_trans_tax_regions,
)


def apply_taxes_to_document(
    trans: AcctTrans,
    customer_org,
    product_entries: Iterable[AcctEntry],
    *,
    order_seq_start: int,
    using: str = "accounting",
) -> Tuple[List[AcctEntry], TaxPlan]:
    product_entries = list(product_entries)
    selected_tax_items = load_selected_tax_items(customer_org, using=using)
    selected_tax_ids = {tax.itemid for tax in selected_tax_items}
    item_ids = {entry.itemid_id for entry in product_entries if entry.itemid_id}
    item_tax_link_map = load_item_tax_link_map(item_ids, selected_tax_ids, using=using)

    taxable_entries = [
        entry for entry in product_entries
        if entry.itemid and entry.itemid.taxable
    ]

    plan = compute_tax_plan(
        taxable_entries,
        selected_tax_items,
        item_tax_link_map,
        fallback_apply_none=True,
    )

    replace_trans_tax_regions(trans, selected_tax_items, using=using)

    applicable_by_entry_id = {
        entry.entryid: plan.applicable_tax_item_ids_by_entry_id.get(entry.entryid, [])
        for entry in product_entries
    }
    replace_entry_applic_taxes(product_entries, applicable_by_entry_id, using=using)

    tax_entries = create_salestax_entries(
        trans,
        plan.tax_amount_by_tax_item_id,
        selected_tax_items,
        order_seq_start,
        using=using,
    )

    return tax_entries, plan
