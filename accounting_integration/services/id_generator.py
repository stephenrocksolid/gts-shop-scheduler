import logging
from django.db import DatabaseError

from accounting_integration.exceptions import IDGenerationError

logger = logging.getLogger('accounting_integration')


def get_next_id(table_name: str, pk_column: str, using: str = 'accounting') -> int:
    from django.db import connections

    sequence_name = f"{table_name}_{pk_column}_seq"

    try:
        db_connection = connections[using]

        with db_connection.cursor() as cursor:
            sql = f"SELECT nextval('{sequence_name}')"
            cursor.execute(sql)
            next_id = cursor.fetchone()[0]
            return int(next_id)

    except DatabaseError as e:
        error_msg = f"Failed to generate ID from sequence '{sequence_name}': {str(e)}"
        logger.error(error_msg)
        raise IDGenerationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error generating ID from sequence '{sequence_name}': {str(e)}"
        logger.error(error_msg)
        raise IDGenerationError(error_msg) from e


def get_next_trans_id(using: str = 'accounting') -> int:
    return get_next_id('acct_trans', 'transid', using)


def get_next_entry_id(using: str = 'accounting') -> int:
    return get_next_id('acct_entry', 'entryid', using)
