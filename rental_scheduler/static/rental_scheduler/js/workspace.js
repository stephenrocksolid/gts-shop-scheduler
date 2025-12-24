/**
 * Job Workspace - Manages open jobs in a bottom tab bar
 * Allows users to open multiple jobs from calendar, minimize them, and switch between them
 * VERSION: 1.1 - Draft HTML moved to sessionStorage for security
 */

(function () {
    'use strict';

    const STORAGE_KEY = 'gts-job-workspace';
    const DRAFT_HTML_PREFIX = 'gts-job-workspace:html:'; // sessionStorage prefix for draft HTML
    const MAX_TABS = 10; // Limit number of open jobs

    // ========================================================================
    // SESSION STORAGE HELPERS FOR DRAFT HTML
    // Draft HTML is stored in sessionStorage (tab-scoped, clears on browser close)
    // to prevent sensitive data from persisting across browser restarts.
    // ========================================================================

    /**
     * Get draft HTML from sessionStorage
     * @param {string} jobId - The job/draft ID
     * @returns {string|null} - The HTML content or null
     */
    function getDraftHtml(jobId) {
        if (!jobId) return null;
        try {
            return sessionStorage.getItem(DRAFT_HTML_PREFIX + jobId);
        } catch (e) {
            console.warn('JobWorkspace: Error reading draft HTML from sessionStorage', e);
            return null;
        }
    }

    /**
     * Set draft HTML in sessionStorage
     * @param {string} jobId - The job/draft ID
     * @param {string} html - The HTML content (capped at 100KB)
     * @returns {boolean} - True if stored successfully
     */
    function setDraftHtml(jobId, html) {
        if (!jobId) return false;
        try {
            // Cap at 100KB to prevent storage overflow
            if (html && html.length > 100000) {
                console.warn('JobWorkspace: Draft HTML too large, not storing');
                return false;
            }
            if (html) {
                sessionStorage.setItem(DRAFT_HTML_PREFIX + jobId, html);
            } else {
                sessionStorage.removeItem(DRAFT_HTML_PREFIX + jobId);
            }
            return true;
        } catch (e) {
            console.warn('JobWorkspace: Error writing draft HTML to sessionStorage', e);
            return false;
        }
    }

    /**
     * Remove draft HTML from sessionStorage
     * @param {string} jobId - The job/draft ID
     */
    function removeDraftHtml(jobId) {
        if (!jobId) return;
        try {
            sessionStorage.removeItem(DRAFT_HTML_PREFIX + jobId);
        } catch (e) {
            // Ignore errors
        }
    }

    /**
     * Clear all draft HTML from sessionStorage (for workspace.clear())
     */
    function clearAllDraftHtml() {
        try {
            const keysToRemove = [];
            for (let i = 0; i < sessionStorage.length; i++) {
                const key = sessionStorage.key(i);
                if (key && key.startsWith(DRAFT_HTML_PREFIX)) {
                    keysToRemove.push(key);
                }
            }
            keysToRemove.forEach(k => sessionStorage.removeItem(k));
        } catch (e) {
            // Ignore errors
        }
    }

    /**
     * Normalize job ID to string for consistent Map key usage
     * This prevents issues where numeric IDs (123) and string IDs ("123") are treated differently
     */
    function normalizeJobId(jobId) {
        return jobId != null ? String(jobId) : null;
    }

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
            jobId = normalizeJobId(jobId);
            if (!jobId) return;

            // Check if already open
            if (this.openJobs.has(jobId)) {
                // Just make it active and show panel
                this.switchToJob(jobId);
                return;
            }

            // Check max tabs limit
            if (this.openJobs.size >= MAX_TABS) {
                GTS.toast.warning(`Maximum ${MAX_TABS} jobs can be open at once`);
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

            this.activeJobId = jobId; // Already normalized above

            // Save and render
            this.saveToStorage();
            this.render();

            // Load job edit form in panel
            if (window.JobPanel) {
                window.JobPanel.setTitle('Edit Job');
                window.JobPanel.load(GTS.urls.jobCreatePartial({ edit: jobId }));
                window.JobPanel.setCurrentJobId(jobId); // Pass normalized ID

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
            jobId = normalizeJobId(jobId);
            if (!jobId) return;

            // Check if already open
            if (this.openJobs.has(jobId)) {
                return; // Already exists, don't modify
            }

            // Check max tabs limit
            if (this.openJobs.size >= MAX_TABS) {
                GTS.toast.warning(`Maximum ${MAX_TABS} jobs can be open at once`);
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
         * Update metadata for an existing job in the workspace
         * @param {string} jobId - The job ID
         * @param {Object} meta - Metadata to update
         * @param {string} [meta.customerName] - Customer name for display
         * @param {string} [meta.trailerColor] - Trailer color
         * @param {string} [meta.calendarColor] - Calendar color
         */
        updateJobMeta(jobId, meta) {
            jobId = normalizeJobId(jobId);
            if (!jobId) return;

            const job = this.openJobs.get(jobId);
            if (!job) return;

            // Update fields if provided (use nullish coalescing to preserve existing values)
            if (meta.customerName !== undefined) {
                job.customerName = meta.customerName || job.customerName;
            }
            if (meta.trailerColor !== undefined) {
                job.trailerColor = meta.trailerColor;
            }
            if (meta.calendarColor !== undefined) {
                job.calendarColor = meta.calendarColor;
            }

            this.saveToStorage();
            this.render();
        }

        /**
         * Minimize a job (keep in workspace but hide panel)
         */
        minimizeJob(jobId) {
            jobId = normalizeJobId(jobId);
            if (!jobId) return;

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
            jobId = normalizeJobId(jobId);
            if (!jobId) return;

            if (!this.openJobs.has(jobId)) return;

            this.openJobs.delete(jobId);

            // Clean up draft HTML from sessionStorage
            removeDraftHtml(jobId);

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
            jobId = normalizeJobId(jobId);
            if (!jobId) return;

            const job = this.openJobs.get(jobId);
            if (!job) return;

            // Check if there are unsaved changes
            if (window.JobPanel && window.JobPanel.hasUnsavedChanges && window.JobPanel.hasUnsavedChanges()) {
                // Save the form first
                window.JobPanel.saveForm(() => {
                    // After saving, add to workspace or update meta if it has a job ID
                    const currentJobId = normalizeJobId(window.JobPanel.currentJobId);
                    if (currentJobId) {
                        // Get job details from the form
                        const form = document.querySelector('#job-panel .panel-body form');
                        const businessName = form?.querySelector('input[name="business_name"]')?.value ||
                            form?.querySelector('input[name="contact_name"]')?.value ||
                            'Unnamed Job';
                        const trailerColor = form?.querySelector('input[name="trailer_color"]')?.value || '';
                        const meta = {
                            customerName: businessName,
                            trailerColor: trailerColor,
                            calendarColor: '#3B82F6'
                        };

                        if (!this.hasJob(currentJobId)) {
                            // Add to workspace as minimized
                            this.addJobMinimized(currentJobId, meta);
                        } else {
                            // Update meta for existing job (e.g. if name changed)
                            this.updateJobMeta(currentJobId, meta);
                        }
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
            jobId = normalizeJobId(jobId);
            if (!jobId) return;

            const job = this.openJobs.get(jobId);
            if (!job) return;

            job.isMinimized = false;
            this.activeJobId = jobId;

            if (window.JobPanel) {
                // Check for draft HTML in sessionStorage (for drafts or failed saves)
                const unsavedHtml = getDraftHtml(jobId);

                if (unsavedHtml) {
                    // Restore from cached HTML instead of loading from server
                    const title = job.isDraft ? 'New Job (Unsaved)' : 'Edit Job (Unsaved)';
                    window.JobPanel.setTitle(title);
                    window.JobPanel.showContent(unsavedHtml);

                    // Set the job ID context (for drafts, store the draft ID so we can promote later)
                    if (job.isDraft) {
                        window.JobPanel.currentDraftId = jobId;
                        window.JobPanel.setCurrentJobId(null); // No real job ID yet
                    } else {
                        window.JobPanel.currentDraftId = null;
                        window.JobPanel.setCurrentJobId(jobId);
                    }

                    // Update minimize button after a short delay
                    setTimeout(() => {
                        if (window.JobPanel.updateMinimizeButton) {
                            window.JobPanel.updateMinimizeButton();
                        }
                    }, 100);

                } else if (job.isDraft) {
                    // Draft without HTML - can't restore, must drop the draft
                    console.warn('JobWorkspace: Draft without HTML, cannot restore. Removing draft.');
                    GTS.toast.warning('Draft expired. Starting a new job.');
                    this.openJobs.delete(jobId);

                    // Load fresh new job form
                    window.JobPanel.setTitle('New Job');
                    window.JobPanel.load(GTS.urls.jobCreatePartial());
                    window.JobPanel.currentDraftId = null;
                    window.JobPanel.setCurrentJobId(null);

                    setTimeout(() => {
                        if (window.JobPanel.updateMinimizeButton) {
                            window.JobPanel.updateMinimizeButton();
                        }
                    }, 100);

                } else {
                    // Normal case: load job from server
                    window.JobPanel.setTitle('Edit Job');
                    window.JobPanel.load(GTS.urls.jobCreatePartial({ edit: jobId }));
                    window.JobPanel.setCurrentJobId(jobId);
                    window.JobPanel.currentDraftId = null;

                    // Update minimize button after a short delay to ensure panel is ready
                    setTimeout(() => {
                        if (window.JobPanel.updateMinimizeButton) {
                            window.JobPanel.updateMinimizeButton();
                        }
                    }, 100);
                }
            }

            this.saveToStorage();
            this.render();
        }

        /**
         * Check if a job is in the workspace
         */
        hasJob(jobId) {
            jobId = normalizeJobId(jobId);
            if (!jobId) return false;
            return this.openJobs.has(jobId);
        }

        /**
         * Get the currently active job ID
         */
        getActiveJobId() {
            return this.activeJobId;
        }

        /**
         * Mark a job as having unsaved changes
         * @param {string} jobId - The job ID
         * @param {string} html - The HTML content to restore (optional, stored in sessionStorage)
         */
        markUnsaved(jobId, html) {
            jobId = normalizeJobId(jobId);
            if (!jobId) return;

            const job = this.openJobs.get(jobId);
            if (!job) return;

            job.unsaved = true;
            // Store sanitized HTML in sessionStorage (tab-scoped, security improvement)
            if (html) {
                const sanitizedHtml = GTS.htmlState.sanitizeDraftHtml(html);
                setDraftHtml(jobId, sanitizedHtml);
            }

            this.saveToStorage();
            this.render();
        }

        /**
         * Clear unsaved state for a job
         * @param {string} jobId - The job ID
         */
        clearUnsaved(jobId) {
            jobId = normalizeJobId(jobId);
            if (!jobId) return;

            const job = this.openJobs.get(jobId);
            if (!job) return;

            job.unsaved = false;
            // Remove draft HTML from sessionStorage
            removeDraftHtml(jobId);

            this.saveToStorage();
            this.render();
        }

        /**
         * Check if a job has unsaved changes
         * @param {string} jobId - The job ID
         * @returns {boolean}
         */
        isUnsaved(jobId) {
            jobId = normalizeJobId(jobId);
            if (!jobId) return false;

            const job = this.openJobs.get(jobId);
            return job ? !!job.unsaved : false;
        }

        /**
         * Get the unsaved HTML for a job (if any)
         * @param {string} jobId - The job ID
         * @returns {string|null}
         */
        getUnsavedHtml(jobId) {
            jobId = normalizeJobId(jobId);
            if (!jobId) return null;

            // Get from sessionStorage (primary) for security
            return getDraftHtml(jobId);
        }

        /**
         * Create a draft workspace entry for a new unsaved job
         * Draft entries have temporary IDs and are marked as isDraft
         * @param {Object} data - Draft job data
         * @param {string} data.customerName - Customer name for display
         * @param {string} data.trailerColor - Trailer color
         * @param {string} data.calendarColor - Calendar color
         * @param {string} data.html - Panel HTML content to restore (stored in sessionStorage)
         * @returns {string} The draft ID
         */
        createDraft(data) {
            // Check max tabs limit
            if (this.openJobs.size >= MAX_TABS) {
                GTS.toast.warning(`Maximum ${MAX_TABS} jobs can be open at once`);
                return null;
            }

            // Generate a unique draft ID
            const draftId = `draft-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

            // Store HTML in sessionStorage (not localStorage) for security
            if (data.html) {
                const sanitizedHtml = GTS.htmlState.sanitizeDraftHtml(data.html);
                setDraftHtml(draftId, sanitizedHtml);
            }

            // Add to workspace as a draft (HTML stored separately in sessionStorage)
            this.openJobs.set(draftId, {
                jobId: draftId,
                customerName: data.customerName || 'New Job',
                trailerColor: data.trailerColor || '',
                calendarColor: data.calendarColor || '#3B82F6',
                isMinimized: true,
                timestamp: Date.now(),
                isDraft: true,
                unsaved: true
                // Note: unsavedHtml no longer stored here, moved to sessionStorage
            });

            this.saveToStorage();
            this.render();

            return draftId;
        }

        /**
         * Promote a draft to a real job after successful save
         * @param {string} draftId - The draft ID to promote
         * @param {string} realJobId - The real job ID from the server
         * @param {Object} updatedMeta - Optional updated metadata
         */
        promoteDraft(draftId, realJobId, updatedMeta = {}) {
            draftId = normalizeJobId(draftId);
            realJobId = normalizeJobId(realJobId);

            if (!draftId || !realJobId) return;

            const draft = this.openJobs.get(draftId);
            if (!draft) return;

            // Remove the draft entry
            this.openJobs.delete(draftId);

            // Clean up draft HTML from sessionStorage
            removeDraftHtml(draftId);

            // Create the real job entry
            const realJob = {
                ...draft,
                jobId: realJobId,
                isDraft: false,
                unsaved: false,
                ...updatedMeta
            };

            this.openJobs.set(realJobId, realJob);

            // Update active job ID if the draft was active
            if (this.activeJobId === draftId) {
                this.activeJobId = realJobId;
            }

            this.saveToStorage();
            this.render();

            console.log(`JobWorkspace: Promoted draft ${draftId} to job ${realJobId}`);
        }

        /**
         * Check if an ID is a draft
         * @param {string} id - The ID to check
         * @returns {boolean}
         */
        isDraftId(id) {
            return id && String(id).startsWith('draft-');
        }

        /**
         * Close all jobs
         */
        closeAll() {
            if (this.openJobs.size === 0) return;

            if (confirm('Close all open jobs?')) {
                // Clean up all draft HTML from sessionStorage
                clearAllDraftHtml();

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
            if (job.unsaved) {
                tab.classList.add('unsaved');
            }
            if (job.isDraft) {
                tab.classList.add('draft');
            }

            // Color indicator (small circle)
            const colorIndicator = document.createElement('div');
            colorIndicator.className = 'workspace-tab-color';
            colorIndicator.style.backgroundColor = job.calendarColor;
            tab.appendChild(colorIndicator);

            // Unsaved indicator (red dot)
            if (job.unsaved || job.isDraft) {
                const unsavedDot = document.createElement('div');
                unsavedDot.className = 'workspace-tab-unsaved-dot';
                unsavedDot.title = job.isDraft ? 'New job (not saved)' : 'Unsaved changes';
                tab.appendChild(unsavedDot);
            }

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
         * For drafts, builds tooltip from local workspace data instead of fetching from API
         */
        async showWorkspaceTabTooltip(jobId, tabElement) {
            try {
                // Check if this is a draft - drafts are client-side only and have no server record
                if (this.isDraftId(jobId)) {
                    const draft = this.openJobs.get(jobId);
                    if (!draft) return;

                    // Build tooltip from local draft data
                    let businessName = draft.customerName || 'New Job';
                    let startDt = null;
                    let endDt = null;

                    // Try to parse additional fields from unsavedHtml in sessionStorage
                    const unsavedHtml = getDraftHtml(jobId);
                    if (unsavedHtml) {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(unsavedHtml, 'text/html');

                        const businessInput = doc.querySelector('input[name="business_name"]');
                        if (businessInput && businessInput.value) {
                            businessName = businessInput.value;
                        }

                        const startInput = doc.querySelector('input[name="start_dt"]');
                        if (startInput && startInput.value) {
                            startDt = new Date(startInput.value);
                        }

                        const endInput = doc.querySelector('input[name="end_dt"]');
                        if (endInput && endInput.value) {
                            endDt = new Date(endInput.value);
                        }
                    }

                    const fakeEvent = {
                        title: businessName,
                        start: startDt,
                        end: endDt,
                        allDay: false,
                        extendedProps: {
                            calendar_name: '',
                            business_name: businessName,
                            contact_name: '',
                            phone: '',
                            trailer_details: '',
                            trailer_color: draft.trailerColor || '',
                            trailer_serial: '',
                            repair_notes: '',
                            notes: '',
                            status: 'Draft (unsaved)',
                            is_recurring_parent: false,
                            is_multi_day: false
                        }
                    };

                    if (window.jobCalendar) {
                        window.jobCalendar.showEventTooltip(fakeEvent, tabElement);
                    }
                    return;
                }

                // For real jobs, fetch from API
                const response = await fetch(GTS.urls.jobDetailApi(jobId));
                if (!response.ok) {
                    console.error(`Failed to fetch job details for job ${jobId}`);
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
                const currentJobId = normalizeJobId(window.JobPanel.currentJobId);
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
         * Note: Draft HTML is stored in sessionStorage, not here (for security)
         */
        saveToStorage() {
            // Create a copy of jobs without unsavedHtml (it's in sessionStorage now)
            const jobsToSave = Array.from(this.openJobs.entries()).map(([key, job]) => {
                const jobCopy = { ...job };
                // Remove unsavedHtml from localStorage payload - it's in sessionStorage
                delete jobCopy.unsavedHtml;
                return [key, jobCopy];
            });

            const state = {
                schemaVersion: 2, // Version 2: unsavedHtml moved to sessionStorage
                jobs: jobsToSave,
                activeJobId: this.activeJobId
            };

            // Use GTS.storage if available
            if (window.GTS && window.GTS.storage) {
                const ok = GTS.storage.setJson(STORAGE_KEY, state);
                if (!ok) {
                    console.error('JobWorkspace: Error saving to localStorage');
                }
            } else {
                try {
                    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
                } catch (error) {
                    console.error('JobWorkspace: Error saving to localStorage', error);
                }
            }
        }

        /**
         * Load workspace state from localStorage
         * Handles migration from v1 (unsavedHtml in localStorage) to v2 (sessionStorage)
         */
        loadFromStorage() {
            let state = null;

            // Use GTS.storage if available
            if (window.GTS && window.GTS.storage) {
                state = GTS.storage.getJson(STORAGE_KEY, null);
            } else {
                try {
                    const saved = localStorage.getItem(STORAGE_KEY);
                    if (saved) {
                        state = JSON.parse(saved);
                    }
                } catch (error) {
                    console.warn('JobWorkspace: Error loading from localStorage', error);
                }
            }

            if (!state) return;

            const needsMigration = !state.schemaVersion || state.schemaVersion < 2;

            // Restore jobs with normalized IDs
            if (state.jobs && Array.isArray(state.jobs)) {
                this.openJobs = new Map();
                state.jobs.forEach(([key, value]) => {
                    const normalizedKey = normalizeJobId(key);
                    if (normalizedKey) {
                        value.jobId = normalizedKey; // Also normalize the stored jobId
                        // Ensure backwards compatibility for new fields
                        value.unsaved = value.unsaved || false;
                        value.isDraft = value.isDraft || false;

                        // MIGRATION: Move unsavedHtml from localStorage to sessionStorage
                        if (needsMigration && value.unsavedHtml) {
                            console.log('JobWorkspace: Migrating draft HTML to sessionStorage for', normalizedKey);
                            setDraftHtml(normalizedKey, value.unsavedHtml);
                        }
                        // Remove unsavedHtml from in-memory state (it's in sessionStorage now)
                        delete value.unsavedHtml;

                        this.openJobs.set(normalizedKey, value);
                    }
                });
            }

            // Restore active job (but don't open panel yet - wait for user action)
            this.activeJobId = null; // Don't auto-open on page load

            // Mark all as minimized on page load
            this.openJobs.forEach(job => {
                job.isMinimized = true;
            });

            // If we migrated, save the updated state immediately to update schema version
            if (needsMigration && this.openJobs.size > 0) {
                console.log('JobWorkspace: Migration complete, saving updated state');
                this.saveToStorage();
            }
        }

        /**
         * Clear all workspace data
         */
        clear() {
            // Clear all draft HTML from sessionStorage
            clearAllDraftHtml();

            this.openJobs.clear();
            this.activeJobId = null;
            if (window.GTS && window.GTS.storage) {
                GTS.storage.remove(STORAGE_KEY);
            } else {
                localStorage.removeItem(STORAGE_KEY);
            }
            this.render();
        }
    }

    // Initialize on load
    new JobWorkspace();
})();

