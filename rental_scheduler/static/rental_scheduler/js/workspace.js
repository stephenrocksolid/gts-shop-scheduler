/**
 * Job Workspace - Manages open jobs in a bottom tab bar
 * Allows users to open multiple jobs from calendar, minimize them, and switch between them
 * VERSION: 1.0 - Initial implementation
 */

(function () {
    'use strict';

    const STORAGE_KEY = 'gts-job-workspace';
    const MAX_TABS = 10; // Limit number of open jobs

    class JobWorkspace {
        constructor() {
            this.openJobs = new Map(); // jobId -> jobData
            this.activeJobId = null;
            this.barElement = null;
            this.tabsContainer = null;

            this.initialize();
        }

        /**
         * Initialize the workspace
         */
        initialize() {
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.init());
            } else {
                this.init();
            }
        }

        init() {
            this.barElement = document.getElementById('workspace-bar');
            this.tabsContainer = document.getElementById('workspace-tabs');

            if (!this.barElement || !this.tabsContainer) {
                console.warn('JobWorkspace: Required elements not found');
                return;
            }

            // Load saved workspace state
            this.loadFromStorage();

            // Render initial state
            this.render();

            // Set up global access
            window.JobWorkspace = this;
        }

        /**
         * Open a job and add it to workspace
         */
        openJob(jobId, jobData) {
            // Check if already open
            if (this.openJobs.has(jobId)) {
                // Just make it active and show panel
                this.switchToJob(jobId);
                return;
            }

            // Check max tabs limit
            if (this.openJobs.size >= MAX_TABS) {
                if (window.showToast) {
                    window.showToast(`Maximum ${MAX_TABS} jobs can be open at once`, 'warning');
                }
                return;
            }

            // Add to workspace
            this.openJobs.set(jobId, {
                jobId: jobId,
                customerName: jobData.customerName || 'No Name',
                trailerColor: jobData.trailerColor || '',
                calendarColor: jobData.calendarColor || '#3B82F6',
                isMinimized: false,
                timestamp: Date.now()
            });

            this.activeJobId = jobId;

            // Save and render
            this.saveToStorage();
            this.render();

            // Load job edit form in panel
            if (window.JobPanel) {
                window.JobPanel.setTitle('Edit Job');
                window.JobPanel.load(`/jobs/new/partial/?edit=${jobId}`);
                window.JobPanel.setCurrentJobId(jobId);

                // Update minimize button after a short delay to ensure panel is ready
                setTimeout(() => {
                    if (window.JobPanel.updateMinimizeButton) {
                        window.JobPanel.updateMinimizeButton();
                    }
                }, 100);
            }
        }

        /**
         * Add a job to workspace in minimized state (doesn't make it active)
         */
        addJobMinimized(jobId, jobData) {
            // Check if already open
            if (this.openJobs.has(jobId)) {
                return; // Already exists, don't modify
            }

            // Check max tabs limit
            if (this.openJobs.size >= MAX_TABS) {
                if (window.showToast) {
                    window.showToast(`Maximum ${MAX_TABS} jobs can be open at once`, 'warning');
                }
                return;
            }

            // Add to workspace as minimized
            this.openJobs.set(jobId, {
                jobId: jobId,
                customerName: jobData.customerName || 'No Name',
                trailerColor: jobData.trailerColor || '',
                calendarColor: jobData.calendarColor || '#3B82F6',
                isMinimized: true,  // Keep it minimized
                timestamp: Date.now()
            });

            // Save and render
            this.saveToStorage();
            this.render();
        }

        /**
         * Minimize a job (keep in workspace but hide panel)
         */
        minimizeJob(jobId) {
            const job = this.openJobs.get(jobId);
            if (!job) return;

            job.isMinimized = true;
            this.activeJobId = null;

            // Hide the panel
            if (window.JobPanel) {
                window.JobPanel.close(true); // Skip unsaved check since we're minimizing
            }

            this.saveToStorage();
            this.render();
        }

        /**
         * Close a job completely (remove from workspace)
         */
        closeJob(jobId) {
            if (!this.openJobs.has(jobId)) return;

            this.openJobs.delete(jobId);

            // If this was the active job, close the panel
            if (this.activeJobId === jobId) {
                this.activeJobId = null;
                if (window.JobPanel) {
                    window.JobPanel.close(true);
                }
            }

            // Update minimize button visibility
            if (window.JobPanel && window.JobPanel.updateMinimizeButton) {
                window.JobPanel.updateMinimizeButton();
            }

            this.saveToStorage();
            this.render();
        }

        /**
         * Switch to a job (restore from minimized state)
         */
        switchToJob(jobId) {
            const job = this.openJobs.get(jobId);
            if (!job) return;

            // Check if there are unsaved changes
            if (window.JobPanel && window.JobPanel.hasUnsavedChanges && window.JobPanel.hasUnsavedChanges()) {
                // Save the form first
                window.JobPanel.saveForm(() => {
                    // After saving, add to workspace if it has a job ID
                    const currentJobId = window.JobPanel.currentJobId;
                    if (currentJobId && !this.hasJob(currentJobId)) {
                        // Get job details from the form
                        const form = document.querySelector('#job-panel .panel-body form');
                        const businessName = form?.querySelector('input[name="business_name"]')?.value ||
                            form?.querySelector('input[name="contact_name"]')?.value ||
                            'Unnamed Job';
                        const trailerColor = form?.querySelector('input[name="trailer_color"]')?.value || '';

                        // Add to workspace as minimized
                        this.addJobMinimized(currentJobId, {
                            customerName: businessName,
                            trailerColor: trailerColor,
                            calendarColor: '#3B82F6'
                        });
                    }

                    // Now switch to the selected job
                    this.doSwitchToJob(jobId);
                });
            } else {
                // No unsaved changes, switch directly
                this.doSwitchToJob(jobId);
            }
        }

        /**
         * Actually perform the job switch (called after unsaved check)
         */
        doSwitchToJob(jobId) {
            const job = this.openJobs.get(jobId);
            if (!job) return;

            job.isMinimized = false;
            this.activeJobId = jobId;

            // Load job edit form in panel
            if (window.JobPanel) {
                window.JobPanel.setTitle('Edit Job');
                window.JobPanel.load(`/jobs/new/partial/?edit=${jobId}`);
                window.JobPanel.setCurrentJobId(jobId);

                // Update minimize button after a short delay to ensure panel is ready
                setTimeout(() => {
                    if (window.JobPanel.updateMinimizeButton) {
                        window.JobPanel.updateMinimizeButton();
                    }
                }, 100);
            }

            this.saveToStorage();
            this.render();
        }

        /**
         * Check if a job is in the workspace
         */
        hasJob(jobId) {
            return this.openJobs.has(jobId);
        }

        /**
         * Get the currently active job ID
         */
        getActiveJobId() {
            return this.activeJobId;
        }

        /**
         * Close all jobs
         */
        closeAll() {
            if (this.openJobs.size === 0) return;

            if (confirm('Close all open jobs?')) {
                this.openJobs.clear();
                this.activeJobId = null;

                if (window.JobPanel) {
                    window.JobPanel.close(true);
                }

                this.saveToStorage();
                this.render();
            }
        }

        /**
         * Render the workspace tabs
         */
        render() {
            if (!this.tabsContainer || !this.barElement) return;

            // If no jobs, hide the bar
            if (this.openJobs.size === 0) {
                this.barElement.classList.add('hidden');
                document.body.classList.remove('workspace-active');
                return;
            }

            // Show the bar
            this.barElement.classList.remove('hidden');
            document.body.classList.add('workspace-active');

            // Clear existing tabs
            this.tabsContainer.innerHTML = '';

            // Sort jobs by timestamp (oldest first)
            const sortedJobs = Array.from(this.openJobs.values())
                .sort((a, b) => a.timestamp - b.timestamp);

            // Create tabs
            sortedJobs.forEach(job => {
                const tab = this.createTab(job);
                this.tabsContainer.appendChild(tab);
            });

            // Add "Close All" button if multiple jobs
            if (this.openJobs.size > 1) {
                const closeAllBtn = this.createCloseAllButton();
                this.tabsContainer.appendChild(closeAllBtn);
            }
        }

        /**
         * Create a tab element for a job
         */
        createTab(job) {
            const tab = document.createElement('div');
            tab.className = 'workspace-tab';
            tab.dataset.jobId = job.jobId; // Store job ID for tooltip

            // Add active/minimized state classes
            if (job.jobId === this.activeJobId && !job.isMinimized) {
                tab.classList.add('active');
            }
            if (job.isMinimized) {
                tab.classList.add('minimized');
            }

            // Color indicator (small circle)
            const colorIndicator = document.createElement('div');
            colorIndicator.className = 'workspace-tab-color';
            colorIndicator.style.backgroundColor = job.calendarColor;
            tab.appendChild(colorIndicator);

            // Customer name
            const name = document.createElement('span');
            name.className = 'workspace-tab-name';
            name.textContent = job.customerName;
            name.title = job.customerName; // Tooltip for long names
            tab.appendChild(name);

            // Close button
            const closeBtn = document.createElement('button');
            closeBtn.className = 'workspace-tab-close';
            closeBtn.innerHTML = '×';
            closeBtn.title = 'Close job';
            closeBtn.onclick = (e) => {
                e.stopPropagation();
                this.closeJob(job.jobId);
            };
            tab.appendChild(closeBtn);

            // Tooltip hover state
            let tooltipTimeout = null;

            // Add hover handlers for tooltip
            tab.addEventListener('mouseenter', (e) => {
                // Don't show tooltip when hovering over close button
                if (e.target === closeBtn || e.target.parentElement === closeBtn) {
                    return;
                }

                // Set a 500ms delay before showing the tooltip
                tooltipTimeout = setTimeout(() => {
                    this.showWorkspaceTabTooltip(job.jobId, tab);
                }, 500);
            });

            tab.addEventListener('mouseleave', () => {
                // Clear the timeout if user stops hovering before delay completes
                if (tooltipTimeout) {
                    clearTimeout(tooltipTimeout);
                    tooltipTimeout = null;
                }

                // Hide the tooltip
                if (window.jobCalendar) {
                    window.jobCalendar.hideEventTooltip();
                }
            });

            // Click to switch/restore
            tab.onclick = () => {
                if (this.activeJobId === job.jobId && !job.isMinimized) {
                    // Already active, minimize it
                    this.minimizeJob(job.jobId);
                } else {
                    // Switch to this job
                    this.switchToJob(job.jobId);
                }
            };

            return tab;
        }

        /**
         * Show tooltip for workspace tab by fetching job details
         */
        async showWorkspaceTabTooltip(jobId, tabElement) {
            try {
                const response = await fetch(`/api/jobs/${jobId}/detail/`);
                if (!response.ok) {
                    console.error('Failed to fetch job details');
                    return;
                }

                const jobData = await response.json();

                const fakeEvent = {
                    title: jobData.display_name || jobData.business_name || 'No Title',
                    start: jobData.start_dt ? new Date(jobData.start_dt) : null,
                    end: jobData.end_dt ? new Date(jobData.end_dt) : null,
                    allDay: !!jobData.all_day,
                    extendedProps: {
                        calendar_name: jobData.calendar_name || '',
                        business_name: jobData.business_name || '',
                        contact_name: jobData.contact_name || '',
                        phone: jobData.phone || '',
                        trailer_details: jobData.trailer_details || '',
                        trailer_color: jobData.trailer_color || '',
                        trailer_serial: jobData.trailer_serial || '',
                        repair_notes: jobData.repair_notes || '',
                        notes: jobData.notes || '',
                        status: jobData.status || '',
                        is_recurring_parent: false,
                        is_multi_day: false
                    }
                };

                if (window.jobCalendar) {
                    window.jobCalendar.showEventTooltip(fakeEvent, tabElement);
                }
            } catch (error) {
                console.error('Error showing workspace tab tooltip:', error);
            }
        }

        /**
         * Create "Close All" button
         */
        createCloseAllButton() {
            const btn = document.createElement('button');
            btn.className = 'workspace-close-all';
            btn.textContent = 'Close All';
            btn.title = 'Close all open jobs';
            btn.onclick = () => this.closeAll();
            return btn;
        }

        /**
         * Show dialog for unsaved changes with options to save, minimize, or cancel
         */
        showUnsavedChangesDialog(onProceed) {
            const overlay = document.createElement('div');
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                animation: fadeIn 0.2s ease;
            `;

            const dialog = document.createElement('div');
            dialog.style.cssText = `
                background: white;
                border-radius: 12px;
                padding: 24px;
                max-width: 480px;
                width: 90%;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                animation: slideUp 0.2s ease;
            `;

            dialog.innerHTML = `
                <div style="display: flex; align-items: start; margin-bottom: 16px;">
                    <svg style="width: 24px; height: 24px; color: #f59e0b; margin-right: 12px; flex-shrink: 0;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                    </svg>
                    <div>
                        <h3 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 600; color: #111827;">Unsaved Changes</h3>
                        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">You have unsaved changes. What would you like to do?</p>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <button id="dialog-save-btn" style="width: 100%; padding: 10px 16px; background: #3b82f6; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;">
                        Save and Switch Job
                    </button>
                    <button id="dialog-minimize-btn" style="width: 100%; padding: 10px 16px; background: #f3f4f6; color: #374151; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;">
                        Minimize to Workspace
                    </button>
                    <button id="dialog-discard-btn" style="width: 100%; padding: 10px 16px; background: #fee2e2; color: #dc2626; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;">
                        Discard Changes
                    </button>
                    <button id="dialog-cancel-btn" style="width: 100%; padding: 10px 16px; background: white; color: #6b7280; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                        Cancel
                    </button>
                </div>
            `;

            // Add animations
            const style = document.createElement('style');
            style.textContent = `
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideUp {
                    from { transform: translateY(20px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);

            overlay.appendChild(dialog);
            document.body.appendChild(overlay);

            // Button hover effects
            const saveBtn = dialog.querySelector('#dialog-save-btn');
            const minimizeBtn = dialog.querySelector('#dialog-minimize-btn');
            const discardBtn = dialog.querySelector('#dialog-discard-btn');
            const cancelBtn = dialog.querySelector('#dialog-cancel-btn');

            saveBtn.addEventListener('mouseenter', () => saveBtn.style.background = '#2563eb');
            saveBtn.addEventListener('mouseleave', () => saveBtn.style.background = '#3b82f6');

            minimizeBtn.addEventListener('mouseenter', () => minimizeBtn.style.background = '#e5e7eb');
            minimizeBtn.addEventListener('mouseleave', () => minimizeBtn.style.background = '#f3f4f6');

            discardBtn.addEventListener('mouseenter', () => discardBtn.style.background = '#fecaca');
            discardBtn.addEventListener('mouseleave', () => discardBtn.style.background = '#fee2e2');

            cancelBtn.addEventListener('mouseenter', () => {
                cancelBtn.style.background = '#f9fafb';
                cancelBtn.style.borderColor = '#9ca3af';
            });
            cancelBtn.addEventListener('mouseleave', () => {
                cancelBtn.style.background = 'white';
                cancelBtn.style.borderColor = '#d1d5db';
            });

            // Close dialog function
            const closeDialog = () => {
                overlay.remove();
                style.remove();
            };

            // Save and proceed
            saveBtn.addEventListener('click', () => {
                if (window.JobPanel.saveForm) {
                    window.JobPanel.saveForm(() => {
                        closeDialog();
                        onProceed();
                    });
                } else {
                    closeDialog();
                    onProceed();
                }
            });

            // Minimize to workspace
            minimizeBtn.addEventListener('click', () => {
                const currentJobId = window.JobPanel.currentJobId;
                if (currentJobId && window.JobWorkspace) {
                    // Save first if there are changes
                    if (window.JobPanel.saveForm) {
                        window.JobPanel.saveForm(() => {
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
                    // No workspace, just close and proceed
                    closeDialog();
                    onProceed();
                }
            });

            // Discard changes and proceed
            discardBtn.addEventListener('click', () => {
                closeDialog();
                onProceed();
            });

            // Cancel - don't switch jobs
            cancelBtn.addEventListener('click', closeDialog);

            // ESC key to cancel
            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    closeDialog();
                    document.removeEventListener('keydown', escHandler);
                }
            };
            document.addEventListener('keydown', escHandler);

            // Click overlay to cancel
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    closeDialog();
                }
            });
        }

        /**
         * Save workspace state to localStorage
         */
        saveToStorage() {
            try {
                const state = {
                    jobs: Array.from(this.openJobs.entries()),
                    activeJobId: this.activeJobId
                };
                localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
            } catch (error) {
                console.warn('JobWorkspace: Error saving to localStorage', error);
            }
        }

        /**
         * Load workspace state from localStorage
         */
        loadFromStorage() {
            try {
                const saved = localStorage.getItem(STORAGE_KEY);
                if (!saved) return;

                const state = JSON.parse(saved);

                // Restore jobs
                if (state.jobs && Array.isArray(state.jobs)) {
                    this.openJobs = new Map(state.jobs);
                }

                // Restore active job (but don't open panel yet - wait for user action)
                this.activeJobId = null; // Don't auto-open on page load

                // Mark all as minimized on page load
                this.openJobs.forEach(job => {
                    job.isMinimized = true;
                });

            } catch (error) {
                console.warn('JobWorkspace: Error loading from localStorage', error);
                this.openJobs.clear();
                this.activeJobId = null;
            }
        }

        /**
         * Clear all workspace data
         */
        clear() {
            this.openJobs.clear();
            this.activeJobId = null;
            localStorage.removeItem(STORAGE_KEY);
            this.render();
        }
    }

    // Initialize on load
    new JobWorkspace();
})();

