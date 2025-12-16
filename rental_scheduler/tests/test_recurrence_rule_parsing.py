import pytest


@pytest.mark.django_db
def test_create_recurrence_rule_accepts_iso_date_string(job):
    job.create_recurrence_rule(
        recurrence_type="monthly",
        interval=1,
        count=5,
        until_date="2026-01-15",
    )

    job.refresh_from_db()
    assert job.recurrence_rule["until_date"] == "2026-01-15"


def test_repeat_choices_include_daily_and_weekly():
    from rental_scheduler.models import Job

    values = {value for value, _label in Job.REPEAT_CHOICES}
    assert "daily" in values
    assert "weekly" in values


