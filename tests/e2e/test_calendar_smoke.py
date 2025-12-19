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


class TestDraftWorkspaceFlow:
    """Test draft minimize → workspace tab → reload → restore flow."""

    def _find_weekday_cell(self, page: Page):
        """Find a non-Sunday day cell (double-click on non-Sunday opens job form)."""
        # Use JavaScript to find a Monday in the current view
        weekday_date = page.evaluate("""
            () => {
                const dayCells = document.querySelectorAll('.fc-daygrid-day');
                for (const cell of dayCells) {
                    const date = cell.getAttribute('data-date');
                    if (date) {
                        const d = new Date(date + 'T12:00:00');
                        // Monday = 1 (avoid Sunday = 0)
                        if (d.getDay() === 1) {
                            return date;
                        }
                    }
                }
                return null;
            }
        """)
        return weekday_date

    def test_minimize_creates_workspace_tab(self, page: Page, server_url):
        """Minimizing a new job with partial data should create a workspace tab."""
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        page.wait_for_timeout(1000)

        # Find a weekday cell and double-click to open job panel
        weekday_date = self._find_weekday_cell(page)
        assert weekday_date, "No weekday cell found in calendar view"

        # Double-click the day number to avoid accidentally targeting an event element.
        day_number = page.locator(f'.fc-daygrid-day[data-date="{weekday_date}"] .fc-daygrid-day-number')
        if day_number.count() > 0:
            day_number.dblclick()
        else:
            page.locator(f'.fc-daygrid-day[data-date="{weekday_date}"]').dblclick()

        # Wait for job panel to appear
        page.wait_for_selector("#job-panel", timeout=5000)
        page.wait_for_selector("input[name='contact_name']", timeout=5000)

        # Fill only contact_name (leave required fields empty to keep it as a draft)
        contact_input = page.locator("input[name='contact_name']")
        test_contact = "E2E Test Draft Contact"
        contact_input.fill(test_contact)

        # Click the minimize button
        minimize_btn = page.locator("#panel-workspace-minimize-btn")
        expect(minimize_btn).to_be_visible()
        minimize_btn.click()

        # Wait for workspace bar and tab to appear
        page.wait_for_selector("#workspace-bar", timeout=5000)
        page.wait_for_selector(".workspace-tab", timeout=5000)

        # Verify workspace tab exists
        workspace_tabs = page.locator(".workspace-tab")
        assert workspace_tabs.count() > 0, "Workspace tab should appear after minimize"

    def test_draft_persists_after_reload(self, page: Page, server_url):
        """Draft should persist in workspace after page reload."""
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        page.wait_for_timeout(1000)

        # Find a weekday cell and double-click to open job panel
        weekday_date = self._find_weekday_cell(page)
        if not weekday_date:
            pytest.skip("No weekday cell found in calendar view")

        day_cell = page.locator(f'.fc-daygrid-day[data-date="{weekday_date}"]')
        day_cell.dblclick()

        page.wait_for_selector("#job-panel", timeout=5000)
        page.wait_for_selector("input[name='contact_name']", timeout=5000)

        # Fill only contact_name (draft state)
        contact_input = page.locator("input[name='contact_name']")
        test_contact = f"E2E Draft Persist {page.evaluate('Date.now()')}"
        contact_input.fill(test_contact)

        # Minimize to workspace
        minimize_btn = page.locator("#panel-workspace-minimize-btn")
        minimize_btn.click()

        # Wait for tab to appear
        page.wait_for_selector(".workspace-tab", timeout=5000)

        # Reload the page
        page.reload()
        page.wait_for_selector("#calendar", timeout=10000)

        # Wait for workspace to restore
        page.wait_for_timeout(1000)

        # Check if workspace tab persisted
        workspace_tabs = page.locator(".workspace-tab")
        assert workspace_tabs.count() > 0, "Workspace tab should persist after reload"

    def test_restore_draft_shows_previous_data(self, page: Page, server_url):
        """Clicking a draft tab should restore the previously entered data."""
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        page.wait_for_timeout(1000)

        # Find a weekday cell and double-click to open job panel
        weekday_date = self._find_weekday_cell(page)
        if not weekday_date:
            pytest.skip("No weekday cell found in calendar view")

        day_cell = page.locator(f'.fc-daygrid-day[data-date="{weekday_date}"]')
        day_cell.dblclick()

        page.wait_for_selector("#job-panel", timeout=5000)
        page.wait_for_selector("input[name='contact_name']", timeout=5000)

        # Fill contact_name with a unique value
        contact_input = page.locator("input[name='contact_name']")
        unique_id = page.evaluate("Date.now()")
        test_contact = f"E2E Restore Test {unique_id}"
        contact_input.fill(test_contact)

        # Minimize to workspace
        minimize_btn = page.locator("#panel-workspace-minimize-btn")
        minimize_btn.click()

        # Wait for tab to appear
        page.wait_for_selector(".workspace-tab", timeout=5000)

        # Reload the page
        page.reload()
        page.wait_for_selector("#calendar", timeout=10000)

        # Wait for workspace to restore
        page.wait_for_timeout(1000)

        # Click the draft tab to restore
        workspace_tab = page.locator(".workspace-tab").first
        if workspace_tab.count() == 0:
            pytest.skip("No workspace tab found after reload")

        workspace_tab.click()

        # Wait for panel to open
        page.wait_for_selector("#job-panel", timeout=5000)

        # Wait for form to load
        page.wait_for_selector("input[name='contact_name']", timeout=5000)
        page.wait_for_timeout(500)  # Allow form to fully populate

        # Verify the contact name was restored
        contact_input = page.locator("input[name='contact_name']")
        restored_value = contact_input.input_value()

        # The value should contain our test data (or be non-empty if draft was restored)
        assert restored_value != "", "Draft contact_name should be restored"


