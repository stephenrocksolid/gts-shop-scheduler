import pytest
from decimal import Decimal


@pytest.mark.django_db
def test_work_order_number_sequence_allocates_sequential_numbers():
    from rental_scheduler.models import WorkOrderNumberSequence

    seq = WorkOrderNumberSequence.get_solo(start_number=100)
    assert seq.start_number == 100
    assert seq.next_number == 100

    n1 = WorkOrderNumberSequence.allocate_work_order_number()
    n2 = WorkOrderNumberSequence.allocate_work_order_number()

    assert (n1, n2) == (100, 101)

    seq.refresh_from_db()
    assert seq.next_number == 102


@pytest.mark.django_db
def test_editing_wo_number_advances_sequence(job):
    from rental_scheduler.models import WorkOrderNumberSequence, WorkOrderV2

    WorkOrderNumberSequence.get_solo(start_number=1)

    wo = WorkOrderV2.objects.create(
        job=job, discount_type="amount", discount_value=Decimal("0.00"),
    )
    assert wo.number == 1

    seq = WorkOrderNumberSequence.objects.get(pk=1)
    assert seq.next_number == 2

    wo.number = 1009
    wo.save()

    seq.refresh_from_db()
    assert seq.next_number == 1010
