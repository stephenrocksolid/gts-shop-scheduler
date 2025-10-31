/**
 * Job Workspace - Manages open jobs in a bottom tab bar
 * Allows users to open multiple jobs from calendar, minimize them, and switch between them
 * VERSION: 1.0 - Initial implementation
 */

(function() {
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
            
            // Track current job in panel
            if (window.JobPanel && window.JobPanel.setCurrentJobId) {
                window.JobPanel.setCurrentJobId(jobId);
            }
            
            // Update minimize button visibility
            if (window.JobPanel && window.JobPanel.updateMinimizeButton) {
                window.JobPanel.updateMinimizeButton();
            }
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

