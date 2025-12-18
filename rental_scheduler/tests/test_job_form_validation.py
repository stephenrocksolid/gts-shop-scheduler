"""
Tests for JobForm validation.
Ensures form-level year range, span, and required field validation work correctly.
"""
import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from rental_scheduler.forms import JobForm
from rental_scheduler.models import Job
from rental_scheduler.constants import MIN_VALID_YEAR, MAX_VALID_YEAR, MAX_JOB_SPAN_DAYS


@pytest.mark.django_db
class TestJobFormRequiredFields:
    """Test that required fields (business_name, start_dt, end_dt, calendar) are enforced."""
    
    def get_valid_form_data(self, calendar):
        """Return valid form data with all required fields."""
        now = timezone.now()
        return {
            'calendar': calendar.id,
            'business_name': 'Test Business',
            'start_dt': now.strftime('%Y-%m-%dT%H:%M'),
            'end_dt': (now + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M'),
            'all_day': False,
            'status': 'uncompleted',
        }
    
    def test_valid_form_with_all_required_fields(self, calendar):
        """Form with all required fields should be valid."""
        data = self.get_valid_form_data(calendar)
        form = JobForm(data=data)
        assert form.is_valid(), f"Form should be valid but has errors: {form.errors}"
    
    def test_missing_business_name_fails(self, calendar):
        """Form without business_name should be invalid."""
        data = self.get_valid_form_data(calendar)
        del data['business_name']
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'business_name' in form.errors
    
    def test_empty_business_name_fails(self, calendar):
        """Form with empty business_name should be invalid."""
        data = self.get_valid_form_data(calendar)
        data['business_name'] = ''
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'business_name' in form.errors
    
    def test_whitespace_only_business_name_fails(self, calendar):
        """Form with whitespace-only business_name should be invalid."""
        data = self.get_valid_form_data(calendar)
        data['business_name'] = '   '
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'business_name' in form.errors
    
    def test_missing_calendar_fails(self, calendar):
        """Form without calendar should be invalid."""
        data = self.get_valid_form_data(calendar)
        del data['calendar']
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'calendar' in form.errors
    
    def test_missing_start_dt_fails(self, calendar):
        """Form without start_dt should be invalid."""
        data = self.get_valid_form_data(calendar)
        del data['start_dt']
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'start_dt' in form.errors
    
    def test_empty_start_dt_fails(self, calendar):
        """Form with empty start_dt should be invalid."""
        data = self.get_valid_form_data(calendar)
        data['start_dt'] = ''
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'start_dt' in form.errors
    
    def test_missing_end_dt_fails(self, calendar):
        """Form without end_dt should be invalid."""
        data = self.get_valid_form_data(calendar)
        del data['end_dt']
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'end_dt' in form.errors
    
    def test_empty_end_dt_fails(self, calendar):
        """Form with empty end_dt should be invalid."""
        data = self.get_valid_form_data(calendar)
        data['end_dt'] = ''
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'end_dt' in form.errors
    
    def test_form_save_does_not_create_job_when_invalid(self, calendar):
        """Ensure form.save() is not called when form is invalid."""
        data = self.get_valid_form_data(calendar)
        data['business_name'] = ''  # Make it invalid
        
        initial_count = Job.objects.count()
        form = JobForm(data=data)
        
        assert not form.is_valid()
        # Attempting to save an invalid form should raise an error
        with pytest.raises(ValueError):
            form.save()
        
        # No new job should be created
        assert Job.objects.count() == initial_count


@pytest.mark.django_db
class TestJobFormYearValidation:
    """Test year range validation in JobForm.clean()."""
    
    def get_valid_form_data(self, calendar):
        """Return valid form data."""
        now = timezone.now()
        return {
            'calendar': calendar.id,
            'business_name': 'Test Business',
            'start_dt': now.strftime('%Y-%m-%dT%H:%M'),
            'end_dt': (now + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M'),
            'all_day': False,
            'status': 'uncompleted',
        }
    
    def test_valid_form_passes(self, calendar):
        """Form with valid dates should be valid."""
        data = self.get_valid_form_data(calendar)
        form = JobForm(data=data)
        assert form.is_valid(), form.errors
    
    def test_start_year_too_old_fails(self, calendar):
        """Form with start year before MIN_VALID_YEAR should be invalid."""
        data = self.get_valid_form_data(calendar)
        data['start_dt'] = '1999-06-15T10:00'
        data['end_dt'] = '1999-06-15T12:00'
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'start_dt' in form.errors
        assert str(MIN_VALID_YEAR) in str(form.errors['start_dt'])
    
    def test_start_year_too_far_future_fails(self, calendar):
        """Form with start year after MAX_VALID_YEAR should be invalid."""
        data = self.get_valid_form_data(calendar)
        data['start_dt'] = '2101-06-15T10:00'
        data['end_dt'] = '2101-06-15T12:00'
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'start_dt' in form.errors
        assert str(MAX_VALID_YEAR) in str(form.errors['start_dt'])
    
    def test_end_year_too_far_future_fails(self, calendar):
        """Form with end year after MAX_VALID_YEAR should be invalid."""
        data = self.get_valid_form_data(calendar)
        now = timezone.now()
        data['start_dt'] = now.strftime('%Y-%m-%dT%H:%M')
        data['end_dt'] = '2101-06-15T12:00'
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'end_dt' in form.errors
        assert str(MAX_VALID_YEAR) in str(form.errors['end_dt'])


@pytest.mark.django_db
class TestJobFormSpanValidation:
    """Test job span validation in JobForm.clean()."""
    
    def get_valid_form_data(self, calendar):
        """Return valid form data."""
        now = timezone.now()
        return {
            'calendar': calendar.id,
            'business_name': 'Test Business',
            'start_dt': now.strftime('%Y-%m-%dT%H:%M'),
            'end_dt': (now + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M'),
            'all_day': False,
            'status': 'uncompleted',
        }
    
    def test_span_exceeds_max_fails(self, calendar):
        """Form with span exceeding MAX_JOB_SPAN_DAYS should be invalid."""
        now = timezone.now()
        end = now + timedelta(days=MAX_JOB_SPAN_DAYS + 10)
        data = self.get_valid_form_data(calendar)
        data['start_dt'] = now.strftime('%Y-%m-%dT%H:%M')
        data['end_dt'] = end.strftime('%Y-%m-%dT%H:%M')
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'end_dt' in form.errors
        assert str(MAX_JOB_SPAN_DAYS) in str(form.errors['end_dt'])
    
    def test_max_span_passes(self, calendar):
        """Form with span exactly at MAX_JOB_SPAN_DAYS should be valid."""
        now = timezone.now()
        end = now + timedelta(days=MAX_JOB_SPAN_DAYS)
        data = self.get_valid_form_data(calendar)
        data['start_dt'] = now.strftime('%Y-%m-%dT%H:%M')
        data['end_dt'] = end.strftime('%Y-%m-%dT%H:%M')
        form = JobForm(data=data)
        assert form.is_valid(), form.errors


@pytest.mark.django_db
class TestJobFormDateOrderValidation:
    """Test that end date must be after start date in form."""
    
    def get_valid_form_data(self, calendar):
        """Return valid form data."""
        now = timezone.now()
        return {
            'calendar': calendar.id,
            'business_name': 'Test Business',
            'start_dt': now.strftime('%Y-%m-%dT%H:%M'),
            'end_dt': (now + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M'),
            'all_day': False,
            'status': 'uncompleted',
        }
    
    def test_end_before_start_fails(self, calendar):
        """Form with end before start should be invalid."""
        now = timezone.now()
        data = self.get_valid_form_data(calendar)
        data['start_dt'] = now.strftime('%Y-%m-%dT%H:%M')
        data['end_dt'] = (now - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
        form = JobForm(data=data)
        assert not form.is_valid()
        assert 'end_dt' in form.errors

