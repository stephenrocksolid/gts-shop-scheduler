"""Tests for editing a finite recurring series to become forever."""

import pytest
from datetime import datetime, timedelta
from django.urls import reverse
from django.utils import timezone
from rental_scheduler.models import Job
from rental_scheduler.utils.recurrence import is_forever_series


@pytest.fixture
def finite_monthly_series(calendar):
    """Create a finite monthly recurring series with 12 occurrences."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(2025, 1, 15, 10, 0, 0), tz)
    end = start + timedelta(hours=2)
    job = Job.objects.create(
        calendar=calendar,
        business_name="Finite Monthly Series",
        start_dt=start,
        end_dt=end,
        all_day=False,
        status="uncompleted",
    )
    job.create_recurrence_rule(recurrence_type="monthly", interval=1, count=12)
    job.generate_recurring_instances()
    return job


@pytest.mark.django_db
class TestFiniteToForeverEdit:
    """Test editing a finite recurring series to become forever."""
    
    def test_edit_finite_to_forever(self, api_client, finite_monthly_series):
        """Test that editing a finite series to 'never' makes it forever."""
        # Verify initial state
        assert not is_forever_series(finite_monthly_series)
        assert finite_monthly_series.recurrence_rule['count'] == 12
        assert finite_monthly_series.recurrence_instances.count() == 12
        
        # Edit the parent to make it forever
        url = reverse('rental_scheduler:job_create_submit')
        data = {
            'job_id': finite_monthly_series.id,
            'calendar': finite_monthly_series.calendar.id,
            'business_name': finite_monthly_series.business_name,
            'start_dt': finite_monthly_series.start_dt.strftime('%Y-%m-%dT%H:%M'),
            'end_dt': finite_monthly_series.end_dt.strftime('%Y-%m-%dT%H:%M'),
            'all_day': 'off',
            'recurrence_enabled': 'on',
            'recurrence_type': 'monthly',
            'recurrence_interval': '1',
            'recurrence_end': 'never',  # Change to forever
        }
        
        response = api_client.post(url, data)
        assert response.status_code == 200
        
        # Reload the job and verify it's now forever
        finite_monthly_series.refresh_from_db()
        assert is_forever_series(finite_monthly_series)
        assert finite_monthly_series.recurrence_rule.get('end') == 'never'
        assert finite_monthly_series.recurrence_rule.get('count') is None
        assert finite_monthly_series.recurrence_rule.get('until_date') is None
        
        # Existing instances should still exist (no data loss)
        assert finite_monthly_series.recurrence_instances.count() == 12
    
    def test_edit_forever_to_finite_count(self, api_client, calendar):
        """Test that editing a forever series to have a count makes it finite."""
        # Create a forever series
        tz = timezone.get_current_timezone()
        start = timezone.make_aware(datetime(2025, 1, 15, 10, 0, 0), tz)
        end = start + timedelta(hours=2)
        job = Job.objects.create(
            calendar=calendar,
            business_name="Forever Weekly Series",
            start_dt=start,
            end_dt=end,
            all_day=False,
            status="uncompleted",
        )
        job.recurrence_rule = {'type': 'weekly', 'interval': 1, 'end': 'never'}
        job.save()
        
        # Verify initial state
        assert is_forever_series(job)
        
        # Edit to make it finite
        url = reverse('rental_scheduler:job_create_submit')
        data = {
            'job_id': job.id,
            'calendar': job.calendar.id,
            'business_name': job.business_name,
            'start_dt': job.start_dt.strftime('%Y-%m-%dT%H:%M'),
            'end_dt': job.end_dt.strftime('%Y-%m-%dT%H:%M'),
            'all_day': 'off',
            'recurrence_enabled': 'on',
            'recurrence_type': 'weekly',
            'recurrence_interval': '1',
            'recurrence_end': 'after_count',
            'recurrence_count': '10',
        }
        
        response = api_client.post(url, data)
        assert response.status_code == 200
        
        # Reload and verify it's now finite
        job.refresh_from_db()
        assert not is_forever_series(job)
        assert job.recurrence_rule.get('count') == 10
        assert 'end' not in job.recurrence_rule or job.recurrence_rule['end'] != 'never'
    
    def test_cannot_edit_recurrence_for_instance(self, api_client, finite_monthly_series):
        """Test that trying to edit recurrence for an instance fails gracefully."""
        # Get an instance
        instance = finite_monthly_series.recurrence_instances.first()
        assert instance is not None
        
        # Try to edit the instance's recurrence (should fail)
        url = reverse('rental_scheduler:job_create_submit')
        data = {
            'job_id': instance.id,
            'calendar': instance.calendar.id,
            'business_name': instance.business_name,
            'start_dt': instance.start_dt.strftime('%Y-%m-%dT%H:%M'),
            'end_dt': instance.end_dt.strftime('%Y-%m-%dT%H:%M'),
            'all_day': 'off',
            'recurrence_enabled': 'on',
            'recurrence_type': 'monthly',
            'recurrence_interval': '1',
            'recurrence_end': 'never',
        }
        
        response = api_client.post(url, data, follow=True)
        # Should redirect with error message
        assert response.status_code == 200
        # The instance's parent shouldn't be affected
        finite_monthly_series.refresh_from_db()
        assert not is_forever_series(finite_monthly_series)

