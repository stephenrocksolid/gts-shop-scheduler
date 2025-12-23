"""
Tests for partial view endpoints that render templates.

These tests ensure that template compilation succeeds and basic rendering works.
This catches template syntax errors (like missing spaces around ==) at test time.
"""
import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from datetime import timedelta


# Note: StaticFilesStorage override is now handled globally in root conftest.py


@pytest.mark.django_db
class TestJobCreatePartial:
    """Test the job_create_partial view renders without errors."""
    
    def test_new_job_form_renders_with_date(self, api_client, calendar):
        """GET /jobs/new/partial/?date=... should return 200 and contain form fields."""
        url = reverse('rental_scheduler:job_create_partial')
        response = api_client.get(url, {'date': '2026-01-12'})
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        # Verify key form fields are present
        assert 'name="start_dt"' in content
        assert 'name="end_dt"' in content
        assert 'name="business_name"' in content
        assert 'name="calendar"' in content
    
    def test_new_job_form_renders_without_date(self, api_client, calendar):
        """GET /jobs/new/partial/ without date param should still return 200."""
        url = reverse('rental_scheduler:job_create_partial')
        response = api_client.get(url)
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        # Verify form fields are present
        assert 'name="start_dt"' in content
        assert 'name="business_name"' in content
    
    def test_new_job_form_preselects_default_calendar(self, api_client, calendar):
        """GET /jobs/new/partial/ without calendar param should preselect first active calendar."""
        url = reverse('rental_scheduler:job_create_partial')
        response = api_client.get(url)
        
        assert response.status_code == 200
        # Access form from context to verify calendar is preselected
        form = response.context['form']
        assert form['calendar'].value() == calendar.id, f"Expected calendar {calendar.id}, got {form['calendar'].value()}"
    
    def test_edit_job_form_renders(self, api_client, job):
        """GET /jobs/new/partial/?edit=<id> should return 200 and show job data."""
        url = reverse('rental_scheduler:job_create_partial')
        response = api_client.get(url, {'edit': job.id})
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        # Verify job data is in the form
        assert job.business_name in content
        assert 'name="start_dt"' in content
    
    def test_edit_job_with_call_reminder(self, api_client, calendar):
        """GET /jobs/new/partial/?edit=<id> for job with call reminder should render."""
        from rental_scheduler.models import Job
        
        now = timezone.now()
        job = Job.objects.create(
            calendar=calendar,
            business_name="Call Reminder Test",
            start_dt=now + timedelta(days=30),
            end_dt=now + timedelta(days=30, hours=2),
            all_day=False,
            status='uncompleted',
            has_call_reminder=True,
            call_reminder_weeks_prior=2,
        )
        
        url = reverse('rental_scheduler:job_create_partial')
        response = api_client.get(url, {'edit': job.id})
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        # Verify call reminder section renders
        assert 'call-reminder-enabled' in content
        assert 'call_reminder_weeks_prior' in content
    
    def test_edit_job_with_recurrence_rule(self, api_client, calendar):
        """GET /jobs/new/partial/?edit=<id> for recurring job should render."""
        from rental_scheduler.models import Job
        
        now = timezone.now()
        job = Job.objects.create(
            calendar=calendar,
            business_name="Recurring Test",
            start_dt=now,
            end_dt=now + timedelta(hours=2),
            all_day=False,
            status='uncompleted',
        )
        # Create a recurrence rule
        job.create_recurrence_rule(
            recurrence_type='monthly',
            interval=1,
            count=5,
        )
        
        url = reverse('rental_scheduler:job_create_partial')
        response = api_client.get(url, {'edit': job.id})
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        # Verify recurrence section renders
        assert 'recurrence-type' in content


@pytest.mark.django_db
class TestCallReminderCreatePartial:
    """Test the call_reminder_create_partial view renders without errors."""
    
    def test_call_reminder_form_renders_with_date(self, api_client, calendar):
        """GET /call-reminders/new/partial/?date=... should return 200."""
        url = reverse('rental_scheduler:call_reminder_create_partial')
        response = api_client.get(url, {'date': '2026-01-12'})
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        # Verify form fields are present
        assert 'name="reminder_date"' in content
        assert 'name="calendar"' in content
        assert 'name="notes"' in content
    
    def test_call_reminder_form_renders_with_calendar(self, api_client, calendar):
        """GET /call-reminders/new/partial/?calendar=... should pre-select calendar."""
        url = reverse('rental_scheduler:call_reminder_create_partial')
        response = api_client.get(url, {'date': '2026-01-12', 'calendar': calendar.id})
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        # Form should render successfully
        assert 'name="reminder_date"' in content
    
    def test_call_reminder_form_preselects_default_calendar(self, api_client, calendar):
        """GET /call-reminders/new/partial/ without calendar param should preselect first active calendar."""
        url = reverse('rental_scheduler:call_reminder_create_partial')
        response = api_client.get(url, {'date': '2026-01-12'})
        
        assert response.status_code == 200
        # Access form from context to verify calendar is preselected
        form = response.context['form']
        assert form['calendar'].value() == calendar.id, f"Expected calendar {calendar.id}, got {form['calendar'].value()}"


