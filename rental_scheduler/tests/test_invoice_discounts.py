import pytest
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from accounting_integration.exceptions import InvoiceError
from accounting_integration.services.discount_item import (
    _validate_discount_item,
    GTS_DISCOUNT_ITEM_NUMBER,
    SALES_DISCOUNT_GL_NUMBER,
)
from accounting_integration.tax.engine import compute_tax_plan, TaxPlan


def _make_gl(gl_acct_id=99):
    return SimpleNamespace(gl_acct_id=gl_acct_id, glnumber=SALES_DISCOUNT_GL_NUMBER)


def _make_discount_item(active=True, itemtypecode="DISCOUNT", gl_id=99):
    return SimpleNamespace(
        itemnumber=GTS_DISCOUNT_ITEM_NUMBER,
        active=active,
        itemtypecode=SimpleNamespace(itemtypecode=itemtypecode),
        salesaccountid_id=gl_id,
    )


class TestValidateDiscountItem:
    def test_valid_item_passes(self):
        gl = _make_gl(gl_acct_id=99)
        item = _make_discount_item(gl_id=99)
        _validate_discount_item(item, gl)

    def test_inactive_item_raises(self):
        gl = _make_gl()
        item = _make_discount_item(active=False)
        with pytest.raises(InvoiceError, match="inactive"):
            _validate_discount_item(item, gl)

    def test_wrong_itemtypecode_raises(self):
        gl = _make_gl()
        item = _make_discount_item(itemtypecode="SERVICE")
        with pytest.raises(InvoiceError, match="SERVICE"):
            _validate_discount_item(item, gl)

    def test_wrong_gl_raises(self):
        gl = _make_gl(gl_acct_id=99)
        item = _make_discount_item(gl_id=777)
        with pytest.raises(InvoiceError, match="777"):
            _validate_discount_item(item, gl)


def _make_tax_item(itemid, price):
    return SimpleNamespace(itemid=itemid, price=price)


def _make_entry(entryid, itemid_val, entrytotal, taxable=True):
    item = SimpleNamespace(itemid=itemid_val, taxable=taxable)
    return SimpleNamespace(
        entryid=entryid,
        itemid=item,
        entrytotal=entrytotal,
    )


def _make_link_info(non_exempt_tax_ids):
    from accounting_integration.tax.context import ItemTaxLinkInfo
    return ItemTaxLinkInfo(
        has_links=True,
        non_exempt_tax_ids=frozenset(non_exempt_tax_ids),
    )


class TestTaxEngineWithDiscount:
    def test_no_discount_uses_full_entrytotal(self):
        tax = _make_tax_item(itemid=500, price=Decimal("10.00"))
        entry = _make_entry(entryid=1, itemid_val=100, entrytotal=Decimal("200.00"))
        link_map = {100: _make_link_info({500})}

        plan = compute_tax_plan([entry], [tax], link_map)

        assert plan.taxable_base_by_tax_item_id[500] == Decimal("200.00")
        assert plan.tax_amount_by_tax_item_id[500] == Decimal("20.00")

    def test_discount_entry_reduces_taxable_base(self):
        tax = _make_tax_item(itemid=500, price=Decimal("10.00"))
        product = _make_entry(entryid=1, itemid_val=100, entrytotal=Decimal("200.00"))
        discount = _make_entry(entryid=2, itemid_val=900, entrytotal=Decimal("-50.00"))
        link_map = {
            100: _make_link_info({500}),
            900: _make_link_info({500}),
        }

        plan = compute_tax_plan([product, discount], [tax], link_map)

        assert plan.taxable_base_by_tax_item_id[500] == Decimal("150.00")
        assert plan.tax_amount_by_tax_item_id[500] == Decimal("15.00")

    def test_multiple_entries_with_discount_entry(self):
        tax = _make_tax_item(itemid=500, price=Decimal("7.00"))
        e1 = _make_entry(entryid=1, itemid_val=100, entrytotal=Decimal("300.00"))
        e2 = _make_entry(entryid=2, itemid_val=101, entrytotal=Decimal("200.00"))
        disc = _make_entry(entryid=3, itemid_val=900, entrytotal=Decimal("-50.00"))
        link_map = {
            100: _make_link_info({500}),
            101: _make_link_info({500}),
            900: _make_link_info({500}),
        }

        plan = compute_tax_plan([e1, e2, disc], [tax], link_map)

        assert plan.taxable_base_by_tax_item_id[500] == Decimal("450.00")
        assert plan.tax_amount_by_tax_item_id[500] == Decimal("31.50")

    def test_discount_without_tax_links_excluded_from_base(self):
        tax = _make_tax_item(itemid=500, price=Decimal("10.00"))
        product = _make_entry(entryid=1, itemid_val=100, entrytotal=Decimal("100.00"))
        discount = _make_entry(entryid=2, itemid_val=900, entrytotal=Decimal("-10.00"))
        link_map = {
            100: _make_link_info({500}),
        }

        plan = compute_tax_plan([product, discount], [tax], link_map)

        assert plan.taxable_base_by_tax_item_id[500] == Decimal("100.00")


class TestApplyDiscountToEntriesEdgeCases:
    def test_zero_discount_returns_none(self):
        from accounting_integration.services.document_builders import apply_discount_to_entries

        result = apply_discount_to_entries(
            trans=MagicMock(),
            product_entries=[],
            discount_amount=Decimal("0.00"),
            order_seq=0,
            discount_item=MagicMock(),
        )
        assert result is None

    def test_negative_discount_returns_none(self):
        from accounting_integration.services.document_builders import apply_discount_to_entries

        result = apply_discount_to_entries(
            trans=MagicMock(),
            product_entries=[],
            discount_amount=Decimal("-5.00"),
            order_seq=0,
            discount_item=MagicMock(),
        )
        assert result is None

    def test_zero_subtotal_returns_none(self):
        from accounting_integration.services.document_builders import apply_discount_to_entries

        entry = MagicMock()
        entry.entrytotal = Decimal("0.00")

        result = apply_discount_to_entries(
            trans=MagicMock(),
            product_entries=[entry],
            discount_amount=Decimal("10.00"),
            order_seq=0,
            discount_item=MagicMock(),
        )
        assert result is None
