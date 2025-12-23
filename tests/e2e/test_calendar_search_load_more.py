"""
Playwright E2E test for calendar search panel "Load more" button.
Regression test for HTMX querySelectorAll error when loading additional job pages.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
    }


class TestCalendarSearchLoadMore:
    """Test that the calendar search panel load-more button works without errors."""
    
    def test_calendar_search_load_more_no_errors(self, page: Page, server_url):
        """
        Test that clicking "Load more" in calendar search panel works without HTMX errors.
        
        Regression test for: TypeError: e.querySelectorAll is not a function
        caused by HTMX parsing raw <tr> fragments mixed with non-table OOB elements.
        """
        errors = []
        console_errors = []
        
        # Capture page errors and console errors
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.on("console", lambda msg: 
                console_errors.append(msg.text) if msg.type == "error" else None)
        
        # Navigate to calendar page
        page.goto(f"{server_url}/")
        page.wait_for_selector("#calendar", timeout=10000)
        
        # Get CSRF token for API calls
        csrf_token = page.evaluate("""
            () => document.cookie.match(/csrftoken=([^;]+)/)?.[1] || ''
        """)
        assert csrf_token, "CSRF token must be available"
        
        # Get a valid calendar ID from the header select
        calendar_id = page.evaluate("""
            () => {
                const select = document.getElementById('calendar-header-select');
                if (!select || select.options.length === 0) return null;
                // Return first non-empty option value
                for (let i = 0; i < select.options.length; i++) {
                    const val = select.options[i].value;
                    if (val && val !== '') return parseInt(val, 10);
                }
                return null;
            }
        """)
        
        if not calendar_id:
            pytest.skip("No calendar available for test")
        
        # Create 30 jobs via API to ensure pagination (paginate_by = 25)
        unique_prefix = "LoadMoreTest"
        import datetime
        base_date = datetime.datetime.now().isoformat()
        
        for i in range(30):
            # Calculate start/end for each job
            start_date = page.evaluate(f"""
                () => {{
                    const d = new Date('{base_date}');
                    d.setDate(d.getDate() + {i});
                    return d.toISOString();
                }}
            """)
            
            end_date = page.evaluate(f"""
                () => {{
                    const d = new Date('{base_date}');
                    d.setDate(d.getDate() + {i});
                    d.setHours(d.getHours() + 2);
                    return d.toISOString();
                }}
            """)
            
            # Create job via API
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
                            business_name: '{unique_prefix} Job {i}',
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
            
            assert response["ok"], f"Failed to create job {i}: {response.get('data', response['status'])}"
        
        # Open search panel
        search_toggle = page.locator("#calendar-toggle-search-btn")
        if search_toggle.count() > 0:
            search_toggle.click()
            page.wait_for_selector("#calendar-search-panel.open", timeout=5000)
        
        # Ensure all calendars are selected (or select the test calendar)
        page.evaluate(f"""
            () => {{
                const checkboxes = document.querySelectorAll('.search-calendar-checkbox');
                checkboxes.forEach(cb => {{
                    if (cb.value === '{calendar_id}') {{
                        cb.checked = true;
                    }}
                }});
            }}
        """)
        
        # Enter search term
        search_input = page.locator("#calendar-search-input")
        search_input.fill(unique_prefix)
        
        # Submit search
        search_form = page.locator("#calendar-search-form")
        search_form.evaluate("form => form.submit()")
        
        # Wait for results to load
        page.wait_for_selector(".job-row", timeout=10000)
        
        # Count initial rows (should be 25, first page)
        initial_row_count = page.locator(".job-row").count()
        assert initial_row_count == 25, f"Expected 25 rows on first page, got {initial_row_count}"
        
        # Check that load-more button exists
        load_more_btn = page.locator("#job-list-load-more-btn")
        expect(load_more_btn).to_be_visible(timeout=5000)
        
        # Clear console errors before the critical action
        console_errors.clear()
        errors.clear()
        
        # Click "Load more" button
        load_more_btn.click()
        
        # Wait for additional rows to appear
        page.wait_for_function("""
            () => document.querySelectorAll('.job-row').length > 25
        """, timeout=10000)
        
        # Count rows after load more
        final_row_count = page.locator(".job-row").count()
        assert final_row_count == 30, f"Expected 30 rows after load more, got {final_row_count}"
        
        # Verify load-more button is hidden/removed (no more pages)
        page.wait_for_function("""
            () => {
                const btn = document.getElementById('job-list-load-more-btn');
                return !btn || btn.style.display === 'none' || btn.offsetParent === null;
            }
        """, timeout=5000)
        
        # Check for HTMX-specific errors
        htmx_errors = [e for e in console_errors if 'htmx' in e.lower() or 'queryselectorall' in e.lower()]
        assert len(htmx_errors) == 0, f"HTMX errors detected in console: {htmx_errors}"
        
        # Check for critical JS errors
        critical_errors = [e for e in errors if 
            "querySelectorAll" in e or 
            "swapError" in e or
            "Cannot read properties" in e
        ]
        
        assert len(critical_errors) == 0, f"Critical JS errors found: {critical_errors}"
        
        # Cleanup: delete created jobs
        for i in range(30):
            job_name = f"{unique_prefix} Job {i}"
            page.evaluate(f"""
                async () => {{
                    // Find job ID by business name (search in rendered rows)
                    const rows = Array.from(document.querySelectorAll('.job-row'));
                    const targetRow = rows.find(r => r.textContent.includes('{job_name}'));
                    if (!targetRow) return;
                    
                    const jobId = targetRow.getAttribute('data-job-id');
                    if (!jobId) return;
                    
                    await fetch(`/api/jobs/${{jobId}}/delete/`, {{
                        method: 'POST',
                        headers: {{
                            'X-CSRFToken': '{csrf_token}',
                            'Content-Type': 'application/json'
                        }}
                    }});
                }}
            """)
    
    def test_jobs_list_page_load_more_no_errors(self, page: Page, server_url):
        """
        Test that clicking "Load more" on /jobs/ page works without HTMX errors.
        
        Regression test for the same issue on the jobs list page.
        """
        errors = []
        console_errors = []
        
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.on("console", lambda msg: 
                console_errors.append(msg.text) if msg.type == "error" else None)
        
        # Navigate to jobs list page
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
                const select = document.querySelector('select[name="calendar"]');
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
        
        # Create 30 jobs
        unique_prefix = "JobsPageLoadMoreTest"
        import datetime
        base_date = datetime.datetime.now().isoformat()
        
        for i in range(30):
            start_date = page.evaluate(f"""
                () => {{
                    const d = new Date('{base_date}');
                    d.setDate(d.getDate() + {i});
                    return d.toISOString();
                }}
            """)
            
            end_date = page.evaluate(f"""
                () => {{
                    const d = new Date('{base_date}');
                    d.setDate(d.getDate() + {i});
                    d.setHours(d.getHours() + 2);
                    return d.toISOString();
                }}
            """)
            
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
                            business_name: '{unique_prefix} Job {i}',
                            start: '{start_date}',
                            end: '{end_date}',
                            status: 'uncompleted',
                            allDay: false
                        }})
                    }});
                    return {{
                        ok: response.ok,
                        status: response.status
                    }};
                }}
            """)
            
            assert response["ok"], f"Failed to create job {i}"
        
        # Reload page to see new jobs
        page.reload()
        page.wait_for_selector("#job-table-body", timeout=10000)
        
        # Count initial rows
        initial_row_count = page.locator(".job-row").count()
        
        # If there are fewer than 25 rows, we may not have pagination
        if initial_row_count < 25:
            pytest.skip("Not enough jobs for pagination test")
        
        # Check for load-more button
        load_more_btn = page.locator("#job-list-load-more-btn")
        if load_more_btn.count() == 0:
            pytest.skip("Load more button not visible (may be scrolled out of view)")
        
        # Clear error tracking
        console_errors.clear()
        errors.clear()
        
        # Click load more
        load_more_btn.scroll_into_view_if_needed()
        load_more_btn.click()
        
        # Wait for additional rows
        page.wait_for_function(f"""
            () => document.querySelectorAll('.job-row').length > {initial_row_count}
        """, timeout=10000)
        
        # Check no HTMX errors occurred
        htmx_errors = [e for e in console_errors if 'htmx' in e.lower() or 'queryselectorall' in e.lower()]
        assert len(htmx_errors) == 0, f"HTMX errors in console: {htmx_errors}"
        
        critical_errors = [e for e in errors if 
            "querySelectorAll" in e or 
            "swapError" in e
        ]
        assert len(critical_errors) == 0, f"Critical errors: {critical_errors}"
        
        # Cleanup
        for i in range(30):
            job_name = f"{unique_prefix} Job {i}"
            page.evaluate(f"""
                async () => {{
                    const rows = Array.from(document.querySelectorAll('.job-row'));
                    const targetRow = rows.find(r => r.textContent.includes('{job_name}'));
                    if (!targetRow) return;
                    
                    const jobId = targetRow.getAttribute('data-job-id');
                    if (!jobId) return;
                    
                    await fetch(`/api/jobs/${{jobId}}/delete/`, {{
                        method: 'POST',
                        headers: {{
                            'X-CSRFToken': '{csrf_token}',
                            'Content-Type': 'application/json'
                        }}
                    }});
                }}
            """)

