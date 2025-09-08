/**
 * Job Calendar - Manages job calendar display with HTMX integration
 * Handles calendar rendering, filtering, and job status updates
 */

(function () {
    'use strict';

    class JobCalendar {
        constructor() {
            this.calendar = null;
            this.calendarEl = null;
            this.calendarFilter = null;
            this.statusFilter = null;
            this.searchFilter = null;
            this.loadingEl = null;
            
            // State management
            this.currentFilters = {
                calendar: '',
                status: '',
                search: '',
                month: new Date().getMonth() + 1,
                year: new Date().getFullYear()
            };
            
            this.initialize();
        }

        /**
         * Initialize the job calendar
         */
        initialize() {
            this.initializeElements();
            this.setupCalendar();
            this.setupEventListeners();
            this.loadCalendarData();
        }

        /**
         * Initialize DOM element references
         */
        initializeElements() {
            this.calendarEl = document.getElementById('calendar');
            this.calendarFilter = document.getElementById('calendar-filter');
            this.statusFilter = document.getElementById('status-filter');
            this.searchFilter = document.getElementById('search-filter');
            this.loadingEl = document.getElementById('calendar-loading');
        }

        /**
         * Setup FullCalendar instance
         */
        setupCalendar() {
            if (!this.calendarEl || typeof FullCalendar === 'undefined') {
                console.error('JobCalendar: FullCalendar not available');
                return;
            }

            this.calendar = new FullCalendar.Calendar(this.calendarEl, {
                initialView: 'dayGridMonth',
                headerToolbar: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,timeGridWeek,timeGridDay'
                },
                height: 'auto',
                events: this.fetchEvents.bind(this),
                eventClick: this.handleEventClick.bind(this),
                eventDoubleClick: this.handleEventDoubleClick.bind(this),
                eventDidMount: this.handleEventMount.bind(this),
                datesSet: this.handleDatesSet.bind(this),
                eventTimeFormat: {
                    hour: 'numeric',
                    minute: '2-digit',
                    meridiem: 'short'
                },
                dayMaxEvents: true,
                moreLinkClick: 'popover',
                eventDisplay: 'block',
                eventColor: '#3B82F6',
                eventTextColor: '#ffffff',
                eventBorderColor: '#3B82F6',
                eventClassNames: this.getEventClassNames.bind(this),
                eventContent: this.renderEventContent.bind(this)
            });

            this.calendar.render();
        }

        /**
         * Setup event listeners for filters
         */
        setupEventListeners() {
            if (this.calendarFilter) {
                this.calendarFilter.addEventListener('change', this.handleFilterChange.bind(this));
            }
            if (this.statusFilter) {
                this.statusFilter.addEventListener('change', this.handleFilterChange.bind(this));
            }
            if (this.searchFilter) {
                this.searchFilter.addEventListener('input', this.debounce(this.handleFilterChange.bind(this), 300));
            }
        }

        /**
         * Fetch events from the server
         */
        fetchEvents(info, successCallback, failureCallback) {
            this.showLoading();
            
            const params = new URLSearchParams({
                ...this.currentFilters,
                start: info.startStr,
                end: info.endStr
            });

            fetch(`/rental_scheduler/api/job-calendar-data/?${params}`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        successCallback(data.events);
                    } else {
                        console.error('JobCalendar: Error fetching events', data.error);
                        failureCallback(data.error);
                    }
                })
                .catch(error => {
                    console.error('JobCalendar: Network error', error);
                    failureCallback(error);
                })
                .finally(() => {
                    this.hideLoading();
                });
        }

        /**
         * Handle filter changes
         */
        handleFilterChange() {
            this.currentFilters.calendar = this.calendarFilter?.value || '';
            this.currentFilters.status = this.statusFilter?.value || '';
            this.currentFilters.search = this.searchFilter?.value || '';
            
            this.refreshCalendar();
        }

        /**
         * Handle calendar date changes
         */
        handleDatesSet(info) {
            this.currentFilters.month = info.start.getMonth() + 1;
            this.currentFilters.year = info.start.getFullYear();
        }

        /**
         * Handle event click for status updates
         */
        handleEventClick(info) {
            const event = info.event;
            const jobId = event.extendedProps.job_id;
            
            if (!jobId) return;

            // Show status update modal or quick action
            this.showStatusUpdateModal(jobId, event.extendedProps.status);
        }

        /**
         * Handle event double click for editing
         */
        handleEventDoubleClick(info) {
            const event = info.event;
            const jobId = event.extendedProps.job_id;
            
            if (jobId) {
                window.location.href = `/rental_scheduler/jobs/${jobId}/edit/`;
            }
        }

        /**
         * Handle event mount for styling
         */
        handleEventMount(info) {
            const event = info.event;
            const props = event.extendedProps;
            
            // Apply completion styling
            if (props.is_completed) {
                event.setProp('textDecoration', 'line-through');
                event.setProp('opacity', '0.7');
            }
            
            // Apply canceled styling
            if (props.is_canceled) {
                event.setProp('textDecoration', 'line-through');
                event.setProp('opacity', '0.5');
            }
        }

        /**
         * Get event class names for styling
         */
        getEventClassNames(info) {
            const classes = ['job-event'];
            const props = info.event.extendedProps;
            
            if (props.is_completed) {
                classes.push('job-completed');
            }
            if (props.is_canceled) {
                classes.push('job-canceled');
            }
            
            return classes;
        }

        /**
         * Render custom event content
         */
        renderEventContent(info) {
            const event = info.event;
            const props = event.extendedProps;
            
            return {
                html: `
                    <div class="job-event-content">
                        <div class="job-title">${event.title}</div>
                        <div class="job-status">${props.status_display}</div>
                    </div>
                `
            };
        }

        /**
         * Show status update modal
         */
        showStatusUpdateModal(jobId, currentStatus) {
            const statusChoices = [
                { value: 'uncompleted', label: 'Uncompleted' },
                { value: 'completed', label: 'Completed' }
            ];

            const modal = document.createElement('div');
            modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50';
            modal.innerHTML = `
                <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                    <div class="mt-3 text-center">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">Update Job Status</h3>
                        <div class="space-y-2">
                            ${statusChoices.map(status => `
                                <button class="status-option w-full text-left px-3 py-2 rounded border ${status.value === currentStatus ? 'bg-blue-100 border-blue-300' : 'bg-white border-gray-300 hover:bg-gray-50'}" 
                                        data-status="${status.value}">
                                    ${status.label}
                                </button>
                            `).join('')}
                        </div>
                        <div class="flex justify-end space-x-3 mt-6">
                            <button class="cancel-btn px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50">
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            // Handle status selection
            modal.querySelectorAll('.status-option').forEach(btn => {
                btn.addEventListener('click', () => {
                    const newStatus = btn.dataset.status;
                    this.updateJobStatus(jobId, newStatus);
                    document.body.removeChild(modal);
                });
            });

            // Handle cancel
            modal.querySelector('.cancel-btn').addEventListener('click', () => {
                document.body.removeChild(modal);
            });

            // Close on outside click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    document.body.removeChild(modal);
                }
            });
        }

        /**
         * Update job status via HTMX
         */
        updateJobStatus(jobId, newStatus) {
            const formData = new FormData();
            formData.append('status', newStatus);

            fetch(`/rental_scheduler/api/jobs/${jobId}/update-status/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.refreshCalendar();
                    this.showToast('Job status updated successfully', 'success');
                } else {
                    this.showToast('Error updating job status', 'error');
                }
            })
            .catch(error => {
                console.error('JobCalendar: Error updating status', error);
                this.showToast('Error updating job status', 'error');
            });
        }

        /**
         * Refresh calendar data
         */
        refreshCalendar() {
            if (this.calendar) {
                this.calendar.refetchEvents();
            }
        }

        /**
         * Load initial calendar data
         */
        loadCalendarData() {
            this.refreshCalendar();
        }

        /**
         * Show loading indicator
         */
        showLoading() {
            if (this.loadingEl) {
                this.loadingEl.classList.remove('hidden');
            }
        }

        /**
         * Hide loading indicator
         */
        hideLoading() {
            if (this.loadingEl) {
                this.loadingEl.classList.add('hidden');
            }
        }

        /**
         * Show toast notification
         */
        showToast(message, type = 'info') {
            // Create toast element
            const toast = document.createElement('div');
            toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white ${
                type === 'success' ? 'bg-green-600' : 
                type === 'error' ? 'bg-red-600' : 'bg-blue-600'
            }`;
            toast.textContent = message;

            document.body.appendChild(toast);

            // Remove after 3 seconds
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 3000);
        }

        /**
         * Get CSRF token from cookies
         */
        getCSRFToken() {
            const name = 'csrftoken';
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        /**
         * Debounce function for search input
         */
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new JobCalendar();
        });
    } else {
        new JobCalendar();
    }

})();