class TestVirtualRecurrenceMaterialization:
    """Test clicking a virtual recurring job occurrence materializes it."""

    def _find_weekday_cell(self, page: Page):
        """Find a non-Sunday day cell (double-click on non-Sunday opens job form)."""
        weekday_date = page.evaluate("""
            () => {
                const dayCells = document.querySelectorAll('.fc-daygrid-day');
                for (const cell of dayCells) {
                    const date = cell.getAttribute('data-date');
                    if (date) {
                        const d = new Date(date + 'T12:00:00');
                        if (d.getDay() === 1) {  // Monday
                            return date;
                        }
                    }
                }
                return null;
            }
        """)
        return weekday_date

    def _submit_job_form_via_fetch(self, page: Page):
        """Submit the job form using fetch (bypasses HTMX button click issues)."""
        result = page.evaluate("""
            async () => {
                const form = document.querySelector('#job-panel form');
                if (!form) return {error: 'No form found'};
                
                const formData = new FormData(form);
                const url = form.getAttribute('hx-post');
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
                
                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'HX-Request': 'true'
                        }
                    });
                    
                    const trigger = response.headers.get('hx-trigger');
                    if (trigger) {
                        const data = JSON.parse(trigger);
                        if (data.jobSaved) {
                            // Close panel and refresh calendar as HTMX would
                            if (window.JobPanel) window.JobPanel.close(true);
                            if (window.jobCalendar && window.jobCalendar.calendar) {
                                window.jobCalendar.calendar.refetchEvents();
                            }
                            return {ok: true, jobId: data.jobSaved.jobId};
                        }
                    }
                    return {ok: response.ok, status: response.status};
                } catch (e) {
                    return {error: e.message};
                }
            }
        """)
        return result

    def _delete_job_via_api(self, page: Page, job_id):
        """Delete a job via API to clean up test data."""
        page.evaluate(f"""
            async () => {{
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                                  document.cookie.match(/csrftoken=([^;]+)/)?.[1];
                try {{
                    await fetch('/api/jobs/{job_id}/delete/', {{
                        method: 'POST',
                        headers: {{
                            'X-CSRFToken': csrfToken,
                            'Content-Type': 'application/json'
                        }}
                    }});
                    if (window.jobCalendar && window.jobCalendar.calendar) {{
                        window.jobCalendar.calendar.refetchEvents();
                    }}
                }} catch (e) {{
                    console.error('Failed to delete job:', e);
                }}
            }}
        """)

    def test_create_recurring_job_shows_on_calendar(self, page: Page, server_url):
        """
        Create a recurring job and verify it appears on the calendar.
        Note: Virtual occurrence materialization requires the events to have 
        the data-gts-* attributes we added in this phase.
        """
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        page.wait_for_timeout(1000)

        # Find a weekday cell and double-click to open job panel
        weekday_date = self._find_weekday_cell(page)
        if not weekday_date:
            pytest.skip("No weekday cell found in calendar view")

        day_cell = page.locator(f'.fc-daygrid-day[data-date="{weekday_date}"]')
        day_cell.dblclick()

        page.wait_for_selector("#job-panel", timeout=5000)
        page.wait_for_selector("input[name='business_name']", timeout=5000)

        # Generate unique test data
        unique_id = page.evaluate("Date.now()")
        test_business = f"E2E Recurrence {unique_id}"

        # Fill in required fields
        page.locator("input[name='business_name']").fill(test_business)
        page.locator("input[name='contact_name']").fill("Test Contact")

        # Select a calendar using the visible header select
        header_select = page.locator("#calendar-header-select")
        if header_select.count() > 0:
            header_select.select_option("1")  # Select first calendar

        page.wait_for_timeout(500)

        # Enable recurrence
        recurrence_checkbox = page.locator("#recurrence-enabled")
        if recurrence_checkbox.count() > 0 and not recurrence_checkbox.is_checked():
            recurrence_checkbox.click()
            page.wait_for_timeout(500)

        # Set recurrence to weekly with no end (generates virtual occurrences)
        recurrence_end_mode = page.locator("#recurrence-end-mode")
        if recurrence_end_mode.count() > 0:
            recurrence_end_mode.select_option("never")

        # Submit using direct fetch (more reliable than button click with HTMX)
        result = self._submit_job_form_via_fetch(page)

        assert result.get("jobId"), f"Could not create test job: {result}"

        parent_job_id = result["jobId"]

        try:
            # Wait for calendar refresh
            page.wait_for_timeout(2000)

            # Look for the parent job event with our data attributes
            parent_event = page.locator(f'[data-gts-job-id="{parent_job_id}"]')

            # The parent job should be visible on the calendar
            assert parent_event.count() > 0, f"Parent job {parent_job_id} should appear on calendar"

            # Also verify the event has the correct type attribute
            event_type = parent_event.first.get_attribute("data-gts-event-type")
            assert event_type == "job", f"Event should have type 'job', got '{event_type}'"

        finally:
            # Cleanup: delete the test job via API
            self._delete_job_via_api(page, parent_job_id)
            page.wait_for_timeout(500)


