from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError


@pytest.mark.django_db
def test_work_order_v2_allocates_number_from_sequence(job, calendar):
    from rental_scheduler.models import Job, WorkOrderNumberSequence, WorkOrderV2
    from django.utils import timezone
    from datetime import timedelta

    WorkOrderNumberSequence.get_solo(start_number=500)

    other_job = Job.objects.create(
        calendar=calendar,
        business_name="Other Business",
        start_dt=timezone.now(),
        end_dt=timezone.now() + timedelta(hours=1),
        all_day=False,
        status="uncompleted",
    )

    wo1 = WorkOrderV2.objects.create(job=job)
    wo2 = WorkOrderV2.objects.create(job=other_job)

    assert wo1.number == 500
    assert wo2.number == 501


@pytest.mark.django_db
def test_work_order_v2_recalculates_totals_from_lines(job):
    from rental_scheduler.models import WorkOrderLineV2, WorkOrderV2

    wo = WorkOrderV2.objects.create(
        job=job,
        discount_type="percent",
        discount_value=Decimal("10.00"),
    )

    line = WorkOrderLineV2.objects.create(
        work_order=wo,
        itemid=123,
        qty=Decimal("2.00"),
        price=Decimal("50.00"),
    )

    assert line.amount == Decimal("100.00")

    wo.refresh_from_db()
    assert wo.subtotal == Decimal("100.00")
    assert wo.discount_amount == Decimal("10.00")
    assert wo.total == Decimal("90.00")


@pytest.mark.django_db
def test_work_order_v2_rejects_percent_discount_over_100(job):
    from rental_scheduler.models import WorkOrderV2

    wo = WorkOrderV2(
        job=job,
        discount_type="percent",
        discount_value=Decimal("100.01"),
    )
    with pytest.raises(ValidationError):
        wo.full_clean()