@pytest.mark.django_db
class TestJobDetailPartial:
    """Test the job_detail_partial view.
    """
    
    def test_job_detail_renders(self, api_client, job):
        """GET /jobs/<pk>/partial/ should return 200."""
        url = reverse('rental_scheduler:job_detail_partial', args=[job.id])
        response = api_client.get(url)
        
        assert response.status_code == 200
    
    def test_job_detail_returns_404_for_missing_job(self, api_client):
        """GET /jobs/<pk>/partial/ with invalid pk should return 404."""
        url = reverse('rental_scheduler:job_detail_partial', args=[99999])
        response = api_client.get(url)
        
        assert response.status_code == 404


@pytest.mark.django_db
class TestJobCreateSubmitValidation:
    """Test that job_create_submit properly validates required fields and rejects invalid submissions."""
    
    def get_valid_form_data(self, calendar):
        """Return valid form data for job creation."""
        now = timezone.now()
        return {
            'calendar': calendar.id,
            'business_name': 'Test Business',
            'start_dt': now.strftime('%Y-%m-%d'),
            'end_dt': now.strftime('%Y-%m-%d'),
            'all_day': 'on',
            'status': 'uncompleted',
        }
    
    def test_valid_submission_returns_success(self, api_client, calendar):
        """POST with all required fields should return success (200)."""
        from rental_scheduler.models import Job
        
        url = reverse('rental_scheduler:job_create_submit')
        data = self.get_valid_form_data(calendar)
        
        initial_count = Job.objects.count()
        response = api_client.post(url)
        
        # Note: We need to test with HTMX headers for full compatibility
        response = api_client.post(url, data)
        
        assert response.status_code == 200
        assert Job.objects.count() == initial_count + 1
    
    def test_missing_business_name_returns_400(self, api_client, calendar):
        """POST without business_name should return 400 and not create job."""
        from rental_scheduler.models import Job
        
        url = reverse('rental_scheduler:job_create_submit')
        data = self.get_valid_form_data(calendar)
        del data['business_name']
        
        initial_count = Job.objects.count()
        response = api_client.post(url, data)
        
        assert response.status_code == 400
        assert Job.objects.count() == initial_count
        assert 'business_name' in response.content.decode('utf-8').lower() or 'required' in response.content.decode('utf-8').lower()
    
    def test_empty_business_name_returns_400(self, api_client, calendar):
        """POST with empty business_name should return 400 and not create job."""
        from rental_scheduler.models import Job
        
        url = reverse('rental_scheduler:job_create_submit')
        data = self.get_valid_form_data(calendar)
        data['business_name'] = ''
        
        initial_count = Job.objects.count()
        response = api_client.post(url, data)
        
        assert response.status_code == 400
        assert Job.objects.count() == initial_count
    
    def test_whitespace_only_business_name_returns_400(self, api_client, calendar):
        """POST with whitespace-only business_name should return 400 and not create job."""
        from rental_scheduler.models import Job
        
        url = reverse('rental_scheduler:job_create_submit')
        data = self.get_valid_form_data(calendar)
        data['business_name'] = '   '
        
        initial_count = Job.objects.count()
        response = api_client.post(url, data)
        
        assert response.status_code == 400
        assert Job.objects.count() == initial_count
    
    def test_missing_calendar_returns_400(self, api_client, calendar):
        """POST without calendar should return 400 and not create job."""
        from rental_scheduler.models import Job
        
        url = reverse('rental_scheduler:job_create_submit')
        data = self.get_valid_form_data(calendar)
        del data['calendar']
        
        initial_count = Job.objects.count()
        response = api_client.post(url, data)
        
        assert response.status_code == 400
        assert Job.objects.count() == initial_count
    
    def test_missing_start_dt_returns_400(self, api_client, calendar):
        """POST without start_dt should return 400 and not create job."""
        from rental_scheduler.models import Job
        
        url = reverse('rental_scheduler:job_create_submit')
        data = self.get_valid_form_data(calendar)
        del data['start_dt']
        
        initial_count = Job.objects.count()
        response = api_client.post(url, data)
        
        assert response.status_code == 400
        assert Job.objects.count() == initial_count
    
    def test_missing_end_dt_returns_400(self, api_client, calendar):
        """POST without end_dt should return 400 and not create job."""
        from rental_scheduler.models import Job
        
        url = reverse('rental_scheduler:job_create_submit')
        data = self.get_valid_form_data(calendar)
        del data['end_dt']
        
        initial_count = Job.objects.count()
        response = api_client.post(url, data)
        
        assert response.status_code == 400
        assert Job.objects.count() == initial_count
    
    def test_invalid_calendar_id_returns_400(self, api_client, calendar):
        """POST with invalid calendar ID should return 400 and not create job."""
        from rental_scheduler.models import Job
        
        url = reverse('rental_scheduler:job_create_submit')
        data = self.get_valid_form_data(calendar)
        data['calendar'] = 99999  # Non-existent calendar
        
        initial_count = Job.objects.count()
        response = api_client.post(url, data)
        
        assert response.status_code == 400
        assert Job.objects.count() == initial_count

