"""
Tests for recurring API endpoint validation.
Ensures date validation is applied to recurring create/update endpoints.
"""
import pytest
import json
from datetime import datetime, timedelta
from django.test import Client
from django.utils import timezone
from django.urls import reverse
from rental_scheduler.models import Job, Calendar
from rental_scheduler.constants import MIN_VALID_YEAR, MAX_VALID_YEAR, MAX_JOB_SPAN_DAYS


@pytest.mark.django_db
class TestRecurringCreateAPIValidation:
    """Test validation in job_create_api_recurring endpoint."""
    
    def get_valid_job_data(self, calendar):
        """Return valid job creation data."""
        now = timezone.now()
        return {
            'business_name': 'Test Business',
            'contact_name': 'Test Contact',
            'calendar_id': calendar.id,
            'start': now.isoformat(),
            'end': (now + timedelta(hours=2)).isoformat(),
            'all_day': False,
        }
    
    def test_valid_data_creates_job(self, api_client, calendar):
        """Valid data should create a job successfully."""
        data = self.get_valid_job_data(calendar)
        
        url = reverse('rental_scheduler:job_create_api')
        response = api_client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
        )
        
        assert response.status_code == 200
        result = response.json()
        assert 'id' in result or 'job_id' in result
    
    def test_start_year_too_old_rejected(self, api_client, calendar):
        """Start year before MIN_VALID_YEAR should be rejected."""
        data = self.get_valid_job_data(calendar)
        data['start'] = '1999-06-15T10:00:00'
        data['end'] = '1999-06-15T12:00:00'
        
        url = reverse('rental_scheduler:job_create_api')
        response = api_client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
        )
        
        assert response.status_code == 400
        result = response.json()
        assert 'error' in result
        assert str(MIN_VALID_YEAR) in result['error']
    
    def test_start_year_too_far_future_rejected(self, api_client, calendar):
        """Start year after MAX_VALID_YEAR should be rejected."""
        data = self.get_valid_job_data(calendar)
        data['start'] = '2101-06-15T10:00:00'
        data['end'] = '2101-06-15T12:00:00'
        
        url = reverse('rental_scheduler:job_create_api')
        response = api_client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
        )
        
        assert response.status_code == 400
        result = response.json()
        assert 'error' in result
        assert str(MAX_VALID_YEAR) in result['error']
    
    def test_span_exceeds_max_rejected(self, api_client, calendar):
        """Job span exceeding MAX_JOB_SPAN_DAYS should be rejected."""
        now = timezone.now()
        data = self.get_valid_job_data(calendar)
        data['start'] = now.isoformat()
        data['end'] = (now + timedelta(days=MAX_JOB_SPAN_DAYS + 10)).isoformat()
        
        url = reverse('rental_scheduler:job_create_api')
        response = api_client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
        )
        
        assert response.status_code == 400
        result = response.json()
        assert 'error' in result
        assert str(MAX_JOB_SPAN_DAYS) in result['error']


@pytest.mark.django_db
class TestRecurringUpdateAPIValidation:
    """Test validation in job_update_api_recurring endpoint."""
    
    def test_update_with_invalid_year_rejected(self, api_client, job):
        """Updating job with invalid year should be rejected."""
        url = reverse('rental_scheduler:job_update_api', args=[job.id])
        
        response = api_client.post(
            url,
            data=json.dumps({
                'start': '1999-06-15T10:00:00',
                'end': '1999-06-15T12:00:00',
            }),
            content_type='application/json',
        )
        
        assert response.status_code == 400
        result = response.json()
        assert 'error' in result
        assert str(MIN_VALID_YEAR) in result['error']
    
    def test_update_with_excessive_span_rejected(self, api_client, job):
        """Updating job with excessive span should be rejected."""
        now = timezone.now()
        url = reverse('rental_scheduler:job_update_api', args=[job.id])
        
        response = api_client.post(
            url,
            data=json.dumps({
                'start': now.isoformat(),
                'end': (now + timedelta(days=MAX_JOB_SPAN_DAYS + 50)).isoformat(),
            }),
            content_type='application/json',
        )
        
        assert response.status_code == 400
        result = response.json()
        assert 'error' in result
        assert str(MAX_JOB_SPAN_DAYS) in result['error']
    
    def test_valid_update_succeeds(self, api_client, job):
        """Valid update should succeed."""
        now = timezone.now()
        url = reverse('rental_scheduler:job_update_api', args=[job.id])
        
        response = api_client.post(
            url,
            data=json.dumps({
                'business_name': 'Updated Business Name',
            }),
            content_type='application/json',
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result.get('status') == 'success' or 'id' in result or 'job_id' in result

