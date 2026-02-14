import logging
from decimal import Decimal
from typing import Optional
from django.db import transaction

from accounting_integration.models import (
    AcctTrans, AcctEntry, AcctEntryApplicTaxes, AcctTransTaxRegions, AcctTerms, Org,
    AcctSalesRep,
)
from accounting_integration.services.document_number import allocate_next_doc_number
from accounting_integration.services.transaction_builder import create_acct_trans
from accounting_integration.services.document_builders import (
    build_billtotx,
    create_work_order_line_items,
    apply_discount_to_entries,
    create_gl_entries,
)
from accounting_integration.services.discount_item import (
    ensure_gts_discount_item,
    ensure_discount_item_unit,
    ensure_discount_tax_links,
)
from accounting_integration.exceptions import InvoiceError
from accounting_integration.tax.apply import apply_taxes_to_document
from accounting_integration.tax.integrity import (
    assert_tax_integrity,
    build_expected_tax_plan,
)

logger = logging.getLogger('accounting_integration')


def _build_invoice_notes(work_order) -> str:
    parts = []
    if work_order.trailer_make_model:
        parts.append(f"Make & Model: {work_order.trailer_make_model}")
    if work_order.trailer_color:
        parts.append(f"Color: {work_order.trailer_color}")
    if work_order.trailer_serial:
        parts.append(f"Serial No.: {work_order.trailer_serial}")
    return "\n".join(parts)


def _validate_tax_applicability(invoice: AcctTrans) -> None:
    taxable_lines = list(
        AcctEntry.objects.using("accounting")
        .filter(
            transid=invoice,
            entrytypecode="ITEMENTRY",
            itemid__taxable=True,
        )
        .exclude(itemid__itemtypecode__itemtypecode="SALESTAX")
        .select_related("itemid")
    )

    expected_plan = build_expected_tax_plan(
        taxable_lines,
        invoice.orgid,
        using="accounting",
    )
    assert_tax_integrity(
        invoice,
        expected_plan,
        error_cls=InvoiceError,
        using="accounting",
    )


