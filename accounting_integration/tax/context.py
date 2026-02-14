from dataclasses import dataclass
from typing import Dict, Iterable, List, Set

from accounting_integration.models import ItmItemLink, ItmItems, Org
from accounting_integration.services.tax_applicability import get_customer_selected_tax_items


@dataclass(frozen=True)
class ItemTaxLinkInfo:
    has_links: bool
    non_exempt_tax_ids: Set[int]


def load_selected_tax_items(customer_org: Org, using: str = "accounting") -> List[ItmItems]:
    return get_customer_selected_tax_items(customer_org, using=using)


def load_item_tax_link_map(
    item_ids: Iterable[int],
    selected_tax_ids: Set[int],
    *,
    using: str = "accounting",
) -> Dict[int, ItemTaxLinkInfo]:
    item_ids = set(item_ids)
    if not item_ids:
        return {}

    links = (
        ItmItemLink.objects.using(using)
        .filter(parentitemid_id__in=item_ids, linktype="TAX")
        .values_list("parentitemid_id", "childitemid_id", "exempt")
    )

    has_links_map: Dict[int, bool] = {item_id: False for item_id in item_ids}
    non_exempt_map: Dict[int, Set[int]] = {item_id: set() for item_id in item_ids}

    for parent_id, child_id, exempt in links:
        has_links_map[parent_id] = True
        if not exempt and child_id in selected_tax_ids:
            non_exempt_map[parent_id].add(child_id)

    return {
        item_id: ItemTaxLinkInfo(
            has_links=has_links_map[item_id],
            non_exempt_tax_ids=non_exempt_map[item_id],
        )
        for item_id in item_ids
    }
