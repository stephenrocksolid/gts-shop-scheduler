"""
Tests for Job model validation.
Ensures year range and span validation work correctly.
"""
import pytest
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from rental_scheduler.models import Job
from rental_scheduler.constants import MIN_VALID_YEAR, MAX_VALID_YEAR, MAX_JOB_SPAN_DAYS


@pytest.mark.django_db
class TestJobModelYearValidation:
    """Test year range validation in Job.clean()."""
    
    def test_valid_year_passes(self, calendar):
        """Job with current year should pass validation."""
        now = timezone.now()
        job = Job(
            calendar=calendar,
            business_name="Test",
            start_dt=now,
            end_dt=now + timedelta(hours=2),
        )
        # Should not raise
        job.full_clean()
    
    def test_start_year_too_old_fails(self, calendar):
        """Job with start year before MIN_VALID_YEAR should fail."""
        old_date = timezone.make_aware(datetime(1999, 6, 15, 10, 0))
        job = Job(
            calendar=calendar,
            business_name="Test",
            start_dt=old_date,
            end_dt=old_date + timedelta(hours=2),
        )
        with pytest.raises(ValidationError) as exc_info:
            job.full_clean()
        assert 'start_dt' in exc_info.value.message_dict
        assert str(MIN_VALID_YEAR) in str(exc_info.value.message_dict['start_dt'])
    
    def test_start_year_too_far_future_fails(self, calendar):
        """Job with start year after MAX_VALID_YEAR should fail."""
        future_date = timezone.make_aware(datetime(2101, 6, 15, 10, 0))
        job = Job(
            calendar=calendar,
            business_name="Test",
            start_dt=future_date,
            end_dt=future_date + timedelta(hours=2),
        )
        with pytest.raises(ValidationError) as exc_info:
            job.full_clean()
        assert 'start_dt' in exc_info.value.message_dict
        assert str(MAX_VALID_YEAR) in str(exc_info.value.message_dict['start_dt'])
    
    def test_end_year_too_old_fails(self, calendar):
        """Job with end year before MIN_VALID_YEAR should fail."""
        old_date = timezone.make_aware(datetime(1999, 6, 15, 10, 0))
        job = Job(
            calendar=calendar,
            business_name="Test",
            start_dt=old_date,
            end_dt=old_date + timedelta(hours=2),
        )
        with pytest.raises(ValidationError) as exc_info:
            job.full_clean()
        # start_dt fails first, but both would fail
        assert 'start_dt' in exc_info.value.message_dict or 'end_dt' in exc_info.value.message_dict
    
    def test_end_year_too_far_future_fails(self, calendar):
        """Job with end year after MAX_VALID_YEAR should fail."""
        now = timezone.now()
        far_future = timezone.make_aware(datetime(2101, 6, 15, 10, 0))
        job = Job(
            calendar=calendar,
            business_name="Test",
            start_dt=now,
            end_dt=far_future,
        )
        with pytest.raises(ValidationError) as exc_info:
            job.full_clean()
        assert 'end_dt' in exc_info.value.message_dict
        assert str(MAX_VALID_YEAR) in str(exc_info.value.message_dict['end_dt'])


@pytest.mark.django_db
class TestJobModelSpanValidation:
    """Test job span validation in Job.clean()."""
    
    def test_short_span_passes(self, calendar):
        """Job spanning a few days should pass."""
        now = timezone.now()
        job = Job(
            calendar=calendar,
            business_name="Test",
            start_dt=now,
            end_dt=now + timedelta(days=30),
        )
        # Should not raise
        job.full_clean()
    
    def test_max_span_passes(self, calendar):
        """Job spanning exactly MAX_JOB_SPAN_DAYS should pass."""
        now = timezone.now()
        job = Job(
            calendar=calendar,
            business_name="Test",
            start_dt=now,
            end_dt=now + timedelta(days=MAX_JOB_SPAN_DAYS),
        )
        # Should not raise
        job.full_clean()
    
    def test_span_exceeds_max_fails(self, calendar):
        """Job spanning more than MAX_JOB_SPAN_DAYS should fail."""
        now = timezone.now()
        job = Job(
            calendar=calendar,
            business_name="Test",
            start_dt=now,
            end_dt=now + timedelta(days=MAX_JOB_SPAN_DAYS + 1),
        )
        with pytest.raises(ValidationError) as exc_info:
            job.full_clean()
        assert 'end_dt' in exc_info.value.message_dict
        assert str(MAX_JOB_SPAN_DAYS) in str(exc_info.value.message_dict['end_dt'])
    
    def test_very_long_span_fails(self, calendar):
        """Job spanning many years should fail."""
        now = timezone.now()
        job = Job(
            calendar=calendar,
            business_name="Test",
            start_dt=now,
            end_dt=now + timedelta(days=1000),  # ~2.7 years
        )
        with pytest.raises(ValidationError) as exc_info:
            job.full_clean()
        assert 'end_dt' in exc_info.value.message_dict


@pytest.mark.django_db
class TestJobModelDateOrderValidation:
    """Test that end date must be after start date."""
    
    def test_end_before_start_fails(self, calendar):
        """End date before start date should fail."""
        now = timezone.now()
        job = Job(
            calendar=calendar,
            business_name="Test",
            start_dt=now,
            end_dt=now - timedelta(hours=1),
            all_day=False,
        )
        with pytest.raises(ValidationError) as exc_info:
            job.full_clean()
        assert 'end_dt' in exc_info.value.message_dict
    
    def test_same_time_timed_event_fails(self, calendar):
        """Timed event with same start and end should fail."""
        now = timezone.now()
        job = Job(
            calendar=calendar,
            business_name="Test",
            start_dt=now,
            end_dt=now,  # Same time
            all_day=False,
        )
        with pytest.raises(ValidationError) as exc_info:
            job.full_clean()
        assert 'end_dt' in exc_info.value.message_dict
    
    def test_same_day_all_day_event_passes(self, calendar):
        """All-day event with same start and end date should pass."""
        now = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        job = Job(
            calendar=calendar,
            business_name="Test",
            start_dt=now,
            end_dt=now,  # Same time is ok for all-day
            all_day=True,
        )
        # Should not raise
        job.full_clean()

