"""
Tests for date filter UI options in calendar and job list pages.
Ensures key date filter options are present.
"""
import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from rental_scheduler.models import Job


@pytest.mark.django_db
class TestCalendarDateFilterUI:
    """Test that calendar search panel includes expected date filter options."""

    def test_calendar_page_has_two_years_filter_value(self, api_client):
        """Calendar search panel should have a radio with value='two_years'."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert 'value="two_years"' in content

    def test_calendar_page_has_two_years_filter_label(self, api_client):
        """Calendar search panel should display 'Events within 2 years' label."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert 'Events within 2 years' in content

    def test_calendar_page_has_past_filter_value(self, api_client):
        """Calendar search panel should have a radio with value='past'."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert 'value="past"' in content


@pytest.mark.django_db
class TestJobListDateFilterUI:
    """Test that job list filter bar includes the two_years filter option."""

    def test_job_list_page_has_two_years_filter_value(self, api_client):
        """Job list filter bar should have a radio with value='two_years'."""
        url = reverse('rental_scheduler:job_list')
        response = api_client.get(url)
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert 'value="two_years"' in content

    def test_job_list_page_has_two_years_filter_label(self, api_client):
        """Job list filter bar should display 'Events within 2 years' label."""
        url = reverse('rental_scheduler:job_list')
        response = api_client.get(url)
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert 'Events within 2 years' in content

    def test_job_list_page_has_past_filter_value(self, api_client):
        """Job list filter bar should have a radio with value='past'."""
        url = reverse('rental_scheduler:job_list')
        response = api_client.get(url)
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert 'value="past"' in content

    def test_job_list_page_has_past_filter_label(self, api_client):
        """Job list filter bar should display 'Past Events' label."""
        url = reverse('rental_scheduler:job_list')
        response = api_client.get(url)
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert 'Past Events' in content

    def test_job_list_two_years_filter_preserves_state(self, api_client):
        """When date_filter=two_years is passed, the radio should be checked."""
        url = reverse('rental_scheduler:job_list')
        response = api_client.get(url, {'date_filter': 'two_years'})
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert re.search(r'value="two_years"[\s\S]*?\bchecked\b', content)

    def test_job_list_past_filter_preserves_state(self, api_client):
        """When date_filter=past is passed, the radio should be checked."""
        url = reverse('rental_scheduler:job_list')
        response = api_client.get(url, {'date_filter': 'past'})
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert re.search(r'value="past"[\s\S]*?\bchecked\b', content)


@pytest.mark.django_db
class TestJobListSectionHeaders:
    """Test that Upcoming/Past section headers appear only for All Events.
    
    Note: 'Past Events' also appears in the filter bar radio label, so we use
    'Upcoming Events' (unique to section headers) and check for specific
    section header CSS classes when testing for Past header presence.
    """

    # CSS class pattern unique to the Past section header row
    PAST_SECTION_HEADER = 'bg-gray-100 border-t-2 border-gray-300'
    # CSS class pattern unique to the Upcoming section header row
    UPCOMING_SECTION_HEADER = 'bg-blue-50 border-t-2 border-blue-200'

    def test_all_events_shows_section_headers(self, api_client, calendar):
        """With date_filter=all (default), Upcoming and Past headers should appear."""
        url = reverse('rental_scheduler:job_list')
        now = timezone.now()

        # Create a future job
        Job.objects.create(
            calendar=calendar,
            business_name="FUTURE_JOB",
            start_dt=now + timedelta(days=5),
            end_dt=now + timedelta(days=5, hours=1),
            all_day=False,
            status="uncompleted",
        )
        # Create a past job
        Job.objects.create(
            calendar=calendar,
            business_name="PAST_JOB",
            start_dt=now - timedelta(days=5),
            end_dt=now - timedelta(days=5, hours=-1),
            all_day=False,
            status="uncompleted",
        )

        response = api_client.get(url)  # default date_filter=all
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert self.UPCOMING_SECTION_HEADER in content
        assert self.PAST_SECTION_HEADER in content

    def test_future_filter_no_section_headers(self, api_client, calendar):
        """With date_filter=future, section headers should NOT appear."""
        url = reverse('rental_scheduler:job_list')
        now = timezone.now()

        Job.objects.create(
            calendar=calendar,
            business_name="FUTURE_JOB",
            start_dt=now + timedelta(days=5),
            end_dt=now + timedelta(days=5, hours=1),
            all_day=False,
            status="uncompleted",
        )

        response = api_client.get(url, {'date_filter': 'future'})
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert self.UPCOMING_SECTION_HEADER not in content
        assert self.PAST_SECTION_HEADER not in content

    def test_past_filter_no_section_headers(self, api_client, calendar):
        """With date_filter=past, section headers should NOT appear."""
        url = reverse('rental_scheduler:job_list')
        now = timezone.now()

        Job.objects.create(
            calendar=calendar,
            business_name="PAST_JOB",
            start_dt=now - timedelta(days=5),
            end_dt=now - timedelta(days=5, hours=-1),
            all_day=False,
            status="uncompleted",
        )

        response = api_client.get(url, {'date_filter': 'past'})
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert self.UPCOMING_SECTION_HEADER not in content
        assert self.PAST_SECTION_HEADER not in content

    def test_two_years_filter_no_section_headers(self, api_client, calendar):
        """With date_filter=two_years, section headers should NOT appear."""
        url = reverse('rental_scheduler:job_list')
        now = timezone.now()

        Job.objects.create(
            calendar=calendar,
            business_name="FUTURE_JOB",
            start_dt=now + timedelta(days=10),
            end_dt=now + timedelta(days=10, hours=1),
            all_day=False,
            status="uncompleted",
        )

        response = api_client.get(url, {'date_filter': 'two_years'})
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert self.UPCOMING_SECTION_HEADER not in content
        assert self.PAST_SECTION_HEADER not in content

    def test_all_events_only_future_shows_upcoming_header(self, api_client, calendar):
        """With only future jobs, only Upcoming header should appear."""
        url = reverse('rental_scheduler:job_list')
        now = timezone.now()

        Job.objects.create(
            calendar=calendar,
            business_name="FUTURE_JOB",
            start_dt=now + timedelta(days=5),
            end_dt=now + timedelta(days=5, hours=1),
            all_day=False,
            status="uncompleted",
        )

        response = api_client.get(url)  # default date_filter=all
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert self.UPCOMING_SECTION_HEADER in content
        assert self.PAST_SECTION_HEADER not in content

    def test_all_events_only_past_shows_past_header(self, api_client, calendar):
        """With only past jobs, only Past header should appear."""
        url = reverse('rental_scheduler:job_list')
        now = timezone.now()

        Job.objects.create(
            calendar=calendar,
            business_name="PAST_JOB",
            start_dt=now - timedelta(days=5),
            end_dt=now - timedelta(days=5, hours=-1),
            all_day=False,
            status="uncompleted",
        )

        response = api_client.get(url)  # default date_filter=all
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        assert self.UPCOMING_SECTION_HEADER not in content
        assert self.PAST_SECTION_HEADER in content
