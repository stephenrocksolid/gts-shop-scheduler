from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from rental_scheduler.models import CallReminder, Job
from rental_scheduler.utils.events import get_call_reminder_sunday
from rental_scheduler.utils.recurrence import (
    compute_occurrence_number,
    get_recurrence_meta,
)


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


# =============================================================================
# Tests for compute_occurrence_number
# =============================================================================

@pytest.mark.django_db
def test_compute_occurrence_number_parent_is_one(calendar):
    """Parent job should always be occurrence 1."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    job = Job.objects.create(
        calendar=calendar,
        business_name="Parent test",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )
    job.create_recurrence_rule(recurrence_type="monthly", interval=1, count=5)

    # Parent's own start is occurrence 1
    occurrence_num = compute_occurrence_number(job, start)
    assert occurrence_num == 1


@pytest.mark.django_db
def test_compute_occurrence_number_daily(calendar):
    """Test daily recurrence occurrence numbering."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    job = Job.objects.create(
        calendar=calendar,
        business_name="Daily test",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )
    job.create_recurrence_rule(recurrence_type="daily", interval=1, count=10)
    instances = job.generate_recurring_instances()

    # First instance should be occurrence 2
    assert compute_occurrence_number(job, instances[0].recurrence_original_start) == 2
    # Fifth instance should be occurrence 6
    assert compute_occurrence_number(job, instances[4].recurrence_original_start) == 6


@pytest.mark.django_db
def test_compute_occurrence_number_weekly(calendar):
    """Test weekly recurrence occurrence numbering."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    job = Job.objects.create(
        calendar=calendar,
        business_name="Weekly test",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )
    job.create_recurrence_rule(recurrence_type="weekly", interval=2, count=5)
    instances = job.generate_recurring_instances()

    # First instance (2 weeks later) should be occurrence 2
    assert compute_occurrence_number(job, instances[0].recurrence_original_start) == 2
    # Third instance (6 weeks later) should be occurrence 4
    assert compute_occurrence_number(job, instances[2].recurrence_original_start) == 4


@pytest.mark.django_db
def test_compute_occurrence_number_monthly(calendar):
    """Test monthly recurrence occurrence numbering."""
    tz = timezone.get_current_timezone()
    # Jan 16, 2026 is 3rd Friday
    start = timezone.make_aware(datetime(2026, 1, 16, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    job = Job.objects.create(
        calendar=calendar,
        business_name="Monthly test",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )
    job.create_recurrence_rule(recurrence_type="monthly", interval=1, count=3)
    instances = job.generate_recurring_instances()

    # First instance should be occurrence 2
    assert compute_occurrence_number(job, instances[0].recurrence_original_start) == 2
    # Third instance should be occurrence 4
    assert compute_occurrence_number(job, instances[2].recurrence_original_start) == 4


@pytest.mark.django_db
def test_compute_occurrence_number_yearly(calendar):
    """Test yearly recurrence occurrence numbering."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    job = Job.objects.create(
        calendar=calendar,
        business_name="Yearly test",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )
    job.create_recurrence_rule(recurrence_type="yearly", interval=1, count=3)
    instances = job.generate_recurring_instances()

    # First instance (1 year later) should be occurrence 2
    assert compute_occurrence_number(job, instances[0].recurrence_original_start) == 2


@pytest.mark.django_db
def test_compute_occurrence_number_not_in_series(calendar):
    """Test that a datetime not in the series returns None."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    job = Job.objects.create(
        calendar=calendar,
        business_name="Not in series test",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )
    job.create_recurrence_rule(recurrence_type="weekly", interval=1, count=5)

    # A random date not in the series
    random_date = timezone.make_aware(datetime(2026, 1, 12, 10, 0, 0), tz)
    assert compute_occurrence_number(job, random_date) is None


# =============================================================================
# Tests for get_recurrence_meta
# =============================================================================

@pytest.mark.django_db
def test_get_recurrence_meta_non_recurring(calendar):
    """Non-recurring job returns is_recurring=False."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    job = Job.objects.create(
        calendar=calendar,
        business_name="Non recurring",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )

    meta = get_recurrence_meta(job)
    assert meta['is_recurring'] is False
    assert meta['is_parent'] is False
    assert meta['is_instance'] is False


