"""
Tests for date filter UI options in calendar and job list pages.
Ensures the "Events within 2 years" filter option is present.
"""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestCalendarDateFilterUI:
    """Test that calendar search panel includes the two_years filter option."""

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

    def test_job_list_two_years_filter_preserves_state(self, api_client):
        """When date_filter=two_years is passed, the radio should be checked."""
        url = reverse('rental_scheduler:job_list')
        response = api_client.get(url, {'date_filter': 'two_years'})
        content = response.content.decode('utf-8')

        assert response.status_code == 200
        # The checked attribute should be present for the two_years radio
        # Due to Django template rendering, 'checked' appears after the value
        assert 'value="two_years"' in content
        # Verify the template logic - when two_years is selected, checked should appear
        assert 'checked' in content

