import logging
from typing import Dict, List, Optional, Sequence, Type

from accounting_integration.models import AcctEntry, AcctEntryApplicTaxes, AcctTrans, AcctTransTaxRegions
from accounting_integration.tax.context import load_item_tax_link_map, load_selected_tax_items
from accounting_integration.tax.engine import TaxPlan, compute_tax_plan

logger = logging.getLogger("accounting_integration")


def build_expected_tax_plan(
    entries: Sequence[AcctEntry],
    customer_org,
    *,
    using: str = "accounting",
) -> TaxPlan:
    selected_tax_items = load_selected_tax_items(customer_org, using=using)
    selected_tax_ids = {tax.itemid for tax in selected_tax_items}
    item_ids = {entry.itemid_id for entry in entries if entry.itemid_id}
    item_tax_link_map = load_item_tax_link_map(item_ids, selected_tax_ids, using=using)

    return compute_tax_plan(
        entries,
        selected_tax_items,
        item_tax_link_map,
        fallback_apply_none=True,
    )


def diff_tax_applicability(
    trans: AcctTrans,
    expected_plan: TaxPlan,
    *,
    using: str = "accounting",
) -> Dict[str, object]:
    expected_region_ids = [tax.itemid for tax in expected_plan.selected_tax_items]
    actual_region_ids = list(
        AcctTransTaxRegions.objects.using(using)
        .filter(trans=trans)
        .order_by("order_seq")
        .values_list("tax_item_id", flat=True)
    )

    region_mismatch = None
    if expected_region_ids != actual_region_ids:
        region_mismatch = {
            "expected": expected_region_ids,
            "actual": actual_region_ids,
        }

    actual_applic_rows = list(
        AcctEntryApplicTaxes.objects.using(using)
        .filter(entry__transid=trans)
        .order_by("entry_id", "order_seq")
        .values_list("entry_id", "tax_item_id")
    )
    actual_by_entry: Dict[int, List[int]] = {}
    for entry_id, tax_item_id in actual_applic_rows:
        actual_by_entry.setdefault(entry_id, []).append(tax_item_id)

    expected_by_entry = expected_plan.applicable_tax_item_ids_by_entry_id
    entry_diffs: Dict[int, Dict[str, List[int]]] = {}

    for entry_id, expected_ids in expected_by_entry.items():
        actual_ids = actual_by_entry.get(entry_id, [])
        if expected_ids != actual_ids:
            entry_diffs[entry_id] = {
                "expected": expected_ids,
                "actual": actual_ids,
            }

    unexpected_entry_ids = [
        entry_id for entry_id in actual_by_entry.keys()
        if entry_id not in expected_by_entry
    ]

    salestax_entry_ids = list(
        AcctEntry.objects.using(using)
        .filter(
            transid=trans,
            entrytypecode="ITEMENTRY",
            itemid__itemtypecode__itemtypecode="SALESTAX",
        )
        .values_list("entryid", flat=True)
    )
    salestax_applic = list(
        AcctEntryApplicTaxes.objects.using(using)
        .filter(entry_id__in=salestax_entry_ids)
        .values_list("entry_id", "tax_item_id")
    )

    has_differences = bool(
        region_mismatch
        or entry_diffs
        or unexpected_entry_ids
        or salestax_applic
    )

    return {
        "has_differences": has_differences,
        "region_mismatch": region_mismatch,
        "entry_diffs": entry_diffs,
        "unexpected_entry_ids": unexpected_entry_ids,
        "salestax_applic": salestax_applic,
    }


def assert_tax_integrity(
    trans: AcctTrans,
    expected_plan: TaxPlan,
    *,
    error_cls: Optional[Type[Exception]] = None,
    using: str = "accounting",
) -> None:
    diff = diff_tax_applicability(trans, expected_plan, using=using)
    if not diff["has_differences"]:
        logger.debug(f"Tax integrity check passed for document {trans.transid}")
        return

    error_cls = error_cls or RuntimeError
    message_parts = [f"Tax integrity check failed for document {trans.transid}."]
    if diff["region_mismatch"]:
        message_parts.append(
            f"Tax regions mismatch expected={diff['region_mismatch']['expected']} "
            f"actual={diff['region_mismatch']['actual']}"
        )
    if diff["entry_diffs"]:
        message_parts.append(
            f"Applicability mismatches for entries: {sorted(diff['entry_diffs'].keys())}"
        )
    if diff["unexpected_entry_ids"]:
        message_parts.append(
            f"Unexpected applicability entries: {sorted(diff['unexpected_entry_ids'])}"
        )
    if diff["salestax_applic"]:
        message_parts.append(
            f"SALESTAX entries have applicability rows: {diff['salestax_applic']}"
        )

    message = " ".join(message_parts)
    logger.error(message)
    raise error_cls(message)
