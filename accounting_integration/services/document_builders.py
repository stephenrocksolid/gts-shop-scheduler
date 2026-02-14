import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from django.db.models import Sum

from accounting_integration.models import (
    AcctTrans, AcctEntry, ItmItems, ItmItemUnit,
    GlAcct, Org, OrgAddress,
)
from accounting_integration.services.transaction_builder import (
    create_item_entry,
    create_gl_entry,
)
from accounting_integration.exceptions import InvoiceError

logger = logging.getLogger('accounting_integration')

MONEY_QUANT = Decimal("0.01")


def build_billtotx(org: Org) -> str:
    lines = []

    if org.orgname:
        lines.append(org.orgname.strip())

    try:
        addr = (
            OrgAddress.objects.using('accounting')
            .filter(orgid=org, addresstype='BILLTO')
            .order_by('-is_default', '-gen_addr_id')
            .first()
        )
    except Exception:
        addr = None

    if addr:
        if addr.streetone:
            lines.append(addr.streetone.strip())
        if addr.streettwo:
            lines.append(addr.streettwo.strip())

        city_state_zip_parts = []
        if addr.txtcity:
            city_state_zip_parts.append(addr.txtcity.strip())
        if addr.txtstate:
            city_state_zip_parts.append(addr.txtstate.strip().upper())
        if addr.txtzip:
            city_state_zip_parts.append(addr.txtzip.strip())

        if city_state_zip_parts:
            lines.append(' '.join(city_state_zip_parts))

    return '\n'.join(lines)


def create_work_order_line_items(trans: AcctTrans, work_order) -> list:
    from rental_scheduler.models import WorkOrderLineV2

    wo_lines = list(
        WorkOrderLineV2.objects
        .filter(work_order=work_order)
        .order_by('created_at')
    )

    entries = []
    for seq, wo_line in enumerate(wo_lines):
        try:
            item = ItmItems.objects.using('accounting').select_related(
                'itemtypecode', 'salesaccountid'
            ).get(itemid=wo_line.itemid)
        except ItmItems.DoesNotExist:
            raise InvoiceError(
                f"Item {wo_line.itemid} not found in Classic Accounting"
            )

        try:
            item_unit = ItmItemUnit.objects.using('accounting').get(
                itemid=item,
                mainunit=True,
            )
        except ItmItemUnit.DoesNotExist:
            try:
                item_unit = ItmItemUnit.objects.using('accounting').filter(
                    itemid=item,
                    defaultselling=True,
                ).first()
            except Exception:
                item_unit = None

            if not item_unit:
                raise InvoiceError(
                    f"No unit found for item {item.itemnumber} in Classic Accounting"
                )

        entry = create_item_entry(
            trans=trans,
            item=item,
            item_unit=item_unit,
            quantity=wo_line.qty,
            unit_price=wo_line.price,
            memo=wo_line.description_snapshot or item.salesdesc or '',
            order_seq=seq,
        )
        entries.append(entry)

    return entries


def apply_discount_to_entries(
    trans: AcctTrans,
    product_entries: List[AcctEntry],
    discount_amount: Decimal,
    order_seq: int,
    discount_item: ItmItems,
    discount_unit: ItmItemUnit = None,
) -> Optional[AcctEntry]:
    if not discount_amount or discount_amount <= 0:
        return None

    subtotal = sum(e.entrytotal for e in product_entries)
    if subtotal <= 0:
        return None

    discount_amount = discount_amount.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)

    neg_amount = -discount_amount
    discount_entry = create_item_entry(
        trans=trans,
        item=discount_item,
        item_unit=discount_unit,
        quantity=Decimal("1.0"),
        unit_price=neg_amount,
        memo=GTS_DISCOUNT_MEMO,
        order_seq=order_seq,
        entrytotal=neg_amount,
    )

    logger.info(f"Created discount ITEMENTRY {discount_entry.entryid}: ${neg_amount}")
    return discount_entry


GTS_DISCOUNT_MEMO = "Discount"


def create_gl_entries(invoice: AcctTrans, line_items: list) -> None:
    ar_account = GlAcct.objects.using('accounting').get(glnumber=1200)

    create_gl_entry(
        trans=invoice,
        gl_acct=ar_account,
        amount=invoice.transtotal,
        memo=f"Invoice #{invoice.referencenumber}",
        order_seq=-1,
    )

    logger.info(f"Created AR GLENTRY: +${invoice.transtotal}")

    for line_item in line_items:
        item = line_item.itemid
        if not item:
            raise InvoiceError(
                f"Line item entry {line_item.entryid} has no item reference"
            )

        sales_gl = item.salesaccountid
        if not sales_gl:
            raise InvoiceError(
                f"Item {item.itemnumber} missing Sales GL account"
            )

        create_gl_entry(
            trans=invoice,
            gl_acct=sales_gl,
            amount=-line_item.entrytotal,
            memo=line_item.memotx or '',
            order_seq=line_item.orderseq,
        )

    gl_sum = AcctEntry.objects.using('accounting').filter(
        transid=invoice,
        entrytypecode='GLENTRY'
    ).aggregate(
        total=Sum('entrytotal')
    )['total']

    if gl_sum != Decimal('0.00'):
        raise InvoiceError(
            f"GLENTRY sum validation failed: {gl_sum} != 0.00 "
            f"(AR: +${invoice.transtotal}, Sales GL: -${sum(li.entrytotal for li in line_items)})"
        )

    logger.info("GL entries validated: sum = 0.00")
