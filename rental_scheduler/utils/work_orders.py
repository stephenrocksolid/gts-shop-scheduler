"""
Work Order pricing utilities.

Pure helpers used by the Work Order domain model + views.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Tuple

from django.core.exceptions import ValidationError


MONEY_QUANT = Decimal("0.01")


def quantize_money(value: Decimal | int | float | str | None) -> Decimal:
    if value is None:
        return Decimal("0.00")
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _get_value(line_item, key: str):
    if isinstance(line_item, dict):
        return line_item.get(key)
    return getattr(line_item, key)


def compute_work_order_totals(
    *,
    line_items: Iterable,
    discount_type: str,
    discount_value: Decimal | int | float | str | None,
    tax_rate: Decimal | int | float | str | None = None,
    clamp: bool = False,
) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
    """
    Compute (subtotal, discount_amount, tax_amount, total).

    Contracts:
    - subtotal = sum(qty * price)
    - discount_type:
      - "percent": discount_value must be 0–100
      - "amount": discount_value must be 0–subtotal
    - tax_amount = (subtotal - discount_amount) * tax_rate / 100
    - total = subtotal - discount_amount + tax_amount

    When *clamp* is True, out-of-range discount values are silently clamped
    instead of raising ValidationError.  Use this for real-time preview
    endpoints where the form may be in an intermediate editing state.
    """

    discount_value_dec = quantize_money(discount_value)

    tax_rate_dec = Decimal("0.00")
    if tax_rate is not None:
        if not isinstance(tax_rate, Decimal):
            tax_rate_dec = Decimal(str(tax_rate))
        else:
            tax_rate_dec = tax_rate
        if tax_rate_dec < 0:
            tax_rate_dec = Decimal("0.00")

    subtotal = Decimal("0.00")
    for li in line_items or []:
        qty = _get_value(li, "qty")
        price = _get_value(li, "price")
        qty_dec = Decimal(str(qty)) if not isinstance(qty, Decimal) else qty
        price_dec = Decimal(str(price)) if not isinstance(price, Decimal) else price
        subtotal += quantize_money(qty_dec * price_dec)
    subtotal = quantize_money(subtotal)

    if discount_type not in ("amount", "percent"):
        raise ValidationError({"discount_type": "Invalid discount type."})

    if discount_value_dec < 0:
        if clamp:
            discount_value_dec = Decimal("0.00")
        else:
            raise ValidationError({"discount_value": "Discount cannot be negative."})

    if discount_type == "percent":
        if discount_value_dec > Decimal("100.00"):
            if clamp:
                discount_value_dec = Decimal("100.00")
            else:
                raise ValidationError({"discount_value": "Percent discount cannot exceed 100%."})
        discount_amount = quantize_money(subtotal * (discount_value_dec / Decimal("100.00")))
    else:
        if discount_value_dec > subtotal:
            if clamp:
                discount_value_dec = subtotal
            else:
                raise ValidationError({"discount_value": "Discount cannot exceed subtotal."})
        discount_amount = quantize_money(discount_value_dec)

    taxable_subtotal = subtotal - discount_amount
    tax_amount = quantize_money(taxable_subtotal * tax_rate_dec / Decimal("100"))

    total = quantize_money(taxable_subtotal + tax_amount)
    return subtotal, discount_amount, tax_amount, total