@pytest.mark.django_db
def test_get_recurrence_meta_parent(calendar):
    """Parent job returns is_parent=True with occurrence 1."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    job = Job.objects.create(
        calendar=calendar,
        business_name="Parent job",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )
    job.create_recurrence_rule(recurrence_type="monthly", interval=1, count=5)

    meta = get_recurrence_meta(job)
    assert meta['is_recurring'] is True
    assert meta['is_parent'] is True
    assert meta['is_instance'] is False
    assert meta['parent_id'] == job.id
    assert meta['occurrence_number'] == 1
    assert meta['total_occurrences'] == 6  # count + 1 (parent is occurrence 1)
    assert 'Repeats monthly' in meta['summary']


@pytest.mark.django_db
def test_get_recurrence_meta_instance(calendar):
    """Recurring instance returns is_instance=True with correct occurrence number."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    parent = Job.objects.create(
        calendar=calendar,
        business_name="Parent job",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )
    parent.create_recurrence_rule(recurrence_type="daily", interval=1, count=5)
    instances = parent.generate_recurring_instances()

    # Test third instance
    instance = instances[2]
    meta = get_recurrence_meta(instance)
    
    assert meta['is_recurring'] is True
    assert meta['is_parent'] is False
    assert meta['is_instance'] is True
    assert meta['parent_id'] == parent.id
    assert meta['occurrence_number'] == 4  # 3rd instance = occurrence 4 (1-based)
    assert meta['total_occurrences'] == 6  # count + 1


@pytest.mark.django_db
def test_get_recurrence_meta_forever_series(calendar):
    """Forever series shows is_forever=True with no total_occurrences."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    job = Job.objects.create(
        calendar=calendar,
        business_name="Forever parent",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
        recurrence_rule={'type': 'monthly', 'interval': 1, 'end': 'never'},
    )

    meta = get_recurrence_meta(job)
    assert meta['is_recurring'] is True
    assert meta['is_forever'] is True
    assert meta['total_occurrences'] is None
    assert 'Forever' in meta['summary']


# =============================================================================
# Tests for job_create_partial view with recurrence_meta
# =============================================================================

@pytest.mark.django_db
def test_job_create_partial_shows_recurrence_banner(calendar, api_client):
    """Editing a recurring instance should show the occurrence banner."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    parent = Job.objects.create(
        calendar=calendar,
        business_name="Parent job",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )
    parent.create_recurrence_rule(recurrence_type="weekly", interval=1, count=5)
    instances = parent.generate_recurring_instances()

    # Edit the second instance (occurrence 3)
    instance = instances[1]
    url = reverse('rental_scheduler:job_create_partial') + f'?edit={instance.id}'
    response = api_client.get(url)

    assert response.status_code == 200
    content = response.content.decode('utf-8')
    
    # Should show compact series hint with occurrence number
    assert 'Part of series' in content
    assert '#3' in content  # 2nd instance = occurrence 3


@pytest.mark.django_db
def test_job_create_partial_shows_parent_banner(calendar, api_client):
    """Editing a recurring parent should show the compact parent series banner."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    parent = Job.objects.create(
        calendar=calendar,
        business_name="Parent job",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )
    parent.create_recurrence_rule(recurrence_type="monthly", interval=1, count=5)

    url = reverse('rental_scheduler:job_create_partial') + f'?edit={parent.id}'
    response = api_client.get(url)

    assert response.status_code == 200
    content = response.content.decode('utf-8')
    
    # Should show compact "Series template" text and occurrence 1
    assert 'Series template' in content
    assert '#1' in content


@pytest.mark.django_db
def test_job_create_partial_forever_shows_infinity(calendar, api_client):
    """Forever series should show infinity symbol."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    parent = Job.objects.create(
        calendar=calendar,
        business_name="Forever parent",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
        recurrence_rule={'type': 'monthly', 'interval': 1, 'end': 'never'},
    )

    url = reverse('rental_scheduler:job_create_partial') + f'?edit={parent.id}'
    response = api_client.get(url)

    assert response.status_code == 200
    content = response.content.decode('utf-8')
    
    # Should show infinity symbol for forever series
    assert '∞' in content


@pytest.mark.django_db
def test_job_create_partial_until_date_does_not_show_infinity(calendar, api_client):
    """Until-date series should NOT show infinity symbol."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    parent = Job.objects.create(
        calendar=calendar,
        business_name="Until-date parent",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
        recurrence_rule={'type': 'yearly', 'interval': 1, 'until_date': '2028-01-28'},
    )

    url = reverse('rental_scheduler:job_create_partial') + f'?edit={parent.id}'
    response = api_client.get(url)

    assert response.status_code == 200
    content = response.content.decode('utf-8')
    
    # Should NOT show infinity symbol for until-date series
    assert '∞' not in content
    # Should show the until date in the form
    assert '2028-01-28' in content


@pytest.mark.django_db
def test_job_create_partial_interval_field_populates(calendar, api_client):
    """Interval field should render correctly with no whitespace issues."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2026, 1, 10, 10, 0, 0), tz)
    end = start + timedelta(hours=1)

    parent = Job.objects.create(
        calendar=calendar,
        business_name="Interval test",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
        recurrence_rule={'type': 'monthly', 'interval': 3, 'count': 5},
    )

    url = reverse('rental_scheduler:job_create_partial') + f'?edit={parent.id}'
    response = api_client.get(url)

    assert response.status_code == 200
    content = response.content.decode('utf-8')
    
    # Should contain interval field with value="3" (no whitespace)
    assert 'name="recurrence_interval"' in content
    assert 'value="3"' in content



