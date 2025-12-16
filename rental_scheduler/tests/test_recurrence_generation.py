from datetime import datetime, timedelta

import pytest
from django.utils import timezone

from rental_scheduler.models import CallReminder, Job
from rental_scheduler.utils.events import get_call_reminder_sunday


@pytest.mark.django_db
def test_monthly_recurrence_preserves_nth_weekday(calendar):
    """
    Jan 16, 2026 is the 3rd Friday of Jan 2026.
    The next monthly occurrence should be the 3rd Friday of Feb 2026 (Feb 20, 2026),
    not Feb 16, 2026 (which would be day-of-month recurrence).
    """
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 16, 10, 0, 0), tz)
    end = start + timedelta(hours=2)

    job = Job.objects.create(
        calendar=calendar,
        business_name="Nth weekday test",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )

    job.create_recurrence_rule(recurrence_type="monthly", interval=1, count=1)
    instances = job.generate_recurring_instances()

    assert len(instances) == 1
    instance_local = timezone.localtime(instances[0].start_dt, tz)
    assert instance_local.date().isoformat() == "2026-02-20"
    assert (instance_local.hour, instance_local.minute) == (10, 0)


@pytest.mark.django_db
def test_recurring_instances_copy_call_reminder_and_create_call_reminders(calendar):
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    parent = Job.objects.create(
        calendar=calendar,
        business_name="Call reminder parent",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
        has_call_reminder=True,
        call_reminder_weeks_prior=2,
        call_reminder_completed=True,  # Instances should reset to False
    )

    parent.create_recurrence_rule(recurrence_type="daily", interval=1, count=2)
    instances = parent.generate_recurring_instances()

    assert len(instances) == 2
    assert CallReminder.objects.filter(job__in=instances).count() == 2

    for inst in instances:
        inst.refresh_from_db()
        assert inst.has_call_reminder is True
        assert inst.call_reminder_weeks_prior == 2
        assert inst.call_reminder_completed is False

        reminder = CallReminder.objects.get(job=inst)
        assert reminder.completed is False
        assert reminder.reminder_date == get_call_reminder_sunday(inst.start_dt, 2).date()


