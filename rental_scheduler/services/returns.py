from django.db import transaction
from rental_scheduler.models import Contract

def backfill_missing_returns(trailer, cutoff_datetime):
    if not trailer or not cutoff_datetime:
        return 0
    with transaction.atomic():
        queryset = Contract.objects.filter(
            trailer=trailer,
            is_returned=False,
            start_datetime__lt=cutoff_datetime,
        ).order_by('start_datetime')
        updates = []
        for item in queryset:
            item.is_returned = True
            item.return_datetime = item.end_datetime if item.end_datetime <= cutoff_datetime else cutoff_datetime
            updates.append(item)
        if updates:
            Contract.objects.bulk_update(updates, ['is_returned', 'return_datetime', 'updated_at'])
        return len(updates)


