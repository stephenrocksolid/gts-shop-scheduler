"""
Playwright E2E tests for the modal-based job delete feature.
Tests that delete works via modal without page navigation on both:
- Calendar search results
- Jobs list page

Regression test for: Full-page redirect to /jobs/<id>/delete/ confirmation page.
"""
import re
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
    }


class TestDeleteModalCalendarSearch:
    """Test delete modal in calendar search results."""

    def test_delete_opens_modal_not_page_navigation(self, page: Page, server_url):
        """
        Clicking trash icon in calendar search should open modal, not navigate away.
        """
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))

        # Navigate to calendar page
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)

        # Get CSRF token for API calls
        csrf_token = page.evaluate("""
            () => document.cookie.match(/csrftoken=([^;]+)/)?.[1] || ''
        """)
        assert csrf_token, "CSRF token must be available"

        # Get a valid calendar ID
        calendar_id = page.evaluate("""
            () => {
                const select = document.getElementById('calendar-header-select');
                if (!select || select.options.length === 0) return null;
                for (let i = 0; i < select.options.length; i++) {
                    const val = select.options[i].value;
                    if (val && val !== '') return parseInt(val, 10);
                }
                return null;
            }
        """)

        if not calendar_id:
            pytest.skip("No calendar available for test")

        # Create a test job via API
        unique_name = "DeleteModalTest_CalSearch"
        import datetime
        base_date = datetime.datetime.now()
        start_date = (base_date + datetime.timedelta(days=1)).isoformat()
        end_date = (base_date + datetime.timedelta(days=1, hours=2)).isoformat()

        response = page.evaluate(f"""
            async () => {{
                const response = await fetch('/api/jobs/create/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{csrf_token}',
                        'X-Requested-With': 'XMLHttpRequest'
                    }},
                    body: JSON.stringify({{
                        calendar: {calendar_id},
                        business_name: '{unique_name}',
                        start: '{start_date}',
                        end: '{end_date}',
                        status: 'uncompleted',
                        allDay: false
                    }})
                }});
                return {{
                    ok: response.ok,
                    status: response.status,
                    data: response.ok ? await response.json() : await response.text()
                }};
            }}
        """)
        assert response["ok"], f"Failed to create test job: {response.get('data', response['status'])}"
        job_id = response["data"].get("job_id") or response["data"].get("id")
        assert job_id, "Job ID not returned"

        try:
            # Open search panel
            search_toggle = page.locator("#calendar-toggle-search-btn")
            if search_toggle.count() > 0:
                search_toggle.click()
                page.wait_for_selector("#calendar-search-panel.open", timeout=5000)

            # Select the test calendar
            page.evaluate(f"""
                () => {{
                    const checkboxes = document.querySelectorAll('.search-calendar-checkbox');
                    checkboxes.forEach(cb => {{
                        cb.checked = (cb.value === '{calendar_id}');
                    }});
                }}
            """)

            # Search for the job
            search_input = page.locator("#calendar-search-input")
            search_input.fill(unique_name)

            # Submit search
            search_form = page.locator("#calendar-search-form")
            search_form.evaluate("form => form.submit()")

            # Wait for results
            page.wait_for_selector(f".job-row[data-job-id='{job_id}']", timeout=10000)

            # Record current URL before clicking delete
            url_before = page.url

            # Find and click the delete button (trash icon)
            delete_btn = page.locator(f".job-row[data-job-id='{job_id}'] [data-gts-action='job-delete']")
            expect(delete_btn).to_be_visible()
            delete_btn.click()

            # Modal should appear
            page.wait_for_selector("#gts-modal-root:not(.hidden)", timeout=5000)
            expect(page.locator("#gts-modal-root [data-modal-confirm]")).to_be_visible()

            # URL should NOT have changed
            assert page.url == url_before, f"URL changed from {url_before} to {page.url} - modal should not navigate"

            # Modal should show job name
            modal_content = page.locator("#gts-modal-root").text_content()
            assert unique_name in modal_content, "Modal should display job name"

            # Click cancel to close modal
            cancel_btn = page.locator("#gts-modal-root [data-modal-cancel]")
            cancel_btn.click()

            # Modal should be hidden
            expect(page.locator("#gts-modal-root")).to_have_class(
                re.compile(r"(^|\s)hidden(\s|$)")
            )

            # Now click delete again and confirm
            delete_btn.click()
            page.wait_for_selector("#gts-modal-root:not(.hidden)", timeout=5000)

            confirm_btn = page.locator("#gts-modal-root [data-modal-confirm]")
            confirm_btn.click()

            # Wait for modal to close
            page.wait_for_function("""
                () => {
                    const modal = document.getElementById('gts-modal-root');
                    return modal && modal.classList.contains('hidden');
                }
            """, timeout=10000)

            # Job row should be gone after refresh
            page.wait_for_function(f"""
                () => !document.querySelector('.job-row[data-job-id="{job_id}"]')
            """, timeout=10000)

            # Check no JS errors occurred
            critical_errors = [e for e in errors if "Cannot read properties" in e or "null" in e]
            assert len(critical_errors) == 0, f"JS errors found: {critical_errors}"

        finally:
            # Cleanup: try to delete the job if it still exists
            page.evaluate(f"""
                async () => {{
                    try {{
                        await fetch('/api/jobs/{job_id}/delete/', {{
                            method: 'POST',
                            headers: {{
                                'X-CSRFToken': '{csrf_token}',
                                'Content-Type': 'application/json'
                            }}
                        }});
                    }} catch (e) {{}}
                }}
            """)