def create_invoice_from_work_order(work_order, strict: bool = False) -> Optional[AcctTrans]:
    try:
        logger.info(f"Creating invoice for work order {work_order.pk} (WO #{work_order.number})")

        customer_org = Org.objects.using('accounting').get(org_id=work_order.customer_org_id)
        logger.info(f"Customer: {customer_org.orgname}")

        with transaction.atomic(using='accounting'):
            try:
                due_on_receipt_terms = AcctTerms.objects.using('accounting').get(terms_id=102)
            except AcctTerms.DoesNotExist:
                logger.warning("Due on Receipt terms (ID 102) not found, using None")
                due_on_receipt_terms = None

            reference_number = allocate_next_doc_number('INVOICE')

            wo_date = work_order.date
            if not wo_date:
                from django.utils import timezone
                wo_date = timezone.now().date()

            sales_rep = None
            if getattr(work_order, 'job_by_rep_id', None):
                try:
                    sales_rep = AcctSalesRep.objects.using('accounting').get(pk=work_order.job_by_rep_id)
                except AcctSalesRep.DoesNotExist:
                    logger.warning(f"Sales rep {work_order.job_by_rep_id} not found, skipping")

            invoice_kwargs = dict(
                trans_type_code='INVOICE',
                org=customer_org,
                trans_date=wo_date,
                reference_number=reference_number,
                trans_total=work_order.subtotal if work_order.subtotal is not None else Decimal('0.00'),
                status_code='OPEN',
                terms_id=due_on_receipt_terms,
                bill_to_tx=build_billtotx(customer_org),
                source_ref_number=str(work_order.number),
                notes=_build_invoice_notes(work_order),
                exported=False,
                taxes_migrated=True,
                tendered_amount=Decimal('0.00'),
                undep_funds_total=Decimal('0.00'),
            )
            if sales_rep:
                invoice_kwargs['sales_rep_id'] = sales_rep

            invoice = create_acct_trans(**invoice_kwargs)

            logger.info(f"Created Invoice {invoice.transid} (#{reference_number})")

            line_items = create_work_order_line_items(invoice, work_order)
            order_seq = len(line_items)

            wo_discount = work_order.discount_amount if work_order.discount_amount is not None else Decimal('0.00')
            if wo_discount > 0:
                discount_item = ensure_gts_discount_item(using='accounting')
                discount_unit = ensure_discount_item_unit(discount_item, using='accounting')
                ensure_discount_tax_links(discount_item, customer_org, using='accounting')
                discount_entry = apply_discount_to_entries(
                    trans=invoice,
                    product_entries=line_items,
                    discount_amount=wo_discount,
                    order_seq=order_seq,
                    discount_item=discount_item,
                    discount_unit=discount_unit,
                )
                if discount_entry:
                    line_items.append(discount_entry)
                    order_seq += 1

            tax_entries, _tax_plan = apply_taxes_to_document(
                trans=invoice,
                customer_org=customer_org,
                product_entries=line_items,
                order_seq_start=order_seq,
                using="accounting",
            )
            if tax_entries:
                line_items.extend(tax_entries)
                order_seq += len(tax_entries)

            logger.info(f"Created {len(line_items)} line items total ({len(tax_entries)} tax items)")

            actual_total = sum(item.entrytotal for item in line_items)
            invoice.transtotal = actual_total
            invoice.save(using='accounting', update_fields=['transtotal'])
            logger.info(f"Updated Invoice total to ${actual_total}")

            create_gl_entries(invoice, line_items)
            logger.info("Created GL entries for Invoice")

            _validate_tax_applicability(invoice)

            work_order.accounting_invoice_id = invoice.transid
            work_order.save(update_fields=['accounting_invoice_id'])

            logger.info(f"Successfully created invoice {invoice.transid} for WO #{work_order.number}")
            return invoice

    except InvoiceError as e:
        logger.error(
            f"Invoice creation failed for WO #{work_order.number}: {e}",
            exc_info=True
        )
        if strict:
            raise
        return None
    except Exception as e:
        logger.error(
            f"Unexpected error creating invoice for WO #{work_order.number}: {e}",
            exc_info=True
        )
        if strict:
            raise InvoiceError(f"Failed to create invoice: {str(e)}") from e
        return None


