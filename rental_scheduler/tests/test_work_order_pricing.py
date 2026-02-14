"""
Unit tests for Work Order pricing / totals logic.

These are pure tests (no DB) and cover the project contracts for subtotal,
discount semantics, and total calculation.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError


def test_compute_totals_no_discount():
    from rental_scheduler.utils.work_orders import compute_work_order_totals

    subtotal, discount_amount, tax_amount, total = compute_work_order_totals(
        line_items=[
            {"qty": Decimal("2.00"), "price": Decimal("10.00")},
            {"qty": Decimal("1.00"), "price": Decimal("5.50")},
        ],
        discount_type="amount",
        discount_value=Decimal("0.00"),
    )

    assert subtotal == Decimal("25.50")
    assert discount_amount == Decimal("0.00")
    assert tax_amount == Decimal("0.00")
    assert total == Decimal("25.50")


def test_compute_totals_percent_discount():
    from rental_scheduler.utils.work_orders import compute_work_order_totals

    subtotal, discount_amount, tax_amount, total = compute_work_order_totals(
        line_items=[{"qty": Decimal("2.00"), "price": Decimal("50.00")}],
        discount_type="percent",
        discount_value=Decimal("10.0"),
    )

    assert subtotal == Decimal("100.00")
    assert discount_amount == Decimal("10.00")
    assert tax_amount == Decimal("0.00")
    assert total == Decimal("90.00")


def test_compute_totals_amount_discount():
    from rental_scheduler.utils.work_orders import compute_work_order_totals

    subtotal, discount_amount, tax_amount, total = compute_work_order_totals(
        line_items=[{"qty": Decimal("3.00"), "price": Decimal("10.00")}],
        discount_type="amount",
        discount_value=Decimal("5.00"),
    )

    assert subtotal == Decimal("30.00")
    assert discount_amount == Decimal("5.00")
    assert tax_amount == Decimal("0.00")
    assert total == Decimal("25.00")


def test_percent_discount_over_100_is_invalid():
    from rental_scheduler.utils.work_orders import compute_work_order_totals

    with pytest.raises(ValidationError):
        compute_work_order_totals(
            line_items=[{"qty": Decimal("1.00"), "price": Decimal("10.00")}],
            discount_type="percent",
            discount_value=Decimal("100.01"),
        )


def test_amount_discount_greater_than_subtotal_is_invalid():
    from rental_scheduler.utils.work_orders import compute_work_order_totals

    with pytest.raises(ValidationError):
        compute_work_order_totals(
            line_items=[{"qty": Decimal("1.00"), "price": Decimal("10.00")}],
            discount_type="amount",
            discount_value=Decimal("10.01"),
        )


def test_compute_totals_zero_price_line_item():
    from rental_scheduler.utils.work_orders import compute_work_order_totals

    subtotal, discount_amount, tax_amount, total = compute_work_order_totals(
        line_items=[
            {"qty": Decimal("1.00"), "price": Decimal("0.00")},
        ],
        discount_type="amount",
        discount_value=Decimal("0.00"),
    )

    assert subtotal == Decimal("0.00")
    assert discount_amount == Decimal("0.00")
    assert tax_amount == Decimal("0.00")
    assert total == Decimal("0.00")


def test_compute_totals_mixed_zero_and_nonzero_prices():
    from rental_scheduler.utils.work_orders import compute_work_order_totals

    subtotal, discount_amount, tax_amount, total = compute_work_order_totals(
        line_items=[
            {"qty": Decimal("1.00"), "price": Decimal("0.00")},
            {"qty": Decimal("2.00"), "price": Decimal("25.00")},
            {"qty": Decimal("3.00"), "price": Decimal("0.00")},
        ],
        discount_type="amount",
        discount_value=Decimal("0.00"),
    )

    assert subtotal == Decimal("50.00")
    assert discount_amount == Decimal("0.00")
    assert tax_amount == Decimal("0.00")
    assert total == Decimal("50.00")