class TestDeleteModalJobsList:
    """Test delete modal on the jobs list page."""

    def test_delete_opens_modal_on_jobs_list(self, page: Page, server_url):
        """
        Clicking trash icon on /jobs/ page should open modal, not navigate away.
        """
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))

        # Navigate to jobs list
        page.goto(f"{server_url}/jobs/")
        page.wait_for_selector("#job-table-body", timeout=10000)

        # Get CSRF token
        csrf_token = page.evaluate("""
            () => document.cookie.match(/csrftoken=([^;]+)/)?.[1] || ''
        """)
        assert csrf_token, "CSRF token must be available"

        # Get a valid calendar ID
        calendar_id = page.evaluate("""
            () => {
                const checkboxes = document.querySelectorAll('.calendar-checkbox');
                for (let i = 0; i < checkboxes.length; i++) {
                    const val = checkboxes[i].value;
                    if (val && val !== '') return parseInt(val, 10);
                }
                return null;
            }
        """)

        if not calendar_id:
            pytest.skip("No calendar available for test")

        # Create a test job
        unique_name = "DeleteModalTest_JobsList"
        import datetime
        base_date = datetime.datetime.now()
        start_date = (base_date + datetime.timedelta(days=2)).isoformat()
        end_date = (base_date + datetime.timedelta(days=2, hours=2)).isoformat()

        response = page.evaluate(f"""
            async () => {{
                const response = await fetch('/api/jobs/create/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{csrf_token}',
                        'X-Requested-With': 'XMLHttpRequest'
                    }},
                    body: JSON.stringify({{
                        calendar: {calendar_id},
                        business_name: '{unique_name}',
                        start: '{start_date}',
                        end: '{end_date}',
                        status: 'uncompleted',
                        allDay: false
                    }})
                }});
                return {{
                    ok: response.ok,
                    status: response.status,
                    data: response.ok ? await response.json() : await response.text()
                }};
            }}
        """)
        assert response["ok"], f"Failed to create test job: {response.get('data', response['status'])}"
        job_id = response["data"].get("job_id") or response["data"].get("id")
        assert job_id, "Job ID not returned"

        try:
            # Reload to see the new job
            page.reload()
            page.wait_for_selector("#job-table-body", timeout=10000)

            # Search for the job
            search_input = page.locator("#search-input")
            if search_input.count() > 0:
                search_input.fill(unique_name)
                page.locator("#search-form").evaluate("form => form.submit()")
                page.wait_for_selector(f".job-row[data-job-id='{job_id}']", timeout=10000)

            # Record current URL
            url_before = page.url

            # Find the delete button
            delete_btn = page.locator(f".job-row[data-job-id='{job_id}'] [data-gts-action='job-delete']")
            expect(delete_btn).to_be_visible()
            delete_btn.click()

            # Modal should appear
            page.wait_for_selector("#gts-modal-root:not(.hidden)", timeout=5000)
            expect(page.locator("#gts-modal-root [data-modal-confirm]")).to_be_visible()

            # URL should NOT have changed
            assert page.url == url_before, f"URL changed - modal should not navigate"

            # Click confirm to delete
            confirm_btn = page.locator("#gts-modal-root [data-modal-confirm]")
            confirm_btn.click()

            # Wait for modal to close and job to disappear
            page.wait_for_function("""
                () => {
                    const modal = document.getElementById('gts-modal-root');
                    return modal && modal.classList.contains('hidden');
                }
            """, timeout=10000)

            # Table should refresh and job should be gone
            page.wait_for_function(f"""
                () => !document.querySelector('.job-row[data-job-id="{job_id}"]')
            """, timeout=10000)

            # Still on jobs list page (not redirected to job_list after delete)
            assert "/jobs" in page.url, "Should still be on jobs list page"

            # Check no JS errors
            critical_errors = [e for e in errors if "Cannot read properties" in e]
            assert len(critical_errors) == 0, f"JS errors found: {critical_errors}"

        finally:
            # Cleanup
            page.evaluate(f"""
                async () => {{
                    try {{
                        await fetch('/api/jobs/{job_id}/delete/', {{
                            method: 'POST',
                            headers: {{
                                'X-CSRFToken': '{csrf_token}',
                                'Content-Type': 'application/json'
                            }}
                        }});
                    }} catch (e) {{}}
                }}
            """)


