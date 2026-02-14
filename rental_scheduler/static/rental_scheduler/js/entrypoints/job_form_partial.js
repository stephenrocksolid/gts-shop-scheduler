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
                    
                    // Close panel/workspace tab unless we're switching jobs or printing
                    if (window.JobPanel && !window.JobPanel.isSwitchingJobs && !window.JobPanel.isPrinting) {
                        const currentJobId = window.JobPanel.currentJobId;
                        const currentDraftId = window.JobPanel.currentDraftId;
                        const activeJobId = window.JobWorkspace ? window.JobWorkspace.activeJobId : null;

                        // Prefer closing by real job ID if present in workspace
                        if (currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob && window.JobWorkspace.hasJob(currentJobId)) {
                            window.JobWorkspace.closeJob(currentJobId);
                        } else if (currentDraftId && window.JobWorkspace && window.JobWorkspace.hasJob && window.JobWorkspace.hasJob(currentDraftId)) {
                            // Draft (minimized new job) flow: close/remove the draft tab on successful save
                            window.JobWorkspace.closeJob(currentDraftId);
                            window.JobPanel.currentDraftId = null;
                        } else if (activeJobId && window.JobWorkspace && window.JobWorkspace.hasJob && window.JobWorkspace.hasJob(activeJobId)) {
                            // Fallback: close the active workspace tab if it exists
                            window.JobWorkspace.closeJob(activeJobId);
                        } else {
                            // Fallback: just close the panel
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

                // Belt-and-suspenders: sync header calendar → hidden form field before validation
                // This prevents "calendar missing" errors when UI shows a selected calendar
                if (window.syncHiddenCalendarFromHeader) {
                    window.syncHiddenCalendarFromHeader();
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
            function resolveJobIdFromEvent(event, fallbackJobId, form) {
                let actualJobId = fallbackJobId;

                // 1. Try to get from HX-Trigger header (jobSaved event contains jobId)
                if (event.detail.xhr) {
                    const triggerHeader = event.detail.xhr.getResponseHeader('HX-Trigger');
                    if (triggerHeader) {
                        try {
                            const triggerData = JSON.parse(triggerHeader);
                            if (triggerData.jobSaved && triggerData.jobSaved.jobId) {
                                actualJobId = triggerData.jobSaved.jobId;
                                console.log('Got job ID from HX-Trigger:', actualJobId);
                            }
                        } catch (e) {
                            console.log('Could not parse HX-Trigger header');
                        }
                    }

                    // 2. Try to extract from response HTML (OOB swap includes job_id input)
                    if (!actualJobId || actualJobId === '0') {
                        const responseText = event.detail.xhr.responseText;
                        const match = responseText.match(/name="job_id"\s+value="(\d+)"/);
                        if (match && match[1]) {
                            actualJobId = match[1];
                            console.log('Got job ID from response HTML:', actualJobId);
                        }
                    }
                }

                // 3. Fallback: check form's hidden input (for existing jobs)
                if ((!actualJobId || actualJobId === '0') && form) {
                    const jobIdInput = form.querySelector('input[name="job_id"]');
                    if (jobIdInput && jobIdInput.value) {
                        actualJobId = jobIdInput.value;
                    }
                }

                return actualJobId;
            }

            function stampOpenJobOnCurrentUrl(jobId) {
                if (!jobId || jobId === '0') return;
                if (!window.history || !window.history.replaceState) return;
                try {
                    const p = new URLSearchParams(window.location.search || '');
                    p.set('open_job', String(jobId));
                    const newUrl = window.location.pathname + '?' + p.toString() + window.location.hash;
                    window.history.replaceState({}, '', newUrl);
                } catch (_) { }
            }

            function saveJobThenNavigate(form, jobId, triggerBtn, buildUrl) {
                if (window.JobPanel) {
                    window.JobPanel.isPrinting = true;
                }

                const originalText = triggerBtn ? triggerBtn.textContent : '';
                if (triggerBtn) {
                    triggerBtn.textContent = 'Saving...';
                    triggerBtn.disabled = true;
                }

                const hxPost = form.getAttribute('hx-post');
                if (hxPost) {
                    const handleAfterRequest = function(event) {
                        const actualJobId = resolveJobIdFromEvent(event, jobId, form);

                        if (event.detail.successful) {
                            if (window.JobPanel && window.JobPanel.clearUnsavedChanges) {
                                window.JobPanel.clearUnsavedChanges();
                            }

                            document.body.removeEventListener('htmx:afterRequest', handleAfterRequest);

                            if (!actualJobId || actualJobId === '0') {
                                alert('Job saved but could not determine job ID. Please try again.');
                                if (triggerBtn) {
                                    triggerBtn.textContent = originalText;
                                    triggerBtn.disabled = false;
                                }
                                if (window.JobPanel) {
                                    window.JobPanel.isPrinting = false;
                                }
                                return;
                            }

                            if (window.JobPanel) {
                                window.JobPanel.isPrinting = false;
                            }

                            window.location.href = buildUrl(actualJobId);
                        } else {
                            if (window.JobPanel) {
                                window.JobPanel.isPrinting = false;
                            }
                            alert('Failed to save job. Please check required fields and try again.');
                            if (triggerBtn) {
                                triggerBtn.textContent = originalText;
                                triggerBtn.disabled = false;
                            }
                            document.body.removeEventListener('htmx:afterRequest', handleAfterRequest);
                        }
                    };

                    document.body.addEventListener('htmx:afterRequest', handleAfterRequest);
                    htmx.trigger(form, 'submit');
                }
            }

            // Use event delegation - attach to document body so it works for all future buttons
            document.body.addEventListener('click', function(e) {
                // Save & Create WO button
                const saveAndCreateBtn = e.target.closest('.save-and-create-wo-btn');
                if (saveAndCreateBtn && !saveAndCreateBtn.disabled) {
                    GTS.dom.stop(e);
                    const form = saveAndCreateBtn.closest('form');
                    if (form && GTS.urls && GTS.urls.workOrderNew) {
                        const jobIdInput = form.querySelector('input[name="job_id"]');
                        const jobId = jobIdInput ? jobIdInput.value : '0';
                        saveJobThenNavigate(form, jobId, saveAndCreateBtn, function(actualJobId) {
                            stampOpenJobOnCurrentUrl(actualJobId);
                            var nextUrl = window.location.pathname + window.location.search;
                            return GTS.urls.workOrderNew({ job: actualJobId, next: nextUrl });
                        });
                    }
                }

                // Create WO (existing job)
                const createBtn = e.target.closest('[data-wo-action="create"]');
                if (createBtn && !createBtn.disabled) {
                    GTS.dom.stop(e);
                    const form = createBtn.closest('form');
                    const jobId = createBtn.getAttribute('data-job-id') || '0';
                    if (form && GTS.urls && GTS.urls.workOrderNew) {
                        const hasUnsaved = window.JobPanel && window.JobPanel.hasUnsavedChanges
                            ? (typeof window.JobPanel.hasUnsavedChanges === 'function'
                                ? window.JobPanel.hasUnsavedChanges()
                                : false)
                            : false;
                        if (hasUnsaved || !jobId || jobId === '0') {
                            saveJobThenNavigate(form, jobId, createBtn, function(actualJobId) {
                                stampOpenJobOnCurrentUrl(actualJobId);
                                var nextUrl = window.location.pathname + window.location.search;
                                return GTS.urls.workOrderNew({ job: actualJobId, next: nextUrl });
                            });
                        } else {
                            stampOpenJobOnCurrentUrl(jobId);
                            var nextUrl = window.location.pathname + window.location.search;
                            window.location.href = GTS.urls.workOrderNew({ job: jobId, next: nextUrl });
                        }
                    }
                }

                // Edit WO
                const editBtn = e.target.closest('[data-wo-action="edit"]');
                if (editBtn && !editBtn.disabled) {
                    GTS.dom.stop(e);
                    const woId = editBtn.getAttribute('data-wo-id');
                    if (woId && GTS.urls && GTS.urls.workOrderEdit) {
                        const form = editBtn.closest('form');
                        let _jobId = '0';
                        try {
                            const jobIdInput = form ? form.querySelector('input[name="job_id"]') : null;
                            _jobId = jobIdInput ? (jobIdInput.value || '0') : '0';
                        } catch (_) { }
                        saveJobThenNavigate(form, _jobId, editBtn, function(actualJobId) {
                            stampOpenJobOnCurrentUrl(actualJobId || _jobId);
                            var nextUrl = window.location.pathname + window.location.search;
                            return GTS.urls.withQuery(GTS.urls.workOrderEdit(woId), { next: nextUrl });
                        });
                    }
                }

                // Print WO (PDF)
                const printWoBtn = e.target.closest('[data-wo-action="print"]');
                if (printWoBtn && !printWoBtn.disabled) {
                    GTS.dom.stop(e);
                    const woId = printWoBtn.getAttribute('data-wo-id');
                    if (woId && GTS.urls && GTS.urls.workOrderPdf) {
                        window.open(GTS.urls.workOrderPdf(woId), '_blank');
                    }
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
             * Detect recurrence state from the job form DOM
             * @returns {Object} { isRecurring, isInstance, isParent }
             */
            function detectRecurrenceState() {
                var recurCheckbox = document.querySelector('#job-panel #recurrence-enabled');
                if (!recurCheckbox) {
                    return { isRecurring: false, isInstance: false, isParent: false };
                }
                
                var isRecurring = recurCheckbox.checked === true;
                var isInstance = isRecurring && recurCheckbox.disabled === true;
                var isParent = isRecurring && recurCheckbox.disabled !== true;
                
                return { isRecurring: isRecurring, isInstance: isInstance, isParent: isParent };
            }

            /**
             * Show recurring delete modal
             * @param {string} jobId
             * @param {boolean} isInstance - true if deleting an instance, false if deleting parent
             */
            function showRecurringDeleteModal(jobId, isInstance) {
                // Create overlay
                var overlay = document.createElement('div');
                overlay.id = 'recurring-delete-overlay';
                overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:10000;display:flex;align-items:center;justify-content:center;';
                
                // Create dialog
                var dialog = document.createElement('div');
                dialog.style.cssText = 'background:white;border-radius:8px;padding:24px;max-width:500px;width:90%;box-shadow:0 20px 25px -5px rgba(0,0,0,0.1);';
                
                // Build content based on whether it's an instance or parent
                var title, body, buttons;
                
                if (isInstance) {
                    title = 'Delete recurring event?';
                    body = '<p class="text-gray-700 mb-2">This event is part of a series. What would you like to delete?</p><p class="text-sm text-gray-500">Past events won\'t be deleted.</p>';
                    buttons = [
                        { text: 'Cancel', scope: null, className: 'bg-gray-100 hover:bg-gray-200 text-gray-800' },
                        { text: 'Delete this event only', scope: 'this_only', className: 'bg-red-600 hover:bg-red-700 text-white' },
                        { text: 'Delete this and future events', scope: 'this_and_future', className: 'bg-red-600 hover:bg-red-700 text-white' }
                    ];
                } else {
                    title = 'Delete recurring series?';
                    body = '<p class="text-gray-700 mb-2">This is the series template. Choose what should happen:</p>';
                    buttons = [
                        { text: 'Cancel', scope: null, className: 'bg-gray-100 hover:bg-gray-200 text-gray-800' },
                        { text: 'Keep this event, delete future events', scope: 'this_and_future', className: 'bg-red-600 hover:bg-red-700 text-white' },
                        { text: 'Delete entire series', scope: 'all', className: 'bg-red-600 hover:bg-red-700 text-white' }
                    ];
                }
                
                // Check for unsaved changes
                var hasUnsavedChanges = window.JobPanel && window.JobPanel.hasUnsavedChanges
                    ? (typeof window.JobPanel.hasUnsavedChanges === 'function'
                        ? window.JobPanel.hasUnsavedChanges()
                        : false)
                    : false;
                
                if (hasUnsavedChanges) {
                    body += '<p class="text-sm text-yellow-600 mt-3 font-medium">⚠️ You have unsaved changes. Deleting will discard them.</p>';
                }
                
                // Build HTML
                dialog.innerHTML = '<h2 class="text-xl font-semibold mb-4 text-gray-900">' + title + '</h2>' +
                    '<div class="mb-6">' + body + '</div>' +
                    '<div id="recurring-delete-buttons" class="flex flex-col gap-2"></div>';
                
                overlay.appendChild(dialog);
                document.body.appendChild(overlay);
                
                // Add buttons
                var buttonsContainer = dialog.querySelector('#recurring-delete-buttons');
                buttons.forEach(function(btnConfig, index) {
                    var btn = document.createElement('button');
                    btn.textContent = btnConfig.text;
                    btn.className = 'px-4 py-2 rounded font-medium transition-colors ' + btnConfig.className;
                    btn.setAttribute('data-scope', btnConfig.scope || '');
                    
                    btn.addEventListener('click', function() {
                        if (btnConfig.scope) {
                            performRecurringDelete(jobId, btnConfig.scope);
                        }
                        closeRecurringDeleteModal();
                    });
                    
                    buttonsContainer.appendChild(btn);
                    
                    // Focus first button (Cancel)
                    if (index === 0) {
                        setTimeout(function() { btn.focus(); }, 50);
                    }
                });
                
                // ESC to close
                var escHandler = function(e) {
                    if (e.key === 'Escape') {
                        closeRecurringDeleteModal();
                        document.removeEventListener('keydown', escHandler);
                    }
                };
                document.addEventListener('keydown', escHandler);
                
                // Click overlay to close
                overlay.addEventListener('click', function(e) {
                    if (e.target === overlay) {
                        closeRecurringDeleteModal();
                    }
                });
            }

            /**
             * Close recurring delete modal
             */
            function closeRecurringDeleteModal() {
                var overlay = document.getElementById('recurring-delete-overlay');
                if (overlay) {
                    overlay.remove();
                }
            }

            /**
             * Perform recurring delete with the specified scope
             * @param {string} jobId
             * @param {string} scope - 'this_only', 'this_and_future', or 'all'
             */
            function performRecurringDelete(jobId, scope) {
                fetch(GTS.urls.jobDeleteRecurring(jobId), {
                    method: 'POST',
                    headers: GTS.csrf.headers({ 'Content-Type': 'application/json' }),
                    body: JSON.stringify({ delete_scope: scope })
                })
                    .then(function(response) { return response.json(); })
                    .then(function(data) {
                        if (data.success) {
                            var count = data.deleted_count || 0;
                            var message = count === 1 ? 'Deleted 1 event' : 'Deleted ' + count + ' events';
                            GTS.showToast(message, 'success');
                            
                            // Close panel
                            if (window.JobPanel) {
                                window.JobPanel.close(true); // true = skip unsaved check
                            }
                            
                            // Refresh calendar
                            if (window.jobCalendar && window.jobCalendar.calendar) {
                                window.jobCalendar.calendar.refetchEvents();
                            }
                        } else {
                            console.error('Failed to delete job:', data.error);
                            GTS.showToast('Failed to delete: ' + (data.error || 'Unknown error'), 'error');
                        }
                    })
                    .catch(function(error) {
                        console.error('Error deleting job:', error);
                        GTS.showToast('Error deleting job', 'error');
                    });
            }

            /**
             * Delete job via API (handles both recurring and non-recurring)
             */
            function deleteJob(jobId) {
                // Detect if this is a recurring job
                var recurrenceState = detectRecurrenceState();
                
                if (recurrenceState.isRecurring) {
                    // Show recurring delete modal
                    showRecurringDeleteModal(jobId, recurrenceState.isInstance);
                } else {
                    // Non-recurring job - use simple confirm
                    if (confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
                        fetch(GTS.urls.jobDelete(jobId), {
                            method: 'POST',
                            headers: GTS.csrf.headers({ 'Content-Type': 'application/json' })
                        })
                            .then(function(response) { return response.json(); })
                            .then(function(data) {
                                if (data.success) {
                                    GTS.showToast('Job deleted', 'success');
                                    
                                    // Close panel and refresh calendar
                                    if (window.JobPanel) {
                                        window.JobPanel.close();
                                    }
                                    if (window.jobCalendar && window.jobCalendar.calendar) {
                                        window.jobCalendar.calendar.refetchEvents();
                                    }
                                } else {
                                    console.error('Failed to delete job:', data.error);
                                    GTS.showToast('Failed to delete job', 'error');
                                }
                            })
                            .catch(function(error) {
                                console.error('Error deleting job:', error);
                                GTS.showToast('Error deleting job', 'error');
                            });
                    }
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
