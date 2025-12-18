"""
Tests for calendar template guardrails injection.
Ensures window.calendarConfig.guardrails is properly injected.
"""
import pytest
import json
import re
from django.test import Client
from django.urls import reverse
from rental_scheduler.constants import (
    MIN_VALID_YEAR,
    MAX_VALID_YEAR,
    MAX_JOB_SPAN_DAYS,
    WARN_DAYS_IN_FUTURE,
    WARN_DAYS_IN_PAST,
    WARN_JOB_SPAN_DAYS,
    get_guardrails_for_frontend,
)


@pytest.mark.django_db
class TestCalendarTemplateGuardrails:
    """Test that calendar template injects guardrails into JavaScript."""
    
    def test_calendar_page_loads(self, api_client):
        """Calendar page should load successfully."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        assert response.status_code == 200
    
    def test_calendar_config_present(self, api_client):
        """window.calendarConfig should be present in the page."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')
        
        assert 'window.calendarConfig' in content
    
    def test_guardrails_present_in_config(self, api_client):
        """guardrails key should be present in calendarConfig."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')
        
        # Look for guardrails in the config
        assert 'guardrails' in content
    
    def test_guardrails_contains_expected_values(self, api_client):
        """guardrails should contain the expected threshold values."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')
        
        # Extract the guardrails JSON from the page
        # Look for pattern like: guardrails: JSON.parse('{"minValidYear":2000,...}')
        # The JSON is escaped for embedding in JS, so we need to handle that
        match = re.search(r"guardrails:\s*JSON\.parse\(['\"](.+?)['\"]\)", content)
        
        if not match:
            # Fallback: try to find the guardrails value directly if not using JSON.parse
            match = re.search(r'"guardrails":\s*(\{[^}]+\})', content)
        
        assert match, f"Could not find guardrails JSON in page. Content snippet: {content[1000:1500]}"
        
        guardrails_json = match.group(1)
        # Unescape the JSON string (handle escaped quotes)
        guardrails_json = guardrails_json.replace('\\u0022', '"').replace('\\"', '"')
        
        try:
            guardrails = json.loads(guardrails_json)
        except json.JSONDecodeError:
            # If that fails, the guardrails might be inline - check if values are present
            assert str(MIN_VALID_YEAR) in content, f"MIN_VALID_YEAR {MIN_VALID_YEAR} not in content"
            assert str(MAX_VALID_YEAR) in content, f"MAX_VALID_YEAR {MAX_VALID_YEAR} not in content"
            return
        
        # Verify values match constants
        assert guardrails['minValidYear'] == MIN_VALID_YEAR
        assert guardrails['maxValidYear'] == MAX_VALID_YEAR
        assert guardrails['maxJobSpanDays'] == MAX_JOB_SPAN_DAYS
        assert guardrails['warnDaysInFuture'] == WARN_DAYS_IN_FUTURE
        assert guardrails['warnDaysInPast'] == WARN_DAYS_IN_PAST
        assert guardrails['warnJobSpanDays'] == WARN_JOB_SPAN_DAYS
    
    def test_guardrails_matches_helper_function(self, api_client):
        """guardrails in template should match get_guardrails_for_frontend()."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')
        
        # Get expected values
        expected = get_guardrails_for_frontend()
        
        # Check that all expected values are present in the content
        for key, value in expected.items():
            # Check for camelCase key in content
            assert key in content, f"Key '{key}' not found in calendar page"
            # Check for value
            assert str(value) in content, f"Value '{value}' for key '{key}' not found in calendar page"


@pytest.mark.django_db
class TestCalendarTemplateOtherConfig:
    """Test other calendarConfig properties are present."""
    
    def test_events_url_present(self, api_client):
        """eventsUrl should be present in config."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')
        
        assert 'eventsUrl' in content
    
    def test_csrf_token_present(self, api_client):
        """csrfToken should be present in config."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')
        
        assert 'csrfToken' in content
    
    def test_calendars_present(self, api_client):
        """calendars should be present in config."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')
        
        assert 'calendars' in content


@pytest.mark.django_db
class TestCalendarSearchPanelDropdown:
    """Test the calendar search panel's calendar dropdown elements."""
    
    def test_search_calendar_dropdown_present(self, api_client):
        """Search calendar dropdown container should be present."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')
        
        assert 'id="search-calendar-dropdown"' in content
    
    def test_search_calendar_all_checkbox_present(self, api_client):
        """Search calendar 'All Calendars' select-all checkbox should be present."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')
        
        assert 'id="search-calendar-all-checkbox"' in content
    
    def test_search_calendar_dropdown_btn_present(self, api_client):
        """Search calendar dropdown button should be present."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')
        
        assert 'id="search-calendar-dropdown-btn"' in content
    
    def test_search_calendar_selected_text_present(self, api_client):
        """Search calendar selected text span should be present."""
        url = reverse('rental_scheduler:calendar')
        response = api_client.get(url)
        content = response.content.decode('utf-8')
        
        assert 'id="search-calendar-selected-text"' in content