class TestDeleteModalRecurring:
    """Test delete modal with recurring job scope options."""

    def test_recurring_job_shows_scope_picker(self, page: Page, server_url):
        """
        Deleting a recurring instance should show scope picker in modal.
        """
        page.goto(f"{server_url}/jobs/")
        page.wait_for_selector("#job-table-body", timeout=10000)

        # Get CSRF token
        csrf_token = page.evaluate("""
            () => document.cookie.match(/csrftoken=([^;]+)/)?.[1] || ''
        """)
        assert csrf_token, "CSRF token must be available"

        # Get a valid calendar ID
        calendar_id = page.evaluate("""
            () => {
                const checkboxes = document.querySelectorAll('.calendar-checkbox');
                for (let i = 0; i < checkboxes.length; i++) {
                    const val = checkboxes[i].value;
                    if (val && val !== '') return parseInt(val, 10);
                }
                return null;
            }
        """)

        if not calendar_id:
            pytest.skip("No calendar available for test")

        # Create a recurring parent job
        unique_name = "DeleteModalTest_Recurring"
        import datetime
        base_date = datetime.datetime.now()
        start_date = (base_date + datetime.timedelta(days=3)).isoformat()
        end_date = (base_date + datetime.timedelta(days=3, hours=2)).isoformat()

        response = page.evaluate(f"""
            async () => {{
                const response = await fetch('/api/jobs/create/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{csrf_token}',
                        'X-Requested-With': 'XMLHttpRequest'
                    }},
                    body: JSON.stringify({{
                        calendar: {calendar_id},
                        business_name: '{unique_name}',
                        start: '{start_date}',
                        end: '{end_date}',
                        status: 'uncompleted',
                        allDay: false,
                        recurrence: {{
                            enabled: true,
                            type: 'weekly',
                            interval: 1,
                            count: 3
                        }}
                    }})
                }});
                return {{
                    ok: response.ok,
                    status: response.status,
                    data: response.ok ? await response.json() : await response.text()
                }};
            }}
        """)

        if not response["ok"]:
            pytest.skip("Recurring job creation may not be fully supported")

        job_id = response["data"].get("job_id") or response["data"].get("id")
        parent_id = job_id

        try:
            # Reload to see the job
            page.reload()
            page.wait_for_selector("#job-table-body", timeout=10000)

            # Search for the recurring job
            search_input = page.locator("#search-input")
            if search_input.count() > 0:
                search_input.fill(unique_name)
                page.locator("#search-form").evaluate("form => form.submit()")
                page.wait_for_timeout(2000)

            # Find any job with this name that has recurring attributes
            recurring_row = page.locator(f".job-row[data-job-display-name*='{unique_name}']").first
            if recurring_row.count() == 0:
                pytest.skip("Recurring job not found in list")

            delete_btn = recurring_row.locator("[data-gts-action='job-delete']")
            delete_btn.click()

            # Modal should appear
            page.wait_for_selector("#gts-modal-root:not(.hidden)", timeout=5000)

            # Check if recurring - scope picker should be present
            is_recurring_parent = recurring_row.get_attribute("data-is-recurring-parent")
            is_recurring_instance = recurring_row.get_attribute("data-is-recurring-instance")

            if is_recurring_parent or is_recurring_instance:
                # Scope radios should be visible
                scope_radios = page.locator("#gts-modal-root input[name='delete_scope']")
                assert scope_radios.count() >= 2, "Recurring job modal should have scope options"

                # Check specific options exist
                expect(page.locator("#gts-modal-root input[value='this_and_future']")).to_be_visible()
                expect(page.locator("#gts-modal-root input[value='all']")).to_be_visible()

            # Cancel the modal
            page.locator("#gts-modal-root [data-modal-cancel]").click()
            expect(page.locator("#gts-modal-root")).to_have_class(
                re.compile(r"(^|\s)hidden(\s|$)")
            )

        finally:
            # Cleanup: delete the entire series
            if parent_id:
                page.evaluate(f"""
                    async () => {{
                        try {{
                            await fetch('/api/jobs/{parent_id}/delete-recurring/', {{
                                method: 'POST',
                                headers: {{
                                    'X-CSRFToken': '{csrf_token}',
                                    'Content-Type': 'application/json'
                                }},
                                body: JSON.stringify({{ delete_scope: 'all' }})
                            }});
                        }} catch (e) {{}}
                    }}
                """)