def update_invoice_from_work_order(work_order) -> Optional[AcctTrans]:
    if not work_order.accounting_invoice_id:
        logger.info(f"No invoice to update for WO #{work_order.number}")
        return None

    try:
        logger.info(f"Updating invoice for WO #{work_order.number}")

        try:
            invoice = AcctTrans.objects.using('accounting').get(
                transid=work_order.accounting_invoice_id
            )
        except AcctTrans.DoesNotExist:
            logger.warning(
                f"Invoice {work_order.accounting_invoice_id} not found. Recreating."
            )
            work_order.accounting_invoice_id = None
            work_order.save(update_fields=['accounting_invoice_id'])
            return create_invoice_from_work_order(work_order, strict=True)

        if invoice.transstatus.statuscode not in ['OPEN', 'PENDING']:
            logger.warning(
                f"Cannot update Invoice {invoice.transid} - status is "
                f"{invoice.transstatus.statuscode}. Skipping."
            )
            return None

        customer_org = Org.objects.using('accounting').get(org_id=work_order.customer_org_id)

        with transaction.atomic(using='accounting'):
            line_entries = AcctEntry.objects.using('accounting').filter(
                transid=invoice.transid,
                entrytypecode='ITEMENTRY'
            )

            for entry in line_entries:
                AcctEntryApplicTaxes.objects.using('accounting').filter(entry=entry).delete()

            AcctTransTaxRegions.objects.using('accounting').filter(trans=invoice).delete()

            deleted_count = AcctEntry.objects.using('accounting').filter(
                transid=invoice.transid
            ).delete()[0]
            logger.info(f"Deleted {deleted_count} existing entries")

            line_items = create_work_order_line_items(invoice, work_order)
            order_seq = len(line_items)

            wo_discount = work_order.discount_amount if work_order.discount_amount is not None else Decimal('0.00')
            if wo_discount > 0:
                discount_item = ensure_gts_discount_item(using='accounting')
                discount_unit = ensure_discount_item_unit(discount_item, using='accounting')
                ensure_discount_tax_links(discount_item, customer_org, using='accounting')
                discount_entry = apply_discount_to_entries(
                    trans=invoice,
                    product_entries=line_items,
                    discount_amount=wo_discount,
                    order_seq=order_seq,
                    discount_item=discount_item,
                    discount_unit=discount_unit,
                )
                if discount_entry:
                    line_items.append(discount_entry)
                    order_seq += 1

            tax_entries, _tax_plan = apply_taxes_to_document(
                trans=invoice,
                customer_org=customer_org,
                product_entries=line_items,
                order_seq_start=order_seq,
                using="accounting",
            )
            if tax_entries:
                line_items.extend(tax_entries)
                order_seq += len(tax_entries)

            logger.info(f"Created {len(line_items)} line items total ({len(tax_entries)} tax items)")

            actual_total = sum(item.entrytotal for item in line_items)

            wo_date = work_order.date
            if not wo_date:
                from django.utils import timezone
                wo_date = timezone.now().date()

            sales_rep = None
            if getattr(work_order, 'job_by_rep_id', None):
                try:
                    sales_rep = AcctSalesRep.objects.using('accounting').get(pk=work_order.job_by_rep_id)
                except AcctSalesRep.DoesNotExist:
                    pass

            invoice.transtotal = actual_total
            invoice.transdate = wo_date
            invoice.billtotx = build_billtotx(customer_org)
            invoice.sourcerefnumber = str(work_order.number)
            invoice.notes = _build_invoice_notes(work_order)
            invoice.sales_rep_id = sales_rep
            invoice.save(using='accounting', update_fields=[
                'transtotal', 'transdate', 'billtotx', 'sourcerefnumber', 'notes',
                'sales_rep_id',
            ])
            logger.info(f"Updated Invoice total to ${actual_total}")

            create_gl_entries(invoice, line_items)
            logger.info("Created GL entries for Invoice")

            _validate_tax_applicability(invoice)

            logger.info(f"Successfully updated invoice {invoice.transid} for WO #{work_order.number}")
            return invoice

    except InvoiceError:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error updating invoice for WO #{work_order.number}: {e}",
            exc_info=True
        )
        raise InvoiceError(f"Failed to update invoice: {str(e)}") from e


def delete_invoice_and_related(work_order) -> None:
    if not work_order.accounting_invoice_id:
        logger.info(f"No invoice to delete for WO #{work_order.number}")
        return

    try:
        invoice = AcctTrans.objects.using('accounting').get(
            transid=work_order.accounting_invoice_id
        )

        if invoice.transstatus.statuscode not in ['OPEN', 'PENDING']:
            raise InvoiceError(
                f"Cannot delete Invoice {invoice.transid} - status is "
                f"{invoice.transstatus.statuscode}."
            )

        logger.info(f"Deleting invoice {invoice.transid} and related records")

        with transaction.atomic(using='accounting'):
            line_entries = AcctEntry.objects.using('accounting').filter(
                transid=invoice.transid,
                entrytypecode='ITEMENTRY'
            )
            for entry in line_entries:
                AcctEntryApplicTaxes.objects.using('accounting').filter(entry=entry).delete()

            AcctTransTaxRegions.objects.using('accounting').filter(trans=invoice).delete()

            AcctEntry.objects.using('accounting').filter(transid=invoice.transid).delete()

            AcctTrans.objects.using('accounting').filter(transid=invoice.transid).delete()

            work_order.accounting_invoice_id = None
            work_order.save(update_fields=['accounting_invoice_id'])

            logger.info(f"Successfully deleted all accounting records for WO #{work_order.number}")

    except AcctTrans.DoesNotExist:
        logger.warning(f"Invoice {work_order.accounting_invoice_id} not found in accounting")
        work_order.accounting_invoice_id = None
        work_order.save(update_fields=['accounting_invoice_id'])
    except InvoiceError:
        raise
    except Exception as e:
        logger.error(f"Failed to delete accounting records for WO #{work_order.number}: {e}", exc_info=True)
        raise InvoiceError(f"Failed to delete accounting records: {e}")
