/**
 * Calendar Job Actions Module
 * 
 * Handles event click → panel/workspace behaviors.
 * Registers: handleEventClick, openJobInPanel, showUnsavedChangesDialog, updateJobStatus
 */
(function() {
    'use strict';

    GTS.calendar.register('job_actions', function(proto) {
        /**
         * Handle event click to open edit form
         */
        proto.handleEventClick = function(info) {
            var self = this;
            try {
                var extendedProps = info.event.extendedProps || {};
                var eventType = extendedProps.type;
                var jobId = extendedProps.job_id;

                // Check if this is a call reminder event (job-related or standalone)
                if (eventType === 'call_reminder' || eventType === 'standalone_call_reminder') {
                    this.showCallReminderPanel(info.event);
                } else if (eventType === 'virtual_job') {
                    // Virtual occurrence - materialize it first, then open
                    this.materializeAndOpenJob(info.event);
                } else if (eventType === 'virtual_call_reminder') {
                    // Virtual call reminder - materialize the job first, then show reminder panel
                    this.materializeAndShowCallReminder(info.event);
                } else if (jobId && window.JobPanel) {
                    // Check if there are unsaved changes
                    var hasChanges = window.JobPanel.hasUnsavedChanges && window.JobPanel.hasUnsavedChanges();
                    if (hasChanges) {
                        // Set flag to prevent panel from auto-closing
                        window.JobPanel.isSwitchingJobs = true;
                        // Save the form first
                        window.JobPanel.saveForm(function() {
                            // After saving, add to workspace if it has a job ID
                            var currentJobId = window.JobPanel.currentJobId;
                            if (currentJobId && window.JobWorkspace && !window.JobWorkspace.hasJob(currentJobId)) {
                                // Get job details from the form
                                var form = document.querySelector('#job-panel .panel-body form');
                                var businessNameEl = form ? form.querySelector('input[name="business_name"]') : null;
                                var contactNameEl = form ? form.querySelector('input[name="contact_name"]') : null;
                                var trailerColorEl = form ? form.querySelector('input[name="trailer_color"]') : null;
                                var businessName = (businessNameEl && businessNameEl.value) || (contactNameEl && contactNameEl.value) || 'Unnamed Job';
                                var trailerColor = (trailerColorEl && trailerColorEl.value) || '';

                                // Add to workspace as minimized (don't make it active)
                                window.JobWorkspace.addJobMinimized(currentJobId, {
                                    customerName: businessName,
                                    trailerColor: trailerColor,
                                    calendarColor: '#3B82F6'
                                });
                            }

                            // Now open the new job
                            self._openJobFromEvent(info.event, jobId);

                            // Clear the switching flag after a delay to allow new form to load
                            setTimeout(function() {
                                window.JobPanel.isSwitchingJobs = false;
                            }, 500);
                        });
                    } else {
                        // No unsaved changes, open directly
                        self._openJobFromEvent(info.event, jobId);
                    }
                } else {
                    console.error('JobPanel not available or job ID missing');
                    this.showError('Unable to open event for editing. Please try again.');
                }
            } catch (error) {
                console.error('JobCalendar: Error handling single click', error);
                this.showError('Unable to open event for editing. Please try again.');
            }
        };

        /**
         * Open a job from an event
         * @private
         */
        proto._openJobFromEvent = function(event, jobId) {
            var props = event.extendedProps || {};
            if (window.JobWorkspace) {
                // Check if the clicked job is already in the workspace
                if (window.JobWorkspace.hasJob(jobId)) {
                    // Job is in workspace, switch to it
                    window.JobWorkspace.switchToJob(jobId);
                } else {
                    // Job is not in workspace, open it fresh
                    window.JobWorkspace.openJob(jobId, {
                        customerName: props.display_name || props.business_name || props.contact_name || event.title || 'Job',
                        trailerColor: props.trailer_color || '',
                        calendarColor: props.calendar_color || '#3B82F6'
                    });
                }
            } else {
                // Fallback to direct panel opening if workspace not available
                this.openJobInPanel(event, jobId);
            }
        };

        /**
         * Open a job in the panel
         */
        proto.openJobInPanel = function(event, jobId) {
            var props = event.extendedProps;

            // Load job edit form in panel
            window.JobPanel.setTitle('Edit Job');
            window.JobPanel.load('/jobs/new/partial/?edit=' + jobId);

            // Track current job ID for workspace integration
            if (window.JobPanel.setCurrentJobId) {
                window.JobPanel.setCurrentJobId(jobId);
            }

            // Update minimize button after a short delay to ensure panel is ready
            setTimeout(function() {
                if (window.JobPanel.updateMinimizeButton) {
                    window.JobPanel.updateMinimizeButton();
                }
            }, 100);
        };

        /**
         * Show dialog for unsaved changes with options to save, minimize, or cancel
         */
        proto.showUnsavedChangesDialog = function(onProceed) {
            var overlay = document.createElement('div');
            overlay.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 10000; animation: fadeIn 0.2s ease;';

            var dialog = document.createElement('div');
            dialog.style.cssText = 'background: white; border-radius: 12px; padding: 24px; max-width: 480px; width: 90%; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); animation: slideUp 0.2s ease;';

            dialog.innerHTML = '<div style="display: flex; align-items: start; margin-bottom: 16px;">' +
                '<svg style="width: 24px; height: 24px; color: #f59e0b; margin-right: 12px; flex-shrink: 0;" fill="none" stroke="currentColor" viewBox="0 0 24 24">' +
                '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>' +
                '<div><h3 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 600; color: #111827;">Unsaved Changes</h3>' +
                '<p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">You have unsaved changes. What would you like to do?</p></div></div>' +
                '<div style="display: flex; flex-direction: column; gap: 8px;">' +
                '<button id="dialog-save-btn" style="width: 100%; padding: 10px 16px; background: #3b82f6; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;">Save and Open New Job</button>' +
                '<button id="dialog-minimize-btn" style="width: 100%; padding: 10px 16px; background: #f3f4f6; color: #374151; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;">Minimize to Workspace</button>' +
                '<button id="dialog-discard-btn" style="width: 100%; padding: 10px 16px; background: #fee2e2; color: #dc2626; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;">Discard Changes</button>' +
                '<button id="dialog-cancel-btn" style="width: 100%; padding: 10px 16px; background: white; color: #6b7280; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;">Cancel</button>' +
                '</div>';

            // Add animations
            var style = document.createElement('style');
            style.textContent = '@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } } @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }';
            document.head.appendChild(style);

            overlay.appendChild(dialog);
            document.body.appendChild(overlay);

            // Get buttons
            var saveBtn = dialog.querySelector('#dialog-save-btn');
            var minimizeBtn = dialog.querySelector('#dialog-minimize-btn');
            var discardBtn = dialog.querySelector('#dialog-discard-btn');
            var cancelBtn = dialog.querySelector('#dialog-cancel-btn');

            // Button hover effects
            saveBtn.addEventListener('mouseenter', function() { saveBtn.style.background = '#2563eb'; });
            saveBtn.addEventListener('mouseleave', function() { saveBtn.style.background = '#3b82f6'; });
            minimizeBtn.addEventListener('mouseenter', function() { minimizeBtn.style.background = '#e5e7eb'; });
            minimizeBtn.addEventListener('mouseleave', function() { minimizeBtn.style.background = '#f3f4f6'; });
            discardBtn.addEventListener('mouseenter', function() { discardBtn.style.background = '#fecaca'; });
            discardBtn.addEventListener('mouseleave', function() { discardBtn.style.background = '#fee2e2'; });
            cancelBtn.addEventListener('mouseenter', function() { cancelBtn.style.background = '#f9fafb'; cancelBtn.style.borderColor = '#9ca3af'; });
            cancelBtn.addEventListener('mouseleave', function() { cancelBtn.style.background = 'white'; cancelBtn.style.borderColor = '#d1d5db'; });

            // Close dialog function
            var closeDialog = function() {
                overlay.remove();
                style.remove();
            };

            // Save and proceed
            saveBtn.addEventListener('click', function() {
                if (window.JobPanel.saveForm) {
                    window.JobPanel.saveForm(function() {
                        closeDialog();
                        onProceed();
                    });
                } else {
                    closeDialog();
                    onProceed();
                }
            });

            // Minimize to workspace
            minimizeBtn.addEventListener('click', function() {
                var currentJobId = window.JobPanel.currentJobId;
                if (currentJobId && window.JobWorkspace) {
                    if (window.JobPanel.saveForm) {
                        window.JobPanel.saveForm(function() {
                            window.JobWorkspace.minimizeJob(currentJobId);
                            closeDialog();
                            onProceed();
                        });
                    } else {
                        window.JobWorkspace.minimizeJob(currentJobId);
                        closeDialog();
                        onProceed();
                    }
                } else {
                    closeDialog();
                    onProceed();
                }
            });

            // Discard changes and proceed
            discardBtn.addEventListener('click', function() {
                closeDialog();
                onProceed();
            });

            // Cancel - don't open new job
            cancelBtn.addEventListener('click', closeDialog);

            // ESC key to cancel
            var escHandler = function(e) {
                if (e.key === 'Escape') {
                    closeDialog();
                    document.removeEventListener('keydown', escHandler);
                }
            };
            document.addEventListener('keydown', escHandler);

            // Click overlay to cancel
            overlay.addEventListener('click', function(e) {
                if (e.target === overlay) closeDialog();
            });
        };

        /**
         * Update job status via API
         */
        proto.updateJobStatus = function(jobId, newStatus) {
            var self = this;
            var csrfToken = this.getCSRFToken();

            fetch('/rental_scheduler/api/jobs/' + jobId + '/update-status/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ status: newStatus })
            })
                .then(function(response) {
                    if (!response.ok) {
                        return response.text().then(function(text) {
                            console.error('JobCalendar: Status update failed', response.status, text);
                            throw new Error('HTTP ' + response.status + ': ' + text);
                        });
                    }
                    return response.json();
                })
                .then(function(data) {
                    if (data.success) {
                        self.refreshCalendar();
                        self.showToast('Job status updated successfully', 'success');
                    } else {
                        self.showToast('Error updating job status', 'error');
                    }
                })
                .catch(function(error) {
                    console.error('JobCalendar: Error updating status', error);
                    self.showToast('Error updating job status', 'error');
                });
        };
    });

})();
