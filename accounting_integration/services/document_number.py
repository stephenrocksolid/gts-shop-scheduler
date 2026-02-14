import re
import logging
from django.db import transaction
from accounting_integration.models import AcctTransType
from accounting_integration.exceptions import DocumentNumberError

logger = logging.getLogger('accounting_integration')

TRAILING_DIGITS_RE = re.compile(r'^(.*?)(\d+)$')


def split_prefix_and_number(doc_number: str) -> tuple:
    if not doc_number or not doc_number.strip():
        raise ValueError(f"Document number is empty: {doc_number}")

    stripped = doc_number.strip()
    match = TRAILING_DIGITS_RE.match(stripped)

    if not match:
        raise ValueError(f"Cannot parse number from: {doc_number}")

    prefix = match.group(1)
    digits = match.group(2)

    current_num = int(digits)
    next_num = current_num + 1
    next_digits = str(next_num).zfill(len(digits))

    return prefix, digits, next_digits


def parse_and_increment(current_number: str) -> str:
    prefix, _, next_digits = split_prefix_and_number(current_number)
    return prefix + next_digits


def allocate_next_doc_number(transtypecode: str) -> str:
    try:
        with transaction.atomic(using='accounting'):
            trans_type = (
                AcctTransType.objects
                .using('accounting')
                .select_for_update()
                .get(accttranstypecode=transtypecode)
            )

            last_seq = trans_type.lastsequence
            if not last_seq:
                raise DocumentNumberError(
                    f"lastsequence is null for {transtypecode}. "
                    "Please set an initial sequence in Classic Accounting."
                )

            next_number = parse_and_increment(last_seq)

            trans_type.lastsequence = next_number
            trans_type.save(using='accounting', update_fields=['lastsequence'])

            logger.info(
                f"Allocated {transtypecode} number '{next_number}' "
                f"(updated lastsequence from '{last_seq}' to '{next_number}')"
            )

            return next_number

    except AcctTransType.DoesNotExist:
        raise DocumentNumberError(f"Transaction type '{transtypecode}' not found")
    except ValueError as e:
        raise DocumentNumberError(f"Failed to parse document number: {e}")
    except DocumentNumberError:
        raise
    except Exception as e:
        logger.error(f"Failed to allocate document number for {transtypecode}: {e}")
        raise DocumentNumberError(f"Failed to allocate document number: {e}")
