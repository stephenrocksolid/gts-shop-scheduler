import logging
from decimal import Decimal
from django.db import IntegrityError, connections, transaction
from django.utils import timezone
from accounting_integration.models import (
    AcctTrans, AcctEntry, AcctTransType, AcctTransStatus,
    Org, ItmItems, ItmItemUnit, GlAcct,
)
from accounting_integration.services.id_generator import get_next_id

logger = logging.getLogger('accounting_integration')


def _is_transid_duplicate(error: IntegrityError) -> bool:
    cause = getattr(error, "__cause__", None)
    pgcode = getattr(cause, "pgcode", None)
    constraint = getattr(getattr(cause, "diag", None), "constraint_name", None)
    if pgcode == "23505" and constraint == "acct_trans_pkey":
        return True
    return "acct_trans_pkey" in str(error)


def _repair_sequence(table: str, pk: str, using: str = 'accounting') -> None:
    sequence_name = f"{table}_{pk}_seq"
    conn = connections[using]
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT max({pk}) FROM {table}")
        max_id = cursor.fetchone()[0]
        if max_id is None:
            cursor.execute("SELECT setval(%s, %s, %s)", (sequence_name, 1, False))
            logger.warning(f"Sequence {sequence_name} reset to 1 (empty {table})")
        else:
            cursor.execute("SELECT setval(%s, %s, %s)", (sequence_name, int(max_id), True))
            logger.warning(f"Sequence {sequence_name} repaired to {max_id}")


def create_acct_trans(
    trans_type_code: str,
    org: Org,
    trans_date,
    reference_number: str,
    trans_total: Decimal,
    status_code: str = 'OPEN',
    memo: str = '',
    notes: str = '',
    terms_id=None,
    bill_to_tx: str = '',
    source_ref_number: str = '',
    **kwargs
) -> AcctTrans:
    trans_type = AcctTransType.objects.using('accounting').get(accttranstypecode=trans_type_code)
    status = AcctTransStatus.objects.using('accounting').get(statuscode=status_code)
    trans_id = kwargs.pop('transid', None)
    auto_generated = trans_id is None
    if auto_generated:
        trans_id = get_next_id('acct_trans', 'transid', using='accounting')

    defaults = {
        'transtypecode': trans_type,
        'transid': trans_id,
        'createdate': timezone.now(),
        'exported': False,
        'fromdate': None,
        'memo': memo,
        'notes': notes,
        'printed': False,
        'referencenumber': reference_number,
        'todate': None,
        'transtotal': trans_total,
        'transdate': trans_date,
        'rec_version': 0,
        'billtotx': bill_to_tx,
        'fobtx': '',
        'pmtreference': '',
        'shiptotx': '',
        'sourcerefnumber': source_ref_number,
        'taxes_migrated': True,
        'is_jrn_deposit_eligible': True,
        'tendered_amount': Decimal('0.00'),
        'orgid': org,
        'transstatus': status,
    }
    if terms_id:
        defaults['termsid'] = terms_id

    defaults.update(kwargs)

    def _create_trans(trans_id_override):
        defaults_with_id = dict(defaults, transid=trans_id_override)
        with transaction.atomic(using='accounting'):
            return AcctTrans.objects.using('accounting').create(**defaults_with_id)

    try:
        trans = _create_trans(trans_id)
    except IntegrityError as exc:
        if auto_generated and _is_transid_duplicate(exc):
            logger.warning("Detected acct_trans duplicate transid; repairing sequence and retrying once")
            _repair_sequence('acct_trans', 'transid', using='accounting')
            trans_id = get_next_id('acct_trans', 'transid', using='accounting')
            trans = _create_trans(trans_id)
        else:
            raise

    logger.info(f"Created {trans_type_code} transaction {trans.transid} (ref: {reference_number})")

    return trans


def create_item_entry(
    trans: AcctTrans,
    item: ItmItems,
    item_unit: ItmItemUnit,
    quantity: Decimal,
    unit_price: Decimal,
    memo: str,
    order_seq: int = 0,
    **kwargs
) -> AcctEntry:
    entry_id = get_next_id('acct_entry', 'entryid', using='accounting')

    line_total = quantity * unit_price

    defaults = {
        'entryid': entry_id,
        'entrytypecode': 'ITEMENTRY',
        'transid': trans,
        'itemid': item,
        'itemunitid': item_unit,
        'entryqty': quantity,
        'entryamnt': unit_price,
        'measure_qty': Decimal('1.0'),
        'entrytotal': line_total,
        'main_unit_qty': quantity,
        'memotx': memo,
        'orderseq': order_seq,
        'active': True,
        'billable': False,
        'billed': False,
        'cleared': False,
        'createdate': timezone.now(),
        'discount_applied': Decimal('0.00'),
        'asset_value_verified': False,
        'total_asset_value': Decimal('0.00'),
        'rec_version': 0
    }

    defaults.update(kwargs)

    entry = AcctEntry.objects.using('accounting').create(**defaults)
    logger.debug(f"Created ITEMENTRY {entry_id} for item {item.itemnumber}")

    return entry


def create_gl_entry(
    trans: AcctTrans,
    gl_acct: GlAcct,
    amount: Decimal,
    memo: str,
    order_seq: int = 0,
    **kwargs
) -> AcctEntry:
    entry_id = get_next_id('acct_entry', 'entryid', using='accounting')

    defaults = {
        'entryid': entry_id,
        'entrytypecode': 'GLENTRY',
        'transid': trans,
        'glacctid': gl_acct,
        'entryqty': Decimal('1.0'),
        'entryamnt': amount,
        'measure_qty': Decimal('1.0'),
        'entrytotal': amount,
        'main_unit_qty': Decimal('1.0'),
        'memotx': memo,
        'orderseq': order_seq,
        'active': True,
        'billable': False,
        'billed': False,
        'cleared': False,
        'createdate': timezone.now(),
        'discount_applied': Decimal('0.00'),
        'asset_value_verified': False,
        'total_asset_value': Decimal('0.00'),
        'rec_version': 0
    }

    defaults.update(kwargs)

    entry = AcctEntry.objects.using('accounting').create(**defaults)
    logger.debug(f"Created GLENTRY {entry_id} for GL {gl_acct.glnumber}: ${amount}")

    return entry