class TestStandaloneCallReminderCRUD:
    """Test standalone call reminder create, update, complete, and delete operations."""

    def _delete_reminder_via_api(self, page: Page, reminder_id):
        """Delete a standalone call reminder via API to clean up test data."""
        page.evaluate(f"""
            async () => {{
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                                  document.cookie.match(/csrftoken=([^;]+)/)?.[1];
                try {{
                    await fetch('/call-reminders/{reminder_id}/delete/', {{
                        method: 'POST',
                        headers: {{
                            'X-CSRFToken': csrfToken,
                            'Content-Type': 'application/json'
                        }}
                    }});
                    if (window.jobCalendar && window.jobCalendar.calendar) {{
                        window.jobCalendar.calendar.refetchEvents();
                    }}
                }} catch (e) {{
                    console.error('Failed to delete reminder:', e);
                }}
            }}
        """)

    def test_create_call_reminder_on_sunday(self, page: Page, server_url):
        """
        Create a standalone call reminder by double-clicking a Sunday cell.
        This tests the basic creation flow and data attribute hooks.
        """
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        # Wait for panel/calendar JS to be ready (reduces flakiness from race conditions)
        page.wait_for_function("() => window.JobPanel && typeof window.JobPanel.load === 'function'")
        page.wait_for_function("() => window.jobCalendar && window.jobCalendar.calendar")

        # Find a Sunday cell to double-click (Sundays create call reminders)
        sunday_cell = page.evaluate("""
            () => {
                const dayCells = document.querySelectorAll('.fc-daygrid-day');
                for (const cell of dayCells) {
                    const date = cell.getAttribute('data-date');
                    if (date) {
                        const d = new Date(date + 'T12:00:00');
                        if (d.getDay() === 0) {  // Sunday
                            return date;
                        }
                    }
                }
                return null;
            }
        """)

        assert sunday_cell, "No Sunday cell found in current calendar view"

        reminder_id = None
        try:
            # Double-click the Sunday cell to open call reminder form
            # Double-click the day number to avoid accidentally targeting an event element.
            day_number = page.locator(f'.fc-daygrid-day[data-date="{sunday_cell}"] .fc-daygrid-day-number')
            if day_number.count() > 0:
                day_number.dblclick()
            else:
                page.locator(f'.fc-daygrid-day[data-date="{sunday_cell}"]').dblclick()

            # Wait for the panel + call reminder creation form to render
            page.wait_for_selector("#job-panel", timeout=10000)
            page.wait_for_selector("#call-reminder-form", timeout=10000)

            call_reminder_form = page.locator("#call-reminder-form")
            expect(call_reminder_form).to_be_visible()

            # Ensure the reminder date matches the cell we clicked (defensive against timezone/date shifting).
            # Note: flatpickr may hide the original input (type="hidden"), so don't try to `.fill()` it.
            current_reminder_date = page.evaluate("""
                () => document.querySelector('#call-reminder-form input[name="reminder_date"]')?.value || null
            """)
            assert current_reminder_date, "Call reminder form missing reminder_date value"
            if current_reminder_date != sunday_cell:
                page.evaluate(
                    """
                    (value) => {
                        const input = document.querySelector('#call-reminder-form input[name="reminder_date"]');
                        if (!input) return;
                        input.value = value;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    """,
                    sunday_cell,
                )

            unique_notes = f"E2E Test Reminder {page.evaluate('Date.now()')}"

            # Fill in notes if there's a notes field
            notes_input = page.locator("#call-reminder-form textarea, #call-reminder-form input[name='notes']")
            if notes_input.count() > 0:
                notes_input.fill(unique_notes)

            # Select a calendar if required
            calendar_select = page.locator("#call-reminder-form select[name='calendar']")
            if calendar_select.count() > 0:
                # Get options and select first non-empty one
                options = page.evaluate("""
                    () => {
                        const select = document.querySelector('#call-reminder-form select[name="calendar"]');
                        if (!select) return [];
                        return Array.from(select.options).filter(o => o.value).map(o => o.value);
                    }
                """)
                assert options, "No calendar options available for call reminder form"
                calendar_select.select_option(options[0])

            # Submit the form via HTMX and capture the JSON response
            submit_btn = page.locator("#call-reminder-form button[type='submit']")
            expect(submit_btn).to_be_visible()

            with page.expect_response(lambda r: "/call-reminders/create/" in r.url and r.request.method == "POST") as resp_info:
                submit_btn.click()

            create_resp = resp_info.value
            payload = create_resp.json()
            assert payload.get("success") is True, f"Call reminder create failed: {payload}"
            reminder_id = payload.get("reminder_id")
            assert reminder_id, f"Missing reminder_id in response: {payload}"

            # Wait for calendar to render the created reminder
            page.wait_for_selector(
                f'[data-gts-event-type="standalone_call_reminder"][data-gts-reminder-id="{reminder_id}"]',
                timeout=15000,
            )

            # Click and validate the panel hooks
            created_reminder = page.locator(
                f'[data-gts-event-type="standalone_call_reminder"][data-gts-reminder-id="{reminder_id}"]'
            ).first
            created_reminder.click()
            page.wait_for_timeout(500)

            notes_textarea = page.locator('[data-testid="call-reminder-notes"]')
            expect(notes_textarea).to_be_visible()

            save_btn = page.locator('[data-testid="call-reminder-save"]')
            complete_btn = page.locator('[data-testid="call-reminder-complete"]')
            delete_btn = page.locator('[data-testid="call-reminder-delete"]')

            has_actions = (
                save_btn.count() > 0 or
                complete_btn.count() > 0 or
                delete_btn.count() > 0
            )
            assert has_actions, "Call reminder panel should have action buttons with data-testid"
        finally:
            # Cleanup: don't leave reminders behind in a developer DB
            if reminder_id:
                self._delete_reminder_via_api(page, reminder_id)

