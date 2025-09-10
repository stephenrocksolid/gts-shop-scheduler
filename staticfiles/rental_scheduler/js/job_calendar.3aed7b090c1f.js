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
                    right: 'newJobButton dayGridMonth,timeGridWeek,timeGridDay'
                },
                headerToolbarHeight: 'auto',
                buttonText: {
                    today: 'Today',
                    month: 'Month',
                    week: 'Week',
                    day: 'Day',
                    dayGridMonth: 'Month',
                    timeGridWeek: 'Week',
                    timeGridDay: 'Day'
                },
                customButtons: {
                    newJobButton: {
                        text: '+ Job',
                        click: function() {
                            // Use the URL from window.calendarConfig if available
                            const createUrl = window.calendarConfig?.jobCreateUrl || '/jobs/create/';
                            window.location.href = createUrl;
                        }
                    }
                },
                height: '100%',        // fill #calendar-wrap
                expandRows: true,      // make weeks expand to fill vertical space
                windowResizeDelay: 50, // better resizing behavior
                events: this.fetchEvents.bind(this),
                dateClick: this.handleDateClick.bind(this),
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
            
            // Style the custom New Job button after render
            this.styleNewJobButton();
        }

        /**
         * Style the New Job button for better appearance
         */
        styleNewJobButton() {
            // Wait a bit for the DOM to be ready
            setTimeout(() => {
                const newJobBtn = document.querySelector('.fc-newJobButton-button');
                if (newJobBtn) {
                    // Style the button for better spacing and appearance
                    newJobBtn.style.fontWeight = 'bold';
                    newJobBtn.style.whiteSpace = 'nowrap';
                    newJobBtn.style.minWidth = 'auto';
                }
            }, 100);
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

            fetch(`/api/job-calendar-data/?${params}`)
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
            try {
                console.log('JobCalendar: Single click detected', {
                    eventId: info.event.id,
                    title: info.event.title,
                    type: info.event.extendedProps.type,
                    extendedProps: info.event.extendedProps
                });
                this.openEventDetailsDialog(info);
            } catch (error) {
                console.error('JobCalendar: Error handling single click', error);
                this.showError('Unable to open event details. Please try again.');
            }
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
         * Handle date click to create new job
         */
        handleDateClick(info) {
            try {
                console.log('JobCalendar: Date clicked', info);
                
                // Create a mock event object with the clicked date/time
                const clickedDate = info.date;
                const mockEvent = {
                    id: 'new-job',
                    start: clickedDate,
                    end: new Date(clickedDate.getTime() + (2 * 60 * 60 * 1000)), // Default 2 hours duration
                    allDay: false,
                    title: 'New Job'
                };
                
                // Create mock props for new job
                const mockProps = {
                    job_id: null,
                    business_name: '',
                    contact_name: '',
                    phone: '',
                    trailer_color: '',
                    trailer_serial: '',
                    trailer_details: '',
                    status: 'uncompleted',
                    notes: '',
                    repair_notes: '',
                    all_day: false
                };
                
                // Open the new job dialog
                this.openNewJobDialog(mockEvent, mockProps);
                
            } catch (error) {
                console.error('JobCalendar: Error handling date click', error);
                this.showError('Unable to create new job. Please try again.');
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
            
            // Format status display
            const statusDisplay = props.status ? props.status.charAt(0).toUpperCase() + props.status.slice(1) : 'Unknown';
            
            return {
                html: `
                    <div class="job-event-content">
                        <div class="job-title">${event.title}</div>
                        <div class="job-status">${statusDisplay}</div>
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
         * Update job status via API
         */
        updateJobStatus(jobId, newStatus) {
            const csrfToken = this.getCSRFToken();
            console.log('JobCalendar: Updating status with CSRF Token:', csrfToken);

            fetch(`/rental_scheduler/api/jobs/${jobId}/update-status/`, {
                method: 'POST',
                credentials: 'same-origin',  // Send cookies so CsrfViewMiddleware can see csrftoken
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,   // exact header name + cookie name
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ status: newStatus })
            })
            .then(response => {
                if (!response.ok) {
                    // Read and log the response body for debugging
                    return response.text().then(text => {
                        console.error('JobCalendar: Status update failed', response.status, text);
                        throw new Error(`HTTP ${response.status}: ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
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

        /**
         * Open comprehensive event details dialog
         * @param {Object} info - FullCalendar event info
         */
        openEventDetailsDialog(info) {
            try {
                console.log('JobCalendar: Opening event details dialog', info);
                
                // Get the latest event data from the calendar to ensure we have fresh info
                const latestEvent = this.calendar?.getEventById(info.event.id);
                const eventProps = latestEvent ? latestEvent.extendedProps : info.event.extendedProps;
                const event = latestEvent || info.event;
                
                console.log('JobCalendar: Event data', { event, eventProps });

                // Create dialog backdrop
                const backdrop = document.createElement('div');
                backdrop.className = 'event-details-backdrop';
                backdrop.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.5);
                    z-index: 1000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                `;

                // Create dialog container
                const dialog = document.createElement('div');
                dialog.className = 'card card-elevated';
                dialog.style.cssText = `
                    max-width: 800px;
                    width: 100%;
                    max-height: 90vh;
                    overflow: hidden;
                    position: relative;
                    background-color: #ffffff;
                    border-radius: 16px;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                    margin: 20px;
                `;
                
                // Add responsive styles
                const style = document.createElement('style');
                style.textContent = `
                    @media (max-width: 768px) {
                        .event-details-dialog {
                            margin: 10px !important;
                            max-width: calc(100vw - 20px) !important;
                            max-height: calc(100vh - 20px) !important;
                        }
                        .event-details-dialog .grid-responsive {
                            grid-template-columns: 1fr !important;
                        }
                    }
                `;
                document.head.appendChild(style);

                // Build dialog content for job events
                const content = this.buildJobEventContent(event, eventProps);
                dialog.innerHTML = content;

                // Add to DOM
                backdrop.appendChild(dialog);
                document.body.appendChild(backdrop);

                // Setup event listeners
                this.setupEventDetailsDialogListeners(backdrop, dialog, event, eventProps);

                // Store reference for cleanup
                this.eventDetailsDialog = backdrop;

            } catch (error) {
                console.error('JobCalendar: Error opening event details dialog', error);
                this.showError('Unable to open event details. Please try again.');
            }
        }

        /**
         * Open new job creation dialog
         * @param {Object} event - Mock event object with clicked date/time
         * @param {Object} props - Mock props for new job
         */
        openNewJobDialog(event, props) {
            try {
                console.log('JobCalendar: Opening new job dialog', { event, props });

                // Create dialog backdrop
                const backdrop = document.createElement('div');
                backdrop.className = 'event-details-backdrop';
                backdrop.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.5);
                    z-index: 1000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                `;

                // Create dialog container
                const dialog = document.createElement('div');
                dialog.className = 'card card-elevated';
                dialog.style.cssText = `
                    max-width: 800px;
                    width: 100%;
                    max-height: 90vh;
                    overflow: hidden;
                    position: relative;
                    background-color: #ffffff;
                    border-radius: 16px;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                    margin: 20px;
                `;
                
                // Add responsive styles
                const style = document.createElement('style');
                style.textContent = `
                    @media (max-width: 768px) {
                        .event-details-dialog {
                            margin: 10px !important;
                            max-width: calc(100vw - 20px) !important;
                            max-height: calc(100vh - 20px) !important;
                        }
                        .event-details-dialog .grid-responsive {
                            grid-template-columns: 1fr !important;
                        }
                    }
                `;
                document.head.appendChild(style);

                // Build new job form content
                const content = this.buildNewJobFormContent(event, props);
                dialog.innerHTML = content;

                // Add to DOM
                backdrop.appendChild(dialog);
                document.body.appendChild(backdrop);

                // Setup event listeners
                this.setupNewJobDialogListeners(backdrop, dialog, event, props);

                // Store reference for cleanup
                this.eventDetailsDialog = backdrop;

            } catch (error) {
                console.error('JobCalendar: Error opening new job dialog', error);
                this.showError('Unable to open new job form. Please try again.');
            }
        }

        /**
         * Build content for job events
         * @param {Object} event - FullCalendar event
         * @param {Object} props - Event extended properties
         * @returns {string} HTML content
         */
        buildJobEventContent(event, props) {
            const formatDateTime = (isoString) => {
                if (!isoString) return 'Not set';
                try {
                    const date = new Date(isoString);
                    return date.toLocaleString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                        hour12: true
                    });
                } catch (error) {
                    return 'Invalid date';
                }
            };

            const getJobStatusBadge = (status) => {
                const statusDisplay = status ? status.charAt(0).toUpperCase() + status.slice(1) : 'Unknown';
                let backgroundColor, textColor;
                
                switch (status ? status.toLowerCase() : '') {
                    case 'completed':
                        backgroundColor = '#10b981';
                        textColor = '#ffffff';
                        break;
                    case 'in_progress':
                        backgroundColor = '#f59e0b';
                        textColor = '#ffffff';
                        break;
                    case 'pending':
                        backgroundColor = '#6b7280';
                        textColor = '#ffffff';
                        break;
                    case 'cancelled':
                        backgroundColor = '#ef4444';
                        textColor = '#ffffff';
                        break;
                    default:
                        backgroundColor = '#f59e0b';
                        textColor = '#ffffff';
                }
                
                return `<span style="
                    background-color: ${backgroundColor};
                    color: ${textColor};
                    padding: 6px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">${statusDisplay}</span>`;
            };

            // Format phone number for tel: link
            const formatPhoneForLink = (phone) => {
                if (!phone || phone === 'N/A') return null;
                return phone.replace(/[^\d]/g, '');
            };
            
            const phoneLink = formatPhoneForLink(props.phone);
            
            return `
                <!-- Header with title and status -->
                <div style="padding: 32px 32px 24px 32px; border-bottom: 1px solid #e5e7eb;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <h2 style="font-size: 24px; font-weight: 700; color: #111827; margin: 0;">Job Details</h2>
                        ${getJobStatusBadge(props.status)}
                    </div>
                </div>
                
                <!-- Scrollable content area -->
                <div style="max-height: calc(90vh - 200px); overflow-y: auto; padding: 32px;">
                    <div style="display: flex; flex-direction: column; gap: 32px;">
                        
                        <!-- Customer Information -->
                        <div style="background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden;">
                            <div style="background: #e2e8f0; padding: 16px 24px; border-bottom: 1px solid #cbd5e1;">
                                <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0; display: flex; align-items: center;">
                                    <svg style="width: 18px; height: 18px; margin-right: 8px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                                    </svg>
                                    Customer Information
                                </h3>
                            </div>
                            <div style="padding: 24px;">
                                <div class="grid-responsive" style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">Business Name</div>
                                        <div style="color: #6b7280; font-size: 14px;">${props.business_name || 'N/A'}</div>
                                    </div>
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">Contact Name</div>
                                        <div style="color: #6b7280; font-size: 14px;">${props.contact_name || 'N/A'}</div>
                                    </div>
                                    <div style="grid-column: 1 / -1;">
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px; display: flex; align-items: center;">
                                            <svg style="width: 16px; height: 16px; margin-right: 6px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                                <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"></path>
                                            </svg>
                                            Phone
                                        </div>
                                        <div style="color: #6b7280; font-size: 14px;">
                                            ${phoneLink ? `<a href="tel:${phoneLink}" style="color: #3b82f6; text-decoration: none;">${props.phone}</a>` : (props.phone || 'N/A')}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Trailer Information -->
                        <div style="background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden;">
                            <div style="background: #e2e8f0; padding: 16px 24px; border-bottom: 1px solid #cbd5e1;">
                                <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0; display: flex; align-items: center;">
                                    <svg style="width: 18px; height: 18px; margin-right: 8px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"></path>
                                        <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1V8a1 1 0 00-1-1h-3z"></path>
                                    </svg>
                                    Trailer Information
                                </h3>
                            </div>
                            <div style="padding: 24px;">
                                <div class="grid-responsive" style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">Color</div>
                                        <div style="color: #6b7280; font-size: 14px;">${props.trailer_color || 'N/A'}</div>
                                    </div>
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">Serial</div>
                                        <div style="color: #6b7280; font-size: 14px;">${props.trailer_serial || 'N/A'}</div>
                                    </div>
                                    <div style="grid-column: 1 / -1;">
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">Details</div>
                                        <div style="color: #6b7280; font-size: 14px;">${props.trailer_details || 'N/A'}</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Schedule Information -->
                        <div style="background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden;">
                            <div style="background: #e2e8f0; padding: 16px 24px; border-bottom: 1px solid #cbd5e1;">
                                <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0; display: flex; align-items: center;">
                                    <svg style="width: 18px; height: 18px; margin-right: 8px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"></path>
                                    </svg>
                                    Schedule Information
                                </h3>
                            </div>
                            <div style="padding: 24px;">
                                <div class="grid-responsive" style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">Start Date & Time</div>
                                        <div style="color: #6b7280; font-size: 14px;">${formatDateTime(event.start)}</div>
                                    </div>
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">End Date & Time</div>
                                        <div style="color: #6b7280; font-size: 14px;">${event.end ? formatDateTime(event.end) : 'Not set'}</div>
                                    </div>
                                    <div style="grid-column: 1 / -1;">
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">All Day Event</div>
                                        <div style="color: #6b7280; font-size: 14px;">${event.allDay ? 'Yes' : 'No'}</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        ${props.notes ? `
                        <!-- Notes -->
                        <div style="background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden;">
                            <div style="background: #e2e8f0; padding: 16px 24px; border-bottom: 1px solid #cbd5e1;">
                                <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0; display: flex; align-items: center;">
                                    <svg style="width: 18px; height: 18px; margin-right: 8px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"></path>
                                    </svg>
                                    Notes
                                </h3>
                            </div>
                            <div style="padding: 24px;">
                                <p style="color: #6b7280; font-size: 14px; line-height: 1.5; margin: 0;">${props.notes}</p>
                            </div>
                        </div>
                        ` : ''}

                        ${props.repair_notes ? `
                        <!-- Repair Notes -->
                        <div style="background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden;">
                            <div style="background: #e2e8f0; padding: 16px 24px; border-bottom: 1px solid #cbd5e1;">
                                <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0; display: flex; align-items: center;">
                                    <svg style="width: 18px; height: 18px; margin-right: 8px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"></path>
                                    </svg>
                                    Repair Notes
                                </h3>
                            </div>
                            <div style="padding: 24px;">
                                <p style="color: #6b7280; font-size: 14px; line-height: 1.5; margin: 0;">${props.repair_notes}</p>
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Footer with buttons -->
                <div style="padding: 24px 32px; border-top: 1px solid #e5e7eb; background: #ffffff;">
                    <div style="display: flex; justify-content: flex-end; gap: 12px;">
                        <button class="cancel-btn" style="
                            padding: 12px 24px;
                            border: 1px solid #d1d5db;
                            border-radius: 8px;
                            background: #ffffff;
                            color: #374151;
                            font-weight: 500;
                            font-size: 14px;
                            cursor: pointer;
                            transition: all 0.2s;
                        " onmouseover="this.style.backgroundColor='#f9fafb'" onmouseout="this.style.backgroundColor='#ffffff'">
                            Close
                        </button>
                        ${props.status === 'uncompleted' ? 
                            `<button class="mark-complete-btn" style="
                                padding: 12px 24px;
                                border: none;
                                border-radius: 8px;
                                background: #10b981;
                                color: #ffffff;
                                font-weight: 500;
                                font-size: 14px;
                                cursor: pointer;
                                transition: all 0.2s;
                            " onmouseover="this.style.backgroundColor='#059669'" onmouseout="this.style.backgroundColor='#10b981'">
                                Mark as Complete
                            </button>` : 
                            ''
                        }
                        <button class="edit-btn" style="
                            padding: 12px 24px;
                            border: none;
                            border-radius: 8px;
                            background: #3b82f6;
                            color: #ffffff;
                            font-weight: 500;
                            font-size: 14px;
                            cursor: pointer;
                            transition: all 0.2s;
                        " onmouseover="this.style.backgroundColor='#2563eb'" onmouseout="this.style.backgroundColor='#3b82f6'">
                            Edit Job
                        </button>
                    </div>
                </div>
            `;
        }

        /**
         * Setup event listeners for the event details dialog
         * @param {HTMLElement} backdrop - Dialog backdrop element
         * @param {HTMLElement} dialog - Dialog element
         * @param {Object} event - FullCalendar event
         * @param {Object} props - Event extended properties
         */
        setupEventDetailsDialogListeners(backdrop, dialog, event, props) {
            const closeDialog = () => {
                if (backdrop && backdrop.parentNode) {
                    backdrop.parentNode.removeChild(backdrop);
                }
                this.eventDetailsDialog = null;
            };

            // Close button
            const closeBtn = dialog.querySelector('.close-btn');
            if (closeBtn) {
                closeBtn.addEventListener('click', closeDialog);
            }

            // Cancel button
            const cancelBtn = dialog.querySelector('.cancel-btn');
            if (cancelBtn) {
                cancelBtn.addEventListener('click', closeDialog);
            }

            // Mark Complete button (for jobs only)
            const markCompleteBtn = dialog.querySelector('.mark-complete-btn');
            if (markCompleteBtn) {
                markCompleteBtn.addEventListener('click', () => {
                    this.updateJobStatus(event, props, 'completed', closeDialog);
                });
            }

            // Edit button
            const editBtn = dialog.querySelector('.edit-btn');
            if (editBtn) {
                editBtn.addEventListener('click', () => {
                    // Switch to edit mode instead of closing
                    this.switchToEditMode(backdrop, dialog, event, props);
                });
            }

            // Backdrop click
            backdrop.addEventListener('click', (e) => {
                if (e.target === backdrop) {
                    closeDialog();
                }
            });

            // Escape key
            const handleEscape = (e) => {
                if (e.key === 'Escape') {
                    closeDialog();
                    document.removeEventListener('keydown', handleEscape);
                }
            };
            document.addEventListener('keydown', handleEscape);
        }

        /**
         * Show error message
         * @param {string} message - Error message to display
         */
        showError(message) {
            console.error('JobCalendar Error:', message);
            // Use the global toast system if available, otherwise use the local toast method
            if (window.layout && window.layout.showToast) {
                window.layout.showToast(message, 'error');
            } else {
                this.showToast(message, 'error');
            }
        }

        /**
         * Update job status
         * @param {Object} event - FullCalendar event
         * @param {Object} props - Event extended properties
         * @param {string} newStatus - New status to set
         * @param {Function} closeDialog - Function to close the dialog
         */
        async updateJobStatus(event, props, newStatus, closeDialog) {
            try {
                if (!confirm(`Are you sure you want to mark this job as ${newStatus}?`)) {
                    return;
                }

                // Extract job ID from event ID (remove "job-" prefix)
                const jobId = event.id.replace(/^job-/, '');
                
                // Get CSRF token
                const csrfToken = this.getCSRFToken();
                
                const response = await fetch(`/api/jobs/${jobId}/update-status/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({
                        status: newStatus
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // Show success message
                    this.showSuccess('Job status updated successfully!');
                    
                    // Close dialog
                    closeDialog();
                    
                    // Refresh calendar to show updated status
                    this.loadCalendarData();
                } else {
                    this.showError(data.error || 'Failed to update job status');
                }
            } catch (error) {
                console.error('JobCalendar: Error updating job status', error);
                this.showError('Network error occurred while updating status');
            }
        }

        /**
         * Show success message
         * @param {string} message - Success message to display
         */
        showSuccess(message) {
            console.log('JobCalendar Success:', message);
            // Use the global toast system if available, otherwise use the local toast method
            if (window.layout && window.layout.showToast) {
                window.layout.showToast(message, 'success');
            } else {
                this.showToast(message, 'success');
            }
        }

        /**
         * Switch dialog to edit mode
         * @param {HTMLElement} backdrop - Dialog backdrop
         * @param {HTMLElement} dialog - Dialog container
         * @param {Object} event - FullCalendar event
         * @param {Object} props - Event extended properties
         */
        switchToEditMode(backdrop, dialog, event, props) {
            try {
                console.log('JobCalendar: Switching to edit mode', { event, props });
                
                // Build edit content
                const editContent = this.buildJobEventEditContent(event, props);
                dialog.innerHTML = editContent;
                
                // Setup edit mode listeners
                this.setupEditModeListeners(backdrop, dialog, event, props);
                
            } catch (error) {
                console.error('JobCalendar: Error switching to edit mode', error);
                this.showError('Unable to switch to edit mode. Please try again.');
            }
        }

        /**
         * Build edit content for job events
         * @param {Object} event - FullCalendar event
         * @param {Object} props - Event extended properties
         * @returns {string} HTML content
         */
        buildJobEventEditContent(event, props) {
            const jobId = props.job_id || event.id.replace(/^job-/, '');
            const status = props.status || 'uncompleted';
            
            // Define status display and badge functions locally
            const getJobStatusDisplay = (status) => {
                return status ? status.charAt(0).toUpperCase() + status.slice(1) : 'Unknown';
            };
            
            const getJobStatusBadge = (status) => {
                const statusDisplay = getJobStatusDisplay(status);
                let backgroundColor, textColor;
                
                switch (status ? status.toLowerCase() : '') {
                    case 'completed':
                        backgroundColor = '#10b981';
                        textColor = '#ffffff';
                        break;
                    case 'in_progress':
                        backgroundColor = '#f59e0b';
                        textColor = '#ffffff';
                        break;
                    case 'pending':
                        backgroundColor = '#6b7280';
                        textColor = '#ffffff';
                        break;
                    case 'cancelled':
                        backgroundColor = '#ef4444';
                        textColor = '#ffffff';
                        break;
                    default:
                        backgroundColor = '#f59e0b';
                        textColor = '#ffffff';
                        break;
                }
                
                return `display: inline-flex; align-items: center; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 600; background-color: ${backgroundColor}; color: ${textColor};`;
            };
            
            const statusDisplay = getJobStatusDisplay(status);
            const statusBadge = getJobStatusBadge(status);

            // Format dates for input fields
            const formatDateForInput = (dateStr) => {
                if (!dateStr) return '';
                const date = new Date(dateStr);
                // Check if date is valid
                if (isNaN(date.getTime())) return '';
                // Convert to local timezone and format for datetime-local input
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                return `${year}-${month}-${day}T${hours}:${minutes}`;
            };

            return `
                <div class="event-details-dialog" style="max-width: 800px; max-height: 90vh; overflow: hidden; background-color: #ffffff; border-radius: 16px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); margin: 20px;">
                    <!-- Header -->
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 24px 24px 0 24px; border-bottom: 1px solid #e5e7eb; margin-bottom: 0;">
                        <h2 style="font-size: 24px; font-weight: bold; color: #111827; margin: 0;">Edit Job</h2>
                        <div style="${statusBadge}">${statusDisplay}</div>
                    </div>

                    <!-- Scrollable Content -->
                    <div style="max-height: calc(90vh - 200px); overflow-y: auto; padding: 24px;">
                        <form id="edit-job-form" class="space-y-6">
                            <!-- Customer Information -->
                            <div style="background-color: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden;">
                                <div style="display: flex; align-items: center; gap: 8px; background-color: #f3f4f6; padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                                    <svg style="width: 16px; height: 16px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                                    </svg>
                                    <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0;">Customer Information</h3>
                                </div>
                                <div style="padding: 20px;">
                                    <div class="grid-responsive" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="business_name">Business Name *</label>
                                            <input type="text" id="business_name" name="business_name" value="${props.business_name || ''}" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;" required>
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="contact_name">Contact Name</label>
                                            <input type="text" id="contact_name" name="contact_name" value="${props.contact_name || ''}" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="phone">Phone</label>
                                            <input type="tel" id="phone" name="phone" value="${props.phone || ''}" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Trailer Information -->
                            <div style="background-color: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden;">
                                <div style="display: flex; align-items: center; gap: 8px; background-color: #f3f4f6; padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                                    <svg style="width: 16px; height: 16px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"></path>
                                        <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1V8a1 1 0 00-1-1h-3z"></path>
                                    </svg>
                                    <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0;">Trailer Information</h3>
                                </div>
                                <div style="padding: 20px;">
                                    <div class="grid-responsive" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="trailer_color">Color</label>
                                            <input type="text" id="trailer_color" name="trailer_color" value="${props.trailer_color || ''}" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="trailer_serial">Serial Number</label>
                                            <input type="text" id="trailer_serial" name="trailer_serial" value="${props.trailer_serial || ''}" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                        </div>
                                        <div style="grid-column: 1 / -1;">
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="trailer_details">Details</label>
                                            <textarea id="trailer_details" name="trailer_details" rows="3" 
                                                      style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff; resize: vertical;">${props.trailer_details || ''}</textarea>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Schedule Information -->
                            <div style="background-color: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden;">
                                <div style="display: flex; align-items: center; gap: 8px; background-color: #f3f4f6; padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                                    <svg style="width: 16px; height: 16px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"></path>
                                    </svg>
                                    <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0;">Schedule Information</h3>
                                </div>
                                <div style="padding: 20px;">
                                    <div class="grid-responsive" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="start_dt">Start Date & Time</label>
                                            <input type="datetime-local" id="start_dt" name="start_dt" value="${formatDateForInput(event.start)}" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="end_dt">End Date & Time</label>
                                            <input type="datetime-local" id="end_dt" name="end_dt" value="${formatDateForInput(event.end)}" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                        </div>
                                        <div>
                                            <label style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;">
                                                <input type="checkbox" id="all_day" name="all_day" ${event.allDay ? 'checked' : ''} 
                                                       style="width: 16px; height: 16px; accent-color: #3b82f6;">
                                                All Day Event
                                            </label>
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="status">Status</label>
                                            <select id="status" name="status" style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                                <option value="uncompleted" ${status === 'uncompleted' ? 'selected' : ''}>Uncompleted</option>
                                                <option value="completed" ${status === 'completed' ? 'selected' : ''}>Completed</option>
                                                <option value="cancelled" ${status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Notes -->
                            <div style="background-color: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden;">
                                <div style="display: flex; align-items: center; gap: 8px; background-color: #f3f4f6; padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                                    <svg style="width: 16px; height: 16px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"></path>
                                    </svg>
                                    <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0;">Notes</h3>
                                </div>
                                <div style="padding: 20px;">
                                    <div class="grid-responsive" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="notes">General Notes</label>
                                            <textarea id="notes" name="notes" rows="4" 
                                                      style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff; resize: vertical;">${props.notes || ''}</textarea>
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="repair_notes">Repair Notes</label>
                                            <textarea id="repair_notes" name="repair_notes" rows="4" 
                                                      style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff; resize: vertical;">${props.repair_notes || ''}</textarea>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>

                    <!-- Footer -->
                    <div style="display: flex; justify-content: flex-end; gap: 12px; padding: 20px 24px; border-top: 1px solid #e5e7eb; background-color: #ffffff;">
                        <button type="button" class="cancel-btn" style="padding: 10px 20px; border: 1px solid #d1d5db; border-radius: 8px; background-color: #ffffff; color: #374151; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;">Cancel</button>
                        <button type="button" class="save-btn" style="padding: 10px 20px; border: none; border-radius: 8px; background-color: #3b82f6; color: #ffffff; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;">Save Changes</button>
                    </div>
                </div>
            `;
        }

        /**
         * Build new job form content
         * @param {Object} event - Mock event object with clicked date/time
         * @param {Object} props - Mock props for new job
         * @returns {string} HTML content
         */
        buildNewJobFormContent(event, props) {
            // Format dates for input fields
            const formatDateForInput = (dateStr) => {
                if (!dateStr) return '';
                const date = new Date(dateStr);
                // Check if date is valid
                if (isNaN(date.getTime())) return '';
                // Convert to local timezone and format for datetime-local input
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                return `${year}-${month}-${day}T${hours}:${minutes}`;
            };

            return `
                <div class="event-details-dialog" style="max-width: 800px; max-height: 90vh; overflow: hidden; background-color: #ffffff; border-radius: 16px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); margin: 20px;">
                    <!-- Header -->
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 24px 24px 0 24px; border-bottom: 1px solid #e5e7eb; margin-bottom: 0;">
                        <h2 style="font-size: 24px; font-weight: bold; color: #111827; margin: 0;">Create New Job</h2>
                        <div style="display: inline-flex; align-items: center; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 600; background-color: #f59e0b; color: #ffffff;">New</div>
                    </div>

                    <!-- Scrollable Content -->
                    <div style="max-height: calc(90vh - 200px); overflow-y: auto; padding: 24px;">
                        <form id="new-job-form" class="space-y-6">
                            <!-- Customer Information -->
                            <div style="background-color: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden;">
                                <div style="display: flex; align-items: center; gap: 8px; background-color: #f3f4f6; padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                                    <svg style="width: 16px; height: 16px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                                    </svg>
                                    <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0;">Customer Information</h3>
                                </div>
                                <div style="padding: 20px;">
                                    <div class="grid-responsive" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="business_name">Business Name *</label>
                                            <input type="text" id="business_name" name="business_name" value="" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;" required>
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="contact_name">Contact Name</label>
                                            <input type="text" id="contact_name" name="contact_name" value="" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="phone">Phone</label>
                                            <input type="tel" id="phone" name="phone" value="" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Trailer Information -->
                            <div style="background-color: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden;">
                                <div style="display: flex; align-items: center; gap: 8px; background-color: #f3f4f6; padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                                    <svg style="width: 16px; height: 16px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"></path>
                                        <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1V8a1 1 0 00-1-1h-3z"></path>
                                    </svg>
                                    <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0;">Trailer Information</h3>
                                </div>
                                <div style="padding: 20px;">
                                    <div class="grid-responsive" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="trailer_color">Color</label>
                                            <input type="text" id="trailer_color" name="trailer_color" value="" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="trailer_serial">Serial Number</label>
                                            <input type="text" id="trailer_serial" name="trailer_serial" value="" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                        </div>
                                        <div style="grid-column: 1 / -1;">
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="trailer_details">Trailer Details</label>
                                            <textarea id="trailer_details" name="trailer_details" rows="3" 
                                                      style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff; resize: vertical;"></textarea>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Schedule Information -->
                            <div style="background-color: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden;">
                                <div style="display: flex; align-items: center; gap: 8px; background-color: #f3f4f6; padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                                    <svg style="width: 16px; height: 16px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"></path>
                                    </svg>
                                    <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0;">Schedule Information</h3>
                                </div>
                                <div style="padding: 20px;">
                                    <div class="grid-responsive" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="start_dt">Start Date & Time</label>
                                            <input type="datetime-local" id="start_dt" name="start_dt" value="${formatDateForInput(event.start)}" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;" required>
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="end_dt">End Date & Time</label>
                                            <input type="datetime-local" id="end_dt" name="end_dt" value="${formatDateForInput(event.end)}" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                        </div>
                                        <div>
                                            <label style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;">
                                                <input type="checkbox" id="all_day" name="all_day" ${event.allDay ? 'checked' : ''} 
                                                       style="width: 16px; height: 16px; accent-color: #3b82f6;">
                                                All Day Event
                                            </label>
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="status">Status</label>
                                            <select id="status" name="status" style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                                <option value="uncompleted" selected>Uncompleted</option>
                                                <option value="completed">Completed</option>
                                                <option value="cancelled">Cancelled</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Notes -->
                            <div style="background-color: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden;">
                                <div style="display: flex; align-items: center; gap: 8px; background-color: #f3f4f6; padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                                    <svg style="width: 16px; height: 16px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"></path>
                                    </svg>
                                    <h3 style="font-size: 16px; font-weight: 600; color: #374151; margin: 0;">Notes</h3>
                                </div>
                                <div style="padding: 20px;">
                                    <div class="grid-responsive" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="notes">Job Notes</label>
                                            <textarea id="notes" name="notes" rows="3" 
                                                      style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff; resize: vertical;"></textarea>
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="repair_notes">Repair Notes</label>
                                            <textarea id="repair_notes" name="repair_notes" rows="3" 
                                                      style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff; resize: vertical;"></textarea>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>

                    <!-- Footer -->
                    <div style="display: flex; justify-content: flex-end; gap: 12px; padding: 20px 24px; border-top: 1px solid #e5e7eb; background-color: #ffffff;">
                        <button type="button" class="cancel-btn" style="padding: 10px 20px; border: 1px solid #d1d5db; border-radius: 8px; background-color: #ffffff; color: #374151; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;">Cancel</button>
                        <button type="button" class="create-btn" style="padding: 10px 20px; border: none; border-radius: 8px; background-color: #10b981; color: #ffffff; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;">Create Job</button>
                    </div>
                </div>
            `;
        }

        /**
         * Setup edit mode event listeners
         * @param {HTMLElement} backdrop - Dialog backdrop
         * @param {HTMLElement} dialog - Dialog container
         * @param {Object} event - FullCalendar event
         * @param {Object} props - Event extended properties
         */
        setupEditModeListeners(backdrop, dialog, event, props) {
            const closeDialog = () => {
                if (backdrop && backdrop.parentNode) {
                    backdrop.parentNode.removeChild(backdrop);
                }
                this.eventDetailsDialog = null;
            };

            // Cancel button
            const cancelBtn = dialog.querySelector('.cancel-btn');
            if (cancelBtn) {
                cancelBtn.addEventListener('click', () => {
                    // Switch back to detail view
                    this.switchToDetailMode(backdrop, dialog, event, props);
                });
            }

            // Save button
            const saveBtn = dialog.querySelector('.save-btn');
            if (saveBtn) {
                saveBtn.addEventListener('click', () => {
                    this.saveJobChanges(backdrop, dialog, event, props);
                });
            }

            // Backdrop click
            backdrop.addEventListener('click', (e) => {
                if (e.target === backdrop) {
                    closeDialog();
                }
            });

            // Escape key
            const handleEscape = (e) => {
                if (e.key === 'Escape') {
                    closeDialog();
                    document.removeEventListener('keydown', handleEscape);
                }
            };
            document.addEventListener('keydown', handleEscape);
        }

        /**
         * Setup new job dialog event listeners
         * @param {HTMLElement} backdrop - Dialog backdrop
         * @param {HTMLElement} dialog - Dialog container
         * @param {Object} event - Mock event object
         * @param {Object} props - Mock props for new job
         */
        setupNewJobDialogListeners(backdrop, dialog, event, props) {
            const closeDialog = () => {
                if (backdrop && backdrop.parentNode) {
                    backdrop.parentNode.removeChild(backdrop);
                }
                this.eventDetailsDialog = null;
            };

            // Cancel button
            const cancelBtn = dialog.querySelector('.cancel-btn');
            if (cancelBtn) {
                cancelBtn.addEventListener('click', closeDialog);
            }

            // Create button
            const createBtn = dialog.querySelector('.create-btn');
            if (createBtn) {
                createBtn.addEventListener('click', () => {
                    this.createNewJob(backdrop, dialog, event, props);
                });
            }

            // Backdrop click
            backdrop.addEventListener('click', (e) => {
                if (e.target === backdrop) {
                    closeDialog();
                }
            });

            // Escape key
            const handleEscape = (e) => {
                if (e.key === 'Escape') {
                    closeDialog();
                    document.removeEventListener('keydown', handleEscape);
                }
            };
            document.addEventListener('keydown', handleEscape);
        }

        /**
         * Switch back to detail mode
         * @param {HTMLElement} backdrop - Dialog backdrop
         * @param {HTMLElement} dialog - Dialog container
         * @param {Object} event - FullCalendar event
         * @param {Object} props - Event extended properties
         */
        switchToDetailMode(backdrop, dialog, event, props) {
            try {
                console.log('JobCalendar: Switching back to detail mode');
                
                // Build detail content
                const detailContent = this.buildJobEventContent(event, props);
                dialog.innerHTML = detailContent;
                
                // Setup detail mode listeners
                this.setupEventDetailsDialogListeners(backdrop, dialog, event, props);
                
            } catch (error) {
                console.error('JobCalendar: Error switching to detail mode', error);
                this.showError('Unable to switch to detail mode. Please try again.');
            }
        }

        /**
         * Save job changes
         * @param {HTMLElement} backdrop - Dialog backdrop
         * @param {HTMLElement} dialog - Dialog container
         * @param {Object} event - FullCalendar event
         * @param {Object} props - Event extended properties
         */
        saveJobChanges(backdrop, dialog, event, props) {
            try {
                console.log('JobCalendar: Saving job changes');
                
                const form = dialog.querySelector('#edit-job-form');
                const formData = new FormData(form);
                
                // Convert FormData to object
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                
                // Add job ID
                data.job_id = props.job_id || event.id.replace(/^job-/, '');
                
                console.log('JobCalendar: Saving data', data);
                
                // Get CSRF token and log for debugging
                const csrfToken = this.getCSRFToken();
                console.log('JobCalendar: CSRF Token:', csrfToken);
                
                // Send update request with proper CSRF headers
                fetch(`/api/jobs/${data.job_id}/update/`, {
                    method: 'POST',
                    credentials: 'same-origin',  // Send cookies so CsrfViewMiddleware can see csrftoken
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,   // exact header name + cookie name
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(data)
                })
                .then(response => {
                    if (!response.ok) {
                        // Read and log the response body for debugging
                        return response.text().then(text => {
                            console.error('JobCalendar: Save failed', response.status, text);
                            throw new Error(`HTTP ${response.status}: ${text}`);
                        });
                    }
                    return response.json();
                })
                .then(result => {
                    console.log('JobCalendar: Job updated successfully', result);
                    
                    // Update the event in the calendar
                    this.updateCalendarEvent(event, result);
                    
                    // Switch back to detail view with updated data
                    this.switchToDetailMode(backdrop, dialog, event, result);
                    
                    // Show success message
                    this.showSuccess('Job updated successfully!');
                })
                .catch(error => {
                    console.error('JobCalendar: Error saving job', error);
                    this.showError(`Error saving job: ${error.message}`);
                });
                
            } catch (error) {
                console.error('JobCalendar: Error saving job changes', error);
                this.showError('Unable to save changes. Please try again.');
            }
        }

        /**
         * Update calendar event with new data
         * @param {Object} event - FullCalendar event
         * @param {Object} newData - Updated job data
         */
        updateCalendarEvent(event, newData) {
            try {
                // Update event properties
                event.setExtendedProp('business_name', newData.business_name);
                event.setExtendedProp('contact_name', newData.contact_name);
                event.setExtendedProp('phone', newData.phone);
                event.setExtendedProp('trailer_color', newData.trailer_color);
                event.setExtendedProp('trailer_serial', newData.trailer_serial);
                event.setExtendedProp('trailer_details', newData.trailer_details);
                event.setExtendedProp('start_dt', newData.start_dt);
                event.setExtendedProp('end_dt', newData.end_dt);
                event.setExtendedProp('all_day', newData.all_day);
                event.setExtendedProp('status', newData.status);
                event.setExtendedProp('notes', newData.notes);
                event.setExtendedProp('repair_notes', newData.repair_notes);
                
                // Update event title if needed
                if (newData.business_name) {
                    event.setTitle(newData.business_name);
                }
                
                // Update event dates if changed
                if (newData.start_dt) {
                    event.setStart(newData.start_dt);
                }
                if (newData.end_dt) {
                    event.setEnd(newData.end_dt);
                }
                
                // Update allDay property
                if (newData.all_day !== undefined) {
                    event.setAllDay(newData.all_day === 'on' || newData.all_day === true);
                }
                
                console.log('JobCalendar: Calendar event updated');
                
            } catch (error) {
                console.error('JobCalendar: Error updating calendar event', error);
            }
        }

        /**
         * Create new job
         * @param {HTMLElement} backdrop - Dialog backdrop
         * @param {HTMLElement} dialog - Dialog container
         * @param {Object} event - Mock event object
         * @param {Object} props - Mock props for new job
         */
        createNewJob(backdrop, dialog, event, props) {
            try {
                console.log('JobCalendar: Creating new job');
                
                const form = dialog.querySelector('#new-job-form');
                const formData = new FormData(form);
                
                // Convert FormData to object
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                
                console.log('JobCalendar: Creating job with data', data);
                
                // Get CSRF token
                const csrfToken = this.getCSRFToken();
                console.log('JobCalendar: CSRF Token:', csrfToken);
                
                // Send create request
                fetch('/api/jobs/create/', {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(data)
                })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            console.error('JobCalendar: Create failed', response.status, text);
                            throw new Error(`HTTP ${response.status}: ${text}`);
                        });
                    }
                    return response.json();
                })
                .then(result => {
                    console.log('JobCalendar: Job created successfully', result);
                    
                    // Close the dialog
                    if (backdrop && backdrop.parentNode) {
                        backdrop.parentNode.removeChild(backdrop);
                    }
                    this.eventDetailsDialog = null;
                    
                    // Refresh the calendar to show the new job
                    this.calendar.refetchEvents();
                    
                    // Show success message
                    this.showSuccess('Job created successfully!');
                })
                .catch(error => {
                    console.error('JobCalendar: Error creating job', error);
                    this.showError(`Error creating job: ${error.message}`);
                });
                
            } catch (error) {
                console.error('JobCalendar: Error creating new job', error);
                this.showError('Unable to create job. Please try again.');
            }
        }

        /**
         * Get CSRF token for API requests
         * @returns {string} CSRF token
         */
        getCSRFToken() {
            // Use global getCookie function if available, otherwise fallback to local implementation
            if (typeof window.getCookie === 'function') {
                return window.getCookie('csrftoken');
            }
            
            // Fallback implementation
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
         * Show success message
         * @param {string} message - Success message
         */
        showSuccess(message) {
            console.log('JobCalendar Success:', message);
            // Use the global toast system if available, otherwise use the local toast method
            if (window.layout && window.layout.showToast) {
                window.layout.showToast(message, 'success');
            } else {
                this.showToast(message, 'success');
            }
        }

        /**
         * Cleanup method for removing event listeners and resetting state
         */
        destroy() {
            // Close event details dialog if open
            if (this.eventDetailsDialog && this.eventDetailsDialog.parentNode) {
                this.eventDetailsDialog.parentNode.removeChild(this.eventDetailsDialog);
                this.eventDetailsDialog = null;
            }

            if (this.calendar) {
                this.calendar.destroy();
            }
            console.log('JobCalendar: Destroyed');
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


