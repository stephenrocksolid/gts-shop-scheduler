import logging
from decimal import Decimal

from django.db import connections
from django.utils import timezone

from accounting_integration.models import ItmItems, ItmItemLink, ItmItemUnit, GlAcct
from accounting_integration.exceptions import InvoiceError

logger = logging.getLogger("accounting_integration")

GTS_DISCOUNT_ITEM_NUMBER = "Discount"
GTS_DISCOUNT_ITEM_DESC = "Discount"
SALES_DISCOUNT_GL_NUMBER = 4800


def _get_sales_discount_gl(using="accounting"):
    try:
        return GlAcct.objects.using(using).get(glnumber=SALES_DISCOUNT_GL_NUMBER)
    except GlAcct.DoesNotExist:
        raise InvoiceError(
            f"GL Account {SALES_DISCOUNT_GL_NUMBER} (Sales Discounts) not found "
            f"in Classic Accounting. This account is required for discount support."
        )


def _create_discount_item_raw(gl_acct, using="accounting"):
    conn = connections[using]
    now = timezone.now()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO itm_items (
                itemtypecode, itemnumber, salesdesc,
                price, cost, taxable, active, salesaccountid, createdate
            )
            VALUES (
                'DISCOUNT', %s, %s,
                0.00, 0.00, TRUE, TRUE, %s, %s
            )
            RETURNING itemid
            """,
            [
                GTS_DISCOUNT_ITEM_NUMBER,
                GTS_DISCOUNT_ITEM_DESC,
                gl_acct.gl_acct_id,
                now,
            ],
        )
        item_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO itm_item_unit (
                active, createdate, defaultpurchasing, defaultselling,
                mainunit, mathoper, quantity, sellable, unitname, itemid
            )
            VALUES (
                TRUE, %s, TRUE, TRUE,
                TRUE, 'Multiply', 1.0000, TRUE, 'Each', %s
            )
            """,
            [now, item_id],
        )

    logger.info(
        f"Created GTS Discount item in Classic Accounting "
        f"(itemid={item_id}, itemnumber={GTS_DISCOUNT_ITEM_NUMBER})"
    )
    return item_id


def _validate_discount_item(item, gl_acct):
    errors = []

    if not item.active:
        errors.append("item is inactive")

    item_type = getattr(item.itemtypecode, "itemtypecode", str(item.itemtypecode))
    if item_type != "DISCOUNT":
        errors.append(f"itemtypecode is '{item_type}', expected 'DISCOUNT'")

    if item.salesaccountid_id != gl_acct.gl_acct_id:
        errors.append(
            f"salesaccountid points to GL {item.salesaccountid_id}, "
            f"expected GL {gl_acct.gl_acct_id} ({SALES_DISCOUNT_GL_NUMBER})"
        )

    if errors:
        raise InvoiceError(
            f"GTS Discount item '{GTS_DISCOUNT_ITEM_NUMBER}' exists but has "
            f"invalid configuration: {'; '.join(errors)}. "
            f"Please correct the item in Classic Accounting."
        )


def ensure_gts_discount_item(using="accounting"):
    gl_acct = _get_sales_discount_gl(using=using)

    try:
        item = (
            ItmItems.objects.using(using)
            .select_related("itemtypecode", "salesaccountid")
            .get(itemnumber=GTS_DISCOUNT_ITEM_NUMBER)
        )
        _validate_discount_item(item, gl_acct)
        return item
    except ItmItems.DoesNotExist:
        pass

    logger.info(
        f"GTS Discount item '{GTS_DISCOUNT_ITEM_NUMBER}' not found, creating..."
    )

    _create_discount_item_raw(gl_acct, using=using)

    return (
        ItmItems.objects.using(using)
        .select_related("itemtypecode", "salesaccountid")
        .get(itemnumber=GTS_DISCOUNT_ITEM_NUMBER)
    )


def ensure_discount_item_unit(discount_item, using="accounting"):
    unit = (
        ItmItemUnit.objects.using(using)
        .filter(itemid=discount_item, mainunit=True)
        .first()
    )
    if unit:
        return unit

    unit = ItmItemUnit.objects.using(using).filter(itemid=discount_item).first()
    if unit:
        return unit

    now = timezone.now()
    unit = ItmItemUnit.objects.using(using).create(
        active=True,
        createdate=now,
        defaultpurchasing=True,
        defaultselling=True,
        mainunit=True,
        mathoper="Multiply",
        quantity=Decimal("1.0000"),
        sellable=True,
        unitname="Each",
        itemid=discount_item,
    )
    logger.info(
        f"Created ItmItemUnit (id={unit.id}) for discount item "
        f"{discount_item.itemnumber}"
    )
    return unit


def ensure_discount_tax_links(discount_item, customer_org, using="accounting"):
    from accounting_integration.services.tax_applicability import get_customer_selected_tax_items

    selected_tax_items = get_customer_selected_tax_items(customer_org, using=using)
    if not selected_tax_items:
        return

    unit = ensure_discount_item_unit(discount_item, using=using)

    existing_child_ids = set(
        ItmItemLink.objects.using(using)
        .filter(parentitemid=discount_item, linktype="TAX")
        .values_list("childitemid_id", flat=True)
    )

    now = timezone.now()
    to_create = []
    for tax_item in selected_tax_items:
        if tax_item.itemid not in existing_child_ids:
            to_create.append(
                ItmItemLink(
                    parentitemid=discount_item,
                    childitemid=tax_item,
                    linktype="TAX",
                    exempt=False,
                    createdate=now,
                    qty=0,
                    itemunitid=unit.id,
                )
            )

    if to_create:
        ItmItemLink.objects.using(using).bulk_create(to_create)
        logger.info(
            f"Created {len(to_create)} TAX link(s) for discount item "
            f"{discount_item.itemnumber}"
        )
