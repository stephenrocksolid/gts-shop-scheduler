/**
 * Job Form Partial Entrypoint
 * 
 * Extracted from _job_form_partial.html inline script.
 * Handles:
 * - After-request orchestration (replaces inline hx-on::after-request)
 * - Recurrence end-mode toggle
 * - Print flow (save-then-print + iframe)
 * - Status update / delete actions
 * - HTMX required-field validation interceptor
 * - Form change tracking initialization
 * 
 * Note: Calendar selector cloning and toggle wiring are handled by panel.js
 *       via initPanelCalendarSelector() and initJobFormToggleUI()
 * 
 * Requires: GTS.initOnce, window.JobPanel, window.JobWorkspace, window.jobCalendar
 */
(function() {
    'use strict';

    // ========================================================================
    // GLOBAL INITIALIZATION (run once, bind via delegation)
    // ========================================================================

    GTS.onDomReady(function() {
        initPrintHandler();
        initAfterRequestHandler();
        initRequiredFieldValidation();
        initStatusDeleteHandlers();
    });

    // ========================================================================
    // AFTER-REQUEST ORCHESTRATION
    // Replaces the inline hx-on::after-request="..." attribute on the form
    // ========================================================================

    function initAfterRequestHandler() {
        GTS.initOnce('job_form_after_request', function() {
            document.body.addEventListener('htmx:afterRequest', function(event) {
                // Only handle job form submissions
                const form = event.target.closest('form');
                if (!form) return;
                
                // Check if this is a job form submission (has hx-post to job_create_submit)
                const hxPost = form.getAttribute('hx-post');
                if (!hxPost || !hxPost.includes('job')) return;
                
                // Check if the form has our marker attribute (set in template)
                if (!form.hasAttribute('data-gts-job-form')) return;
                
                if (event.detail.successful) {
                    // Clear unsaved changes tracking
                    if (window.JobPanel && window.JobPanel.clearUnsavedChanges) {
                        window.JobPanel.clearUnsavedChanges();
                    }
                    
                    // Close panel/workspace tab unless we're switching jobs
                    if (window.JobPanel && !window.JobPanel.isSwitchingJobs) {
                        const currentJobId = window.JobPanel.currentJobId;
                        if (currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob && window.JobWorkspace.hasJob(currentJobId)) {
                            window.JobWorkspace.closeJob(currentJobId);
                        } else {
                            window.JobPanel.close(true); // true = skip unsaved check
                        }
                    }
                    
                    // Refresh calendar events
                    if (window.jobCalendar && window.jobCalendar.calendar) {
                        window.jobCalendar.calendar.refetchEvents();
                    }
                }
            });
        });
    }

    // ========================================================================
    // REQUIRED-FIELD VALIDATION INTERCEPTOR
    // ========================================================================

    function initRequiredFieldValidation() {
        GTS.initOnce('job_form_validation', function() {
            /**
             * Check which required fields are missing from the form.
             * Required fields: business_name, start_dt, end_dt, calendar
             */
            function getRequiredMissing(form) {
                if (!form) return ['form'];
                const missing = [];

                // Business name - required and must not be whitespace-only
                const businessName = form.querySelector('input[name="business_name"]');
                if (!businessName || !businessName.value.trim()) {
                    missing.push('business_name');
                }

                // Start date - required
                const startDt = form.querySelector('input[name="start_dt"]');
                if (!startDt || !startDt.value.trim()) {
                    missing.push('start_dt');
                }

                // End date - required
                const endDt = form.querySelector('input[name="end_dt"]');
                if (!endDt || !endDt.value.trim()) {
                    missing.push('end_dt');
                }

                // Calendar - required (select element)
                const calendar = form.querySelector('select[name="calendar"]');
                if (!calendar || !calendar.value) {
                    missing.push('calendar');
                }

                return missing;
            }

            // Intercept HTMX form submission to validate required fields
            document.body.addEventListener('htmx:beforeRequest', function(event) {
                const form = event.target.closest('form');

                // Only validate for job form submissions
                if (!form || !form.hasAttribute('data-gts-job-form')) {
                    return;
                }

                // Check if this is a "natural" submit (user clicked Save button) vs programmatic
                // Programmatic calls use htmx.trigger() which we can detect by checking if
                // window.JobPanel.isSwitchingJobs is true (set during minimize/close flows)
                if (window.JobPanel && window.JobPanel.isSwitchingJobs) {
                    // This is a programmatic call from minimize/close, skip validation
                    return;
                }

                const missingFields = getRequiredMissing(form);
                if (missingFields.length > 0) {
                    // Prevent the HTMX request from proceeding
                    event.preventDefault();

                    // Show user-friendly error
                    GTS.showToast('Please fill in all required fields (Business Name, Start, End, Calendar) before saving.', 'warning');

                    // Focus the first missing field
                    if (missingFields.includes('business_name')) {
                        const field = form.querySelector('input[name="business_name"]');
                        if (field) field.focus();
                    } else if (missingFields.includes('start_dt')) {
                        const field = form.querySelector('input[name="start_dt"]');
                        if (field) field.focus();
                    } else if (missingFields.includes('end_dt')) {
                        const field = form.querySelector('input[name="end_dt"]');
                        if (field) field.focus();
                    } else if (missingFields.includes('calendar')) {
                        // Focus the visible header calendar select, not the hidden form field
                        let headerSelect = document.getElementById('calendar-header-select');

                        // If header select doesn't exist, try to initialize it
                        if (!headerSelect && window.initPanelCalendarSelector) {
                            const panelBody = document.querySelector('#job-panel .panel-body');
                            if (panelBody) {
                                window.initPanelCalendarSelector(panelBody);
                                headerSelect = document.getElementById('calendar-header-select');
                            }
                        }

                        if (headerSelect) {
                            headerSelect.focus();
                        }
                    }

                    console.log('HTMX form submission blocked: missing required fields', missingFields);
                }
            });
        });
    }

    // ========================================================================
    // PRINT HANDLER (Delegated, global)
    // ========================================================================

    function initPrintHandler() {
        GTS.initOnce('job_form_print', function() {
            /**
             * Print via hidden iframe
             */
            function printViaIframe(url) {
                console.log('Print via iframe:', url);

                // Close the Job Panel before printing
                if (window.JobPanel) {
                    window.JobPanel.close();
                }

                // Remove any existing iframe
                let oldFrame = document.getElementById('printFrame');
                if (oldFrame) {
                    oldFrame.remove();
                }

                // Create a fresh iframe for each print job
                const printFrame = document.createElement('iframe');
                printFrame.id = 'printFrame';
                printFrame.style.cssText = 'position:absolute;width:0;height:0;border:none;';
                document.body.appendChild(printFrame);

                // Add cache-busting parameter
                const fullUrl = url + (url.includes('?') ? '&' : '?') + '_=' + Date.now();

                console.log('Loading URL:', fullUrl);

                // Use onload to trigger print
                let loadAttempted = false;
                printFrame.onload = function() {
                    if (loadAttempted) return;
                    loadAttempted = true;

                    console.log('Iframe loaded, attempting to print...');

                    // Wait a bit for the content to fully render
                    setTimeout(function() {
                        try {
                            const iframeWindow = printFrame.contentWindow || printFrame.contentDocument.defaultView;
                            if (iframeWindow) {
                                iframeWindow.focus();
                                iframeWindow.print();
                                console.log('Print dialog triggered');
                            } else {
                                throw new Error('Could not access iframe window');
                            }
                        } catch (error) {
                            console.error('Error printing:', error);
                            alert('Unable to print directly. Opening in new window...');
                            window.open(url, '_blank');
                        }
                    }, 500);
                };

                // Small delay before loading to ensure iframe is ready
                setTimeout(function() {
                    printFrame.src = fullUrl;
                }, 50);
            }

            /**
             * Save job form and then print
             */
            function saveJobThenPrint(form, jobId, printType) {
                console.log('Saving job form before printing...');

                // Show loading state on the print button
                const printBtn = document.querySelector('[data-print-type="' + printType + '"]');
                const originalText = printBtn ? printBtn.textContent : '';
                if (printBtn) {
                    printBtn.textContent = 'Saving...';
                    printBtn.disabled = true;
                }

                // Get the form action URL
                const hxPost = form.getAttribute('hx-post');

                if (hxPost) {
                    // Define the success handler
                    const handleAfterRequest = function(event) {
                        // Get the job ID from the form after save
                        let actualJobId = jobId;
                        const jobIdInput = form.querySelector('input[name="job_id"]');
                        if (jobIdInput && jobIdInput.value) {
                            actualJobId = jobIdInput.value;
                        }

                        if (event.detail.successful) {
                            console.log('Job saved successfully, now printing...');

                            // Clear unsaved changes tracking
                            if (window.JobPanel && window.JobPanel.clearUnsavedChanges) {
                                window.JobPanel.clearUnsavedChanges();
                            }

                            // Remove the event listener
                            document.body.removeEventListener('htmx:afterRequest', handleAfterRequest);

                            var url = GTS.urls.jobPrint(actualJobId, printType);
                            printViaIframe(url);
                        } else {
                            console.error('Failed to save job:', event.detail);

                            let errorMsg = 'Failed to save job. Please check all required fields and try again.';
                            if (event.detail.xhr && event.detail.xhr.responseText) {
                                console.error('Server response:', event.detail.xhr.responseText);
                            }

                            alert(errorMsg);
                            if (printBtn) {
                                printBtn.textContent = originalText;
                                printBtn.disabled = false;
                            }
                            // Remove the event listener
                            document.body.removeEventListener('htmx:afterRequest', handleAfterRequest);
                        }
                    };

                    // Add event listener
                    document.body.addEventListener('htmx:afterRequest', handleAfterRequest);

                    // Trigger the form submission using HTMX's trigger
                    htmx.trigger(form, 'submit');
                } else {
                    // Fallback: try to submit using fetch
                    const formData = new FormData(form);

                    fetch(form.action || window.location.href, {
                        method: 'POST',
                        body: formData,
                        headers: { 'X-CSRFToken': GTS.csrf.getToken({ root: form }) }
                    })
                        .then(function(response) {
                            if (response.ok) {
                                console.log('Job saved successfully, now printing...');
                                var url = GTS.urls.jobPrint(jobId, printType);
                                printViaIframe(url);
                            } else {
                                throw new Error('Save failed - status ' + response.status);
                            }
                        })
                        .catch(function(error) {
                            console.error('Failed to save job:', error);
                            alert('Failed to save job. Please check all required fields and try again.');
                            if (printBtn) {
                                printBtn.textContent = originalText;
                                printBtn.disabled = false;
                            }
                        });
                }
            }

            // Use event delegation - attach to document body so it works for all future buttons
            document.body.addEventListener('click', function(e) {
                // Check if clicked element is a print button
                const btn = e.target.closest('.print-btn');
                if (btn && !btn.disabled) {
                    GTS.dom.stop(e);
                    const jobId = btn.getAttribute('data-job-id');
                    const printType = btn.getAttribute('data-print-type');

                    // Check if we're in a job form and need to save first
                    const form = btn.closest('form');
                    if (form && form.querySelector('input[name="business_name"]')) {
                        // We're in a job form - save first, then print
                        console.log('Print button clicked in job form - saving first...');
                        saveJobThenPrint(form, jobId, printType);
                    } else if (jobId && jobId !== '0') {
                        // Not in a form but have a valid job ID - print directly
                        var url = GTS.urls.jobPrint(jobId, printType);
                        console.log('Print button clicked! JobId:', jobId, 'Type:', printType);
                        printViaIframe(url);
                    } else {
                        // No job ID or job ID is 0 - can't print
                        alert('Please save the job first before printing.');
                    }
                }
            });

            // Hover effects using event delegation
            document.body.addEventListener('mouseover', function(e) {
                const btn = e.target.closest('.print-btn');
                if (btn && !btn.disabled) {
                    btn.style.backgroundColor = '#f9fafb';
                }
            });

            document.body.addEventListener('mouseout', function(e) {
                const btn = e.target.closest('.print-btn');
                if (btn && !btn.disabled) {
                    btn.style.backgroundColor = '#ffffff';
                }
            });
        });
    }

    // ========================================================================
    // STATUS UPDATE / DELETE HANDLERS
    // ========================================================================

    function initStatusDeleteHandlers() {
        GTS.initOnce('job_form_status_delete', function() {
            /**
             * Update job status via API
             */
            function updateJobStatus(jobId, status) {
                // Check if there's a form with unsaved changes
                const form = document.querySelector('#job-panel form');
                const hasUnsavedChanges = window.JobPanel && window.JobPanel.hasUnsavedChanges
                    ? (typeof window.JobPanel.hasUnsavedChanges === 'function'
                        ? window.JobPanel.hasUnsavedChanges()
                        : false)
                    : false;

                // If there are unsaved changes and we have a form, save first
                if (hasUnsavedChanges && form) {
                    console.log('Saving form before updating job status...');

                    // Create a one-time listener for the save success
                    const handleAfterRequest = function(event) {
                        if (event.detail.successful) {
                            console.log('Form saved, now updating job status...');
                            document.body.removeEventListener('htmx:afterRequest', handleAfterRequest);

                            // Clear unsaved changes tracking
                            if (window.JobPanel && window.JobPanel.clearUnsavedChanges) {
                                window.JobPanel.clearUnsavedChanges();
                            }

                            // Now update the status
                            performStatusUpdate(jobId, status);
                        }
                    };

                    document.body.addEventListener('htmx:afterRequest', handleAfterRequest);

                    // Trigger form submission
                    htmx.trigger(form, 'submit');
                } else {
                    // No unsaved changes, proceed directly
                    performStatusUpdate(jobId, status);
                }
            }

            /**
             * Perform the actual status update API call
             */
            function performStatusUpdate(jobId, status) {
                fetch(GTS.urls.jobUpdateStatus(jobId), {
                    method: 'POST',
                    headers: GTS.csrf.headers({ 'Content-Type': 'application/json' }),
                    body: JSON.stringify({ status: status })
                })
                    .then(function(response) { return response.json(); })
                    .then(function(data) {
                        if (data.success) {
                            // Close panel without unsaved check
                            if (window.JobPanel) {
                                window.JobPanel.close(true);
                            }
                            // Refresh the calendar
                            if (window.jobCalendar && window.jobCalendar.calendar) {
                                window.jobCalendar.calendar.refetchEvents();
                            }
                        } else {
                            console.error('Failed to update job status:', data.error);
                        }
                    })
                    .catch(function(error) {
                        console.error('Error updating job status:', error);
                    });
            }

            /**
             * Delete job via API
             */
            function deleteJob(jobId) {
                if (confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
                    fetch(GTS.urls.jobDelete(jobId), {
                        method: 'POST',
                        headers: GTS.csrf.headers({ 'Content-Type': 'application/json' })
                    })
                        .then(function(response) { return response.json(); })
                        .then(function(data) {
                            if (data.success) {
                                // Close panel and refresh calendar
                                if (window.JobPanel) {
                                    window.JobPanel.close();
                                }
                                if (window.jobCalendar && window.jobCalendar.calendar) {
                                    window.jobCalendar.calendar.refetchEvents();
                                }
                            } else {
                                console.error('Failed to delete job:', data.error);
                            }
                        })
                        .catch(function(error) {
                            console.error('Error deleting job:', error);
                        });
                }
            }

            // Use event delegation for complete/uncomplete/delete buttons
            document.body.addEventListener('click', function(e) {
                const completeBtn = e.target.closest('.complete-btn');
                if (completeBtn) {
                    const jobId = completeBtn.getAttribute('data-job-id');
                    if (jobId) updateJobStatus(jobId, 'completed');
                    return;
                }

                const uncompleteBtn = e.target.closest('.uncomplete-btn');
                if (uncompleteBtn) {
                    const jobId = uncompleteBtn.getAttribute('data-job-id');
                    if (jobId) updateJobStatus(jobId, 'uncompleted');
                    return;
                }

                const deleteBtn = e.target.closest('.delete-btn');
                if (deleteBtn) {
                    const jobId = deleteBtn.getAttribute('data-job-id');
                    if (jobId) deleteJob(jobId);
                    return;
                }
            });
        });
    }

    // ========================================================================
    // FORM INITIALIZATION FUNCTION (called when form partial is loaded)
    // ========================================================================

    /**
     * Initialize job form partial behaviors.
     * Called by panel.js after loading form content, or by HTMX events.
     * 
     * @param {HTMLElement} rootEl - Root element containing the form
     */
    window.initJobFormPartial = function(rootEl) {
        if (!rootEl) return;

        // Initialize recurrence end-mode toggle
        initRecurrenceEndModeToggle(rootEl);

        // Initialize form change tracking
        if (window.JobPanel && window.JobPanel.trackFormChanges) {
            window.JobPanel.trackFormChanges();
        }
    };

    /**
     * Set up recurrence end mode toggle (Never/After N/On date)
     */
    function initRecurrenceEndModeToggle(rootEl) {
        const endModeSelect = rootEl.querySelector('#recurrence-end-mode');
        const countContainer = rootEl.querySelector('#recurrence-count-container');
        const untilContainer = rootEl.querySelector('#recurrence-until-container');
        const countInput = rootEl.querySelector('#recurrence-count');
        const untilInput = rootEl.querySelector('#recurrence-until');

        if (!endModeSelect || !countContainer || !untilContainer) return;

        // Guard against duplicate listeners
        if (GTS.isElInitialized(endModeSelect, 'end_mode_toggle')) return;
        GTS.markElInitialized(endModeSelect, 'end_mode_toggle');

        function toggleEndModeFields() {
            const mode = endModeSelect.value;

            if (mode === 'never') {
                countContainer.style.display = 'none';
                untilContainer.style.display = 'none';
                // Clear values so they don't get submitted
                if (countInput) countInput.value = '';
                if (untilInput) untilInput.value = '';
            } else if (mode === 'after_count') {
                countContainer.style.display = '';
                untilContainer.style.display = 'none';
                // Set default count if empty
                if (countInput && !countInput.value) countInput.value = '12';
                if (untilInput) untilInput.value = '';
            } else if (mode === 'on_date') {
                countContainer.style.display = 'none';
                untilContainer.style.display = '';
                if (countInput) countInput.value = '';
            }
        }

        // Set initial state
        toggleEndModeFields();

        // Add change listener
        endModeSelect.addEventListener('change', toggleEndModeFields);
    }

    // ========================================================================
    // HTMX EVENT INTEGRATION
    // ========================================================================

    // Initialize form partial when content is loaded via HTMX
    GTS.onHtmxLoad(function(evt) {
        const target = evt.detail.elt;
        if (target && target.querySelector && target.querySelector('form[data-gts-job-form]')) {
            window.initJobFormPartial(target);
        }
    });

    GTS.onHtmxAfterSwap(function(evt) {
        const target = evt.detail.target;
        if (target && target.querySelector && target.querySelector('form[data-gts-job-form]')) {
            window.initJobFormPartial(target);
        }
    });

})();
