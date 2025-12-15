"""
Playwright E2E smoke tests for calendar page.
Tests JS behavior, guardrails injection, and basic functionality.
"""
import pytest
import re
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
    }


class TestCalendarPageLoads:
    """Test that the calendar page loads correctly."""
    
    def test_calendar_page_loads_without_errors(self, page: Page, server_url):
        """Calendar page should load without JS errors."""
        errors = []
        
        # Capture page errors
        page.on("pageerror", lambda err: errors.append(str(err)))
        
        # Navigate to calendar
        page.goto(f"{server_url}/")
        
        # Wait for calendar to be visible
        page.wait_for_selector("#calendar", timeout=10000)
        
        # Check for critical JS errors
        critical_errors = [e for e in errors if 
            "Unexpected end of JSON" in e or 
            "removeChild" in e or
            "Cannot read properties of null" in e
        ]
        
        assert len(critical_errors) == 0, f"JS errors found: {critical_errors}"
    
    def test_calendar_renders(self, page: Page, server_url):
        """Calendar should render with FullCalendar structure."""
        page.goto(f"{server_url}/")
        
        # Wait for FullCalendar to initialize
        page.wait_for_selector(".fc", timeout=10000)
        
        # Check calendar structure exists
        expect(page.locator(".fc-header-toolbar")).to_be_visible()
        expect(page.locator(".fc-daygrid")).to_be_visible()


class TestGuardrailsInjection:
    """Test that guardrails are properly injected into JS."""
    
    def test_calendar_config_exists(self, page: Page, server_url):
        """window.calendarConfig should exist."""
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        
        result = page.evaluate("typeof window.calendarConfig")
        assert result == "object", "window.calendarConfig should be an object"
    
    def test_guardrails_object_exists(self, page: Page, server_url):
        """window.calendarConfig.guardrails should exist."""
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        
        result = page.evaluate("typeof window.calendarConfig.guardrails")
        assert result == "object", "guardrails should be an object"
    
    def test_guardrails_has_expected_keys(self, page: Page, server_url):
        """guardrails should have all expected keys."""
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        
        guardrails = page.evaluate("window.calendarConfig.guardrails")
        
        expected_keys = ['minValidYear', 'maxValidYear', 'maxJobSpanDays', 
                        'warnDaysInFuture', 'warnJobSpanDays']
        
        for key in expected_keys:
            assert key in guardrails, f"Missing key: {key}"
    
    def test_guardrails_values_are_numbers(self, page: Page, server_url):
        """guardrails values should be numbers."""
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        
        guardrails = page.evaluate("window.calendarConfig.guardrails")
        
        for key, value in guardrails.items():
            assert isinstance(value, (int, float)), f"{key} should be a number, got {type(value)}"
    
    def test_guardrails_min_year_is_2000(self, page: Page, server_url):
        """minValidYear should be 2000."""
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        
        min_year = page.evaluate("window.calendarConfig.guardrails.minValidYear")
        assert min_year == 2000


class TestEventsAPIFetch:
    """Test that events API is fetched correctly."""
    
    def test_events_api_returns_json(self, page: Page, server_url):
        """Events API should return valid JSON."""
        responses = []
        
        def handle_response(response):
            if "/api/job-calendar-data/" in response.url:
                responses.append({
                    "url": response.url,
                    "status": response.status,
                    "content_type": response.headers.get("content-type", ""),
                })
        
        page.on("response", handle_response)
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        
        # Wait a bit for the API call to complete
        page.wait_for_timeout(2000)
        
        # Should have at least one API call
        api_responses = [r for r in responses if "/api/job-calendar-data/" in r["url"]]
        assert len(api_responses) > 0, "Expected at least one API call"
        
        # First response should be successful JSON
        first_response = api_responses[0]
        assert first_response["status"] == 200
        assert "application/json" in first_response["content_type"]
    
    def test_events_api_not_huge(self, page: Page, server_url):
        """Events API response should not be excessively large."""
        response_sizes = []
        
        def handle_response(response):
            if "/api/job-calendar-data/" in response.url and response.status == 200:
                try:
                    body = response.body()
                    response_sizes.append(len(body))
                except:
                    pass
        
        page.on("response", handle_response)
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        page.wait_for_timeout(2000)
        
        if response_sizes:
            # Response should be < 1MB (reasonable for a month view)
            max_size = max(response_sizes)
            assert max_size < 1_000_000, f"Response too large: {max_size} bytes"


class TestNoConsoleErrors:
    """Test that there are no critical console errors."""
    
    def test_no_json_parse_errors(self, page: Page, server_url):
        """Should not have JSON parse errors."""
        console_errors = []
        
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        page.wait_for_timeout(3000)  # Wait for any async operations
        
        json_errors = [e for e in console_errors if "JSON" in e and ("parse" in e.lower() or "unexpected" in e.lower())]
        assert len(json_errors) == 0, f"JSON errors found: {json_errors}"
    
    def test_no_remove_child_errors(self, page: Page, server_url):
        """Should not have removeChild errors (popover fix)."""
        console_errors = []
        page_errors = []
        
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        page.wait_for_timeout(3000)
        
        all_errors = console_errors + page_errors
        remove_child_errors = [e for e in all_errors if "removeChild" in e]
        assert len(remove_child_errors) == 0, f"removeChild errors found: {remove_child_errors}"


class TestJobPanel:
    """Test job panel functionality (basic smoke test)."""
    
    def test_can_open_add_job_panel(self, page: Page, server_url):
        """Should be able to open the add job panel."""
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        
        # Look for add job button in toolbar
        add_button = page.locator(".fc-addJobButton-button")
        
        if add_button.count() > 0:
            add_button.click()
            
            # Wait for panel to appear
            page.wait_for_selector("#job-panel", timeout=5000)
            expect(page.locator("#job-panel")).to_be_visible()
    
    def test_job_panel_has_date_inputs(self, page: Page, server_url):
        """Job panel should have start and end date inputs."""
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        
        # Open add job panel
        add_button = page.locator(".fc-addJobButton-button")
        
        if add_button.count() > 0:
            add_button.click()
            page.wait_for_selector("#job-panel", timeout=5000)
            
            # Wait for form to load
            page.wait_for_timeout(1000)
            
            # Check for date inputs
            start_input = page.locator("input[name='start_dt']")
            end_input = page.locator("input[name='end_dt']")
            
            # At least one of these should exist
            has_dates = start_input.count() > 0 or end_input.count() > 0
            assert has_dates, "Job panel should have date inputs"

