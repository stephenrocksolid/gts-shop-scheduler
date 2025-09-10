/**
 * Calendar - Manages FullCalendar integration for contract scheduling
 * Handles calendar rendering, filtering, and event management
 */

// Wrap in IIFE to avoid global conflicts
(function () {
    'use strict';

    // Defensive loading - only declare Calendar if it doesn't already exist
    if (typeof window.Calendar === 'undefined') {

        class Calendar {
            constructor(config = {}) {
                // Configuration and dependencies
                this.config = config;
                this.calendar = null;
                this.calendarEl = null;
                this.categoryFilter = null;
                this.trailerFilter = null;
                this.statusFilter = null;
                this.loadingEl = null;
                this.statusPopover = null;
                this.activeEventEl = null;

                // State management
                this.isInitialized = false;
                this.isLoading = false;
                this.clickTimer = null;
                this.clickDelay = 300; // milliseconds to wait for double click

                // Initialize if dependencies are available
                this.initialize();
            }

            /**
             * Initialize the calendar module
             */
            initialize() {
                // Check for required dependencies
                if (!window.RentalConfig) {
                    window.Logger?.error('Calendar: RentalConfig is required but not available');
                    return;
                }

                if (!window.Logger) {
                    console.warn('Calendar: Logger not available, falling back to console logging');
                }

                // Check for FullCalendar dependency
                if (typeof FullCalendar === 'undefined') {
                    window.Logger?.error('Calendar: FullCalendar library is required but not available');
                    return;
                }

                // Initialize DOM elements
                this.initializeElements();

                if (!this.validateElements()) {
                    window.Logger?.error('Calendar: Required calendar elements not found');
                    return;
                }

                // Setup calendar and event listeners
                this.setupCalendar();
                this.setupEventListeners();

                // Initial data load
                this.loadInitialData();

                this.isInitialized = true;
                window.Logger?.debug('Calendar initialized successfully');
            }

            /**
             * Initialize DOM element references using RentalConfig
             */
            initializeElements() {
                this.calendarEl = document.getElementById('calendar');
                this.categoryFilter = window.RentalConfig.getField('categoryFilter') ||
                    document.getElementById('category-filter');
                this.trailerFilter = window.RentalConfig.getField('trailerFilter') ||
                    document.getElementById('trailer-filter');
                this.statusFilter = window.RentalConfig.getField('statusFilter') ||
                    document.getElementById('status-filter');
                this.loadingEl = window.RentalConfig.getDisplay('calendarLoading') ||
                    document.getElementById('calendar-loading');
            }

            /**
             * Validate that required elements exist
             * @returns {boolean} True if all required elements are present
             */
            validateElements() {
                const required = {
                    calendarEl: this.calendarEl,
                    categoryFilter: this.categoryFilter,
                    trailerFilter: this.trailerFilter,
                    statusFilter: this.statusFilter
                };

                const missing = Object.entries(required)
                    .filter(([name, element]) => !element)
                    .map(([name]) => name);

                if (missing.length > 0) {
                    window.Logger?.error('Calendar: Missing required elements', { missing });
                    return false;
                }

                return true;
            }

            /**
             * Setup FullCalendar instance
             */
            setupCalendar() {
                try {
                    this.calendar = new FullCalendar.Calendar(this.calendarEl, {
                        initialView: 'dayGridMonth',
                        buttonText: {
                            today: 'Today'
                        },
                        headerToolbar: {
                            left: 'prev,next today',
                            center: 'title',
                            right: ''
                        },
                        height: 'auto',
                        eventTimeFormat: {
                            hour: '2-digit',
                            minute: '2-digit',
                            meridiem: false,
                            hour12: false
                        },
                        displayEventEnd: true,
                        displayEventTime: true,
                        eventDisplay: 'block',
                        dayMaxEvents: false,
                        dayMaxEventRows: false,
                        moreLinkClick: 'popover',
                        // Fix for multi-day events not showing on intermediate days
                        nextDayThreshold: '00:00:00',
                        // Force all events to show times
                        allDaySlot: false,
                        // Customize how events are rendered to force time display
                        eventContent: function (arg) {
                            const event = arg.event;
                            const timeFormat = { hour: '2-digit', minute: '2-digit', hour12: false };

                            // Format start and end times
                            const startTime = event.start ? event.start.toLocaleTimeString('en-US', timeFormat) : '';
                            const endTime = event.end ? event.end.toLocaleTimeString('en-US', timeFormat) : '';

                            // Create custom HTML content with inline display
                            let content = '';
                            if (startTime && endTime) {
                                content += `<span class="fc-event-time">${startTime}-${endTime}</span> `;
                            } else if (startTime) {
                                content += `<span class="fc-event-time">${startTime}</span> `;
                            }
                            content += `<span class="fc-event-title">${event.title}</span>`;

                            return { html: content };
                        },
                        eventDidMount: (info) => this.handleEventMount(info),
                        eventClick: (info) => this.handleEventClick(info),
                        loading: (isLoading) => this.handleLoadingState(isLoading)
                    });

                    // Render the calendar
                    this.calendar.render();
                    window.Logger?.debug('Calendar: FullCalendar instance created and rendered');

                } catch (error) {
                    window.Logger?.error('Calendar: Failed to setup FullCalendar', error);
                    this.showError('Failed to initialize calendar. Please refresh the page.');
                }
            }

            /**
             * Setup event listeners for filters
             */
            setupEventListeners() {
                // Category filter change
                if (this.categoryFilter) {
                    this.categoryFilter.addEventListener('change', async () => {
                        window.Logger?.debug('Calendar: Category filter changed', {
                            category: this.categoryFilter.value
                        });
                        await this.updateTrailerOptions();
                        await this.updateCalendarEvents();
                    });
                }

                // Trailer filter change
                if (this.trailerFilter) {
                    this.trailerFilter.addEventListener('change', async () => {
                        window.Logger?.debug('Calendar: Trailer filter changed', {
                            trailer: this.trailerFilter.value
                        });
                        await this.updateCalendarEvents();
                    });
                }

                // Status filter change
                if (this.statusFilter) {
                    this.statusFilter.addEventListener('change', async () => {
                        window.Logger?.debug('Calendar: Status filter changed', {
                            status: this.statusFilter.value
                        });
                        await this.updateCalendarEvents();
                    });
                }

                window.Logger?.debug('Calendar: Event listeners setup complete');
            }

            /**
             * Handle event mounting for styling and tooltips
             * @param {Object} info - FullCalendar event info
             */
            handleEventMount(info) {
                try {
                    // Add tooltip
                    info.el.title = info.event.extendedProps.tooltip || '';

                    // Add status-based class
                    if (info.event.extendedProps.type === 'service' || info.event.extendedProps.is_service) {
                        info.el.classList.add('event-service');
                    } else if (info.event.extendedProps.is_overdue) {
                        info.el.classList.add('event-overdue');
                    } else if (info.event.extendedProps.is_picked_up) {
                        info.el.classList.add('event-picked-up');
                    } else if (info.event.extendedProps.is_returned) {
                        info.el.classList.add('event-returned');
                    } else {
                        info.el.classList.add('event-pending');
                    }

                    window.Logger?.debug('Calendar: Event mounted with styling', {
                        eventId: info.event.id,
                        title: info.event.title,
                        status: this.getEventStatus(info.event.extendedProps)
                    });

                } catch (error) {
                    window.Logger?.warn('Calendar: Error mounting event', error);
                }
            }

            /**
             * Handle event click navigation - distinguishes between single and double clicks
             * @param {Object} info - FullCalendar event info
             */
            handleEventClick(info) {
                try {
                    if (this.statusPopover) {
                        this.closeStatusPopover();
                    }

                    // Clear any existing timer
                    if (this.clickTimer) {
                        clearTimeout(this.clickTimer);
                        this.clickTimer = null;

                        // This is a double click - navigate to appropriate form
                        this.handleEventDoubleClick(info);
                        return;
                    }

                    // Set timer for single click detection
                    this.clickTimer = setTimeout(() => {
                        this.clickTimer = null;
                        // This is a single click - show popover (only for contracts)
                        this.handleEventSingleClick(info);
                    }, this.clickDelay);

                } catch (error) {
                    window.Logger?.error('Calendar: Error handling event click', error);
                    this.showError('Unable to handle calendar event. Please try again.');
                }
            }

            /**
             * Handle single click on event - shows event details dialog
             * @param {Object} info - FullCalendar event info
             */
            handleEventSingleClick(info) {
                try {
                    window.Logger?.debug('Calendar: Single click detected', {
                        eventId: info.event.id,
                        title: info.event.title,
                        type: info.event.extendedProps.type
                    });
                    this.openEventDetailsDialog(info);
                } catch (error) {
                    window.Logger?.error('Calendar: Error handling single click', error);
                    this.showError('Unable to open event details. Please try again.');
                }
            }

            /**
             * Handle double click on event - navigates to contract or service form
             * @param {Object} info - FullCalendar event info
             */
            handleEventDoubleClick(info) {
                try {
                    const eventId = info.event.id;

                    // Check if this is a service event
                    if (info.event.extendedProps.type === 'service' || info.event.extendedProps.is_service) {
                        // Extract numeric ID from service event ID (remove "service-" prefix)
                        const serviceId = eventId.replace(/^service-/, '');
                        window.Logger?.debug('Calendar: Double click on service event, navigating to service form', {
                            eventId: eventId,
                            serviceId: serviceId,
                            title: info.event.title
                        });

                        // Close any open popover first
                        this.closeStatusPopover();

                        // Navigate to service update form
                        const serviceUrl = `/service/${serviceId}/update/?next=${encodeURIComponent(window.location.pathname)}`;
                        window.location.href = serviceUrl;

                    } else {
                        // Handle contract events (including overdue events)
                        // Extract numeric ID from event ID, handling both "contract-123" and "contract-123-overdue" formats
                        let contractId = eventId.replace(/^contract-/, '');
                        // Remove any suffix like "-overdue" to get just the numeric ID
                        contractId = contractId.replace(/-overdue$/, '');

                        window.Logger?.debug('Calendar: Double click on contract event, navigating to contract form', {
                            eventId: eventId,
                            contractId: contractId,
                            title: info.event.title,
                            isOverdue: eventId.includes('-overdue')
                        });

                        // Close any open popover first
                        this.closeStatusPopover();

                        // Navigate to contract update form
                        const contractUrl = `/contracts/${contractId}/update/?next=${encodeURIComponent(window.location.pathname)}`;
                        window.location.href = contractUrl;
                    }

                } catch (error) {
                    window.Logger?.error('Calendar: Error handling double click', error);
                    this.showError('Unable to open form. Please try again.');
                }
            }

            openStatusPopover(info) {
                // Extract numeric ID from event ID, handling both "contract-123" and "contract-123-overdue" formats
                let contractId = info.event.id.replace(/^contract-/, '');
                // Remove any suffix like "-overdue" to get just the numeric ID
                contractId = contractId.replace(/-overdue$/, '');
                this.closeStatusPopover();

                // Get the latest event data from the calendar to ensure we have fresh info
                const latestEvent = this.calendar?.getEventById(info.event.id);
                const eventProps = latestEvent ? latestEvent.extendedProps : info.event.extendedProps;

                // Create popover element
                const pop = document.createElement('div');
                pop.className = 'status-popover';
                document.body.appendChild(pop);
                this.statusPopover = pop;
                this.activeEventEl = info.el;
                info.el.classList.add('event-active');

                // Prevent popover clicks from closing it
                pop.addEventListener('click', e => e.stopPropagation());

                // Setup outside click handler
                setTimeout(() => {
                    document.addEventListener('click', this.boundCloseStatusPopover = () => this.closeStatusPopover(), { once: true });
                }, 0);

                // Build form content using latest event data
                const p = eventProps;

                // Format return date if available
                const formatReturnDate = (isoDateString) => {
                    if (!isoDateString) return '';
                    try {
                        const date = new Date(isoDateString);
                        return date.toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            hour: 'numeric',
                            minute: '2-digit',
                            hour12: true
                        });
                    } catch (error) {
                        return '';
                    }
                };

                const returnDateDisplay = p.return_datetime ? ` (${formatReturnDate(p.return_datetime)})` : '';

                const fields = [
                    ['is_billed', 'Billed', p.is_billed],
                    ['is_invoiced', 'Send Invoice', p.is_invoiced],
                    ['is_picked_up', 'Picked Up', p.is_picked_up],
                    ['is_returned', `Returned${returnDateDisplay}`, p.is_returned]
                ];

                let html = '<div class="font-semibold text-gray-800 mb-2">' + info.event.title + '</div>';

                // Add license scanning status badge
                const licenseScanned = p.drivers_license_scanned;
                const badgeStyles = licenseScanned
                    ? 'background-color:#d1fae5;color:#065f46;'
                    : 'background-color:#fee2e2;color:#991b1b;';
                const badgeText = licenseScanned ? 'License Scanned' : 'License Not Scanned';
                html += '<div class="mb-3">';
                html += '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" style="' + badgeStyles + '">';
                html += badgeText;
                html += '</span>';
                html += '</div>';

                html += '<form hx-put="/contracts/' + contractId + '/status/" hx-trigger="change" hx-swap="none">';

                fields.forEach(f => {
                    // Special handling for is_returned - don't trigger immediate HTMX
                    const triggerAttr = f[0] === 'is_returned' ? '' : '';
                    html += '<label class="flex items-center gap-2 mb-1">';
                    html += '<input type="checkbox" name="' + f[0] + '"' + (f[2] ? ' checked' : '') + ' class="mr-2"' + triggerAttr + '>';
                    html += '<span>' + f[1] + '</span>';
                    html += '</label>';
                });

                html += '</form>';

                // Set the HTML content
                pop.innerHTML = html;

                // Add special event listener for is_returned checkbox
                const returnedCheckbox = pop.querySelector('input[name="is_returned"]');

                if (returnedCheckbox) {
                    const calendarInstance = this;
                    returnedCheckbox.addEventListener('change', (e) => {
                        if (e.target.checked) {
                            // Show return date dialog instead of immediate submission
                            e.preventDefault();
                            e.stopPropagation();
                            // Prefer contract end as default when present
                            const defaultReturn = p.return_datetime || info.event.end || null;
                            calendarInstance.showReturnDateDialog(contractId, info, defaultReturn);
                            // Uncheck the box until user confirms in dialog
                            e.target.checked = false;
                        } else {
                            // Allow unchecking to happen immediately
                            calendarInstance.updateContractStatus(contractId, { is_returned: false, return_datetime: null });
                        }
                    });
                }

                // IMPORTANT: Tell HTMX to process the new elements (except is_returned)
                if (typeof htmx !== 'undefined') {
                    htmx.process(pop);

                    // Add event listeners to other checkboxes for additional debugging
                    const checkboxes = pop.querySelectorAll('input[type="checkbox"]:not([name="is_returned"])');
                    checkboxes.forEach(checkbox => {
                        checkbox.addEventListener('change', function (e) {
                            window.Logger?.debug('Calendar: Checkbox changed', {
                                name: e.target.name,
                                checked: e.target.checked,
                                form: e.target.form
                            });
                        });
                    });
                } else {
                    window.Logger?.error('Calendar: HTMX not available for processing form', {
                        htmxExists: typeof htmx,
                        windowHtmx: !!window.htmx
                    });
                }

                // Position the popover
                const popWidth = pop.offsetWidth;
                const popHeight = pop.offsetHeight;
                const rect = info.el.getBoundingClientRect();
                let left = rect.right + 8;
                let top = rect.top;
                let flip = false;

                if (left + popWidth > window.innerWidth) {
                    left = rect.left - popWidth - 8;
                    flip = true;
                }

                if (left < 8) {
                    left = 8;
                }
                if (left + popWidth > window.innerWidth - 8) {
                    left = Math.max(8, window.innerWidth - popWidth - 8);
                }

                top = Math.min(Math.max(top, 8), window.innerHeight - popHeight - 8);

                const docLeft = left + window.scrollX;
                const docTop = top + window.scrollY;
                pop.style.left = docLeft + 'px';
                pop.style.top = docTop + 'px';

                if (flip) {
                    pop.classList.add('arrow-right');
                } else {
                    pop.classList.remove('arrow-right');
                }

                window.Logger?.debug('Calendar: Status popover opened', {
                    contractId,
                    position: { left: docLeft, top: docTop },
                    fields: fields.map(f => ({ name: f[0], label: f[1], checked: f[2] }))
                });
            }

            /**
             * Show return date dialog modal
             * @param {string} contractId - Contract ID (numeric, without prefix)
             * @param {Object} eventInfo - Calendar event info
             * @param {string|null} existingReturnDateTime - Existing return datetime if any
             */
            showReturnDateDialog(contractId, eventInfo, existingReturnDateTime) {
                // Remove any existing modal
                this.removeReturnDateDialog();

                // Temporarily disable the popover's outside click handler
                if (this.boundCloseStatusPopover) {
                    document.removeEventListener('click', this.boundCloseStatusPopover);
                    this.boundCloseStatusPopover = null;
                }

                // Get default return datetime (today at 6:59 AM)
                const getDefaultReturnDateTime = () => {
                    const now = new Date();
                    // 6 hours 59 minutes represents 6:59 AM in 24-hour time
                    return new Date(now.getFullYear(), now.getMonth(), now.getDate(), 6, 59);
                };

                const defaultDate = existingReturnDateTime ? new Date(existingReturnDateTime) : getDefaultReturnDateTime();
                const formattedDate = this.toDateTimeLocalFormat(defaultDate);

                // Create modal backdrop
                const backdrop = document.createElement('div');
                backdrop.className = 'return-dialog-backdrop';
                backdrop.id = 'return-dialog-backdrop';

                // Create modal content
                const modal = document.createElement('div');
                modal.className = 'return-dialog-modal';
                modal.id = 'return-dialog-modal';

                modal.innerHTML = `
                    <div class="return-dialog-header">
                        <h3 class="return-dialog-title">Mark Trailer as Returned</h3>
                        <button type="button" class="return-dialog-close" id="return-dialog-close">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    <div class="return-dialog-body">
                        <p class="return-dialog-text">Please specify the return date and time for:</p>
                        <p class="return-dialog-contract"><strong>${eventInfo.event.title}</strong></p>
                        <div class="return-dialog-input-group">
                            <label for="return-datetime-input" class="return-dialog-label">Return Date & Time</label>
                            <input type="datetime-local" id="return-datetime-input" class="return-dialog-input" value="${formattedDate}">
                        </div>
                    </div>
                    <div class="return-dialog-footer">
                        <button type="button" class="return-dialog-btn return-dialog-btn-cancel" id="return-dialog-cancel">Cancel</button>
                        <button type="button" class="return-dialog-btn return-dialog-btn-save" id="return-dialog-save">Save Return</button>
                    </div>
                `;

                backdrop.appendChild(modal);
                document.body.appendChild(backdrop);

                // Store references
                this.returnDialogBackdrop = backdrop;
                this.returnDialogModal = modal;

                // Prevent modal clicks from bubbling up
                modal.addEventListener('click', (e) => {
                    e.stopPropagation();
                });

                // Add event listeners
                const closeBtn = modal.querySelector('#return-dialog-close');
                const cancelBtn = modal.querySelector('#return-dialog-cancel');
                const saveBtn = modal.querySelector('#return-dialog-save');
                const input = modal.querySelector('#return-datetime-input');

                const closeDialog = () => {
                    this.removeReturnDateDialog();
                    // Re-establish the popover outside click handler if popover is still open
                    if (this.statusPopover && !this.boundCloseStatusPopover) {
                        setTimeout(() => {
                            document.addEventListener('click', this.boundCloseStatusPopover = () => this.closeStatusPopover(), { once: true });
                        }, 0);
                    }
                };

                closeBtn.addEventListener('click', closeDialog);
                cancelBtn.addEventListener('click', closeDialog);
                backdrop.addEventListener('click', (e) => {
                    if (e.target === backdrop) closeDialog();
                });

                saveBtn.addEventListener('click', () => {
                    const returnDateTime = input.value;
                    if (!returnDateTime) {
                        alert('Please select a return date and time.');
                        return;
                    }

                    // Update the contract status with return datetime
                    this.updateContractStatus(contractId, {
                        is_returned: true,
                        return_datetime: returnDateTime
                    });

                    closeDialog();
                });

                // Focus on the input field
                setTimeout(() => input.focus(), 100);

                window.Logger?.debug('Calendar: Return date dialog opened', { contractId, defaultDate: formattedDate });
            }

            /**
             * Remove return date dialog modal
             */
            removeReturnDateDialog() {
                if (this.returnDialogBackdrop && this.returnDialogBackdrop.parentNode) {
                    this.returnDialogBackdrop.parentNode.removeChild(this.returnDialogBackdrop);
                }
                this.returnDialogBackdrop = null;
                this.returnDialogModal = null;
            }

            /**
 * Update contract status via HTMX API call
 * @param {string} contractId - Contract ID
 * @param {Object} statusData - Status data to update
 */
            updateContractStatus(contractId, statusData) {
                try {
                    // Get the current event to access all current status values
                    // getEventById expects the full event ID with prefix
                    const currentEvent = this.calendar?.getEventById(`contract-${contractId}`);
                    if (!currentEvent) {
                        throw new Error('Could not find current event data');
                    }

                    // Build URL-encoded form data with ALL current checkbox states
                    const formParams = new URLSearchParams();

                    // Get current status from event extended props
                    const currentProps = currentEvent.extendedProps;

                    // Define all checkbox fields that need to be maintained
                    const allCheckboxFields = {
                        'is_billed': currentProps.is_billed,
                        'is_invoiced': currentProps.is_invoiced,
                        'is_picked_up': currentProps.is_picked_up,
                        'is_returned': currentProps.is_returned
                    };

                    // Apply the status updates to the current state
                    Object.keys(statusData).forEach(key => {
                        if (key in allCheckboxFields) {
                            allCheckboxFields[key] = statusData[key];
                        }
                    });

                    // Add all checkbox fields to form data (only if they're true)
                    Object.keys(allCheckboxFields).forEach(key => {
                        if (allCheckboxFields[key]) {
                            formParams.append(key, 'on');
                        }
                    });

                    // Add non-checkbox fields (like return_datetime)
                    Object.keys(statusData).forEach(key => {
                        if (!(key in allCheckboxFields) && statusData[key] !== null && statusData[key] !== undefined) {
                            formParams.append(key, statusData[key]);
                        }
                    });

                    // Make the API call
                    fetch(`/contracts/${contractId}/status/`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': this.getCSRFToken(),
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: formParams.toString()
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success') {
                                window.Logger?.debug('Calendar: Contract status updated successfully', { contractId, statusData, response: data });

                                // Trigger the same event handling as HTMX would
                                const xhr = {
                                    status: 200,
                                    responseText: JSON.stringify(data),
                                    getResponseHeader: () => 'application/json'
                                };
                                const event = new CustomEvent('htmx:afterOnLoad', {
                                    detail: { xhr: xhr }
                                });
                                document.body.dispatchEvent(event);

                                // Remove any synthetic overdue event immediately
                                try {
                                    const overdue = this.calendar?.getEventById(`contract-${contractId}-overdue`);
                                    if (overdue) {
                                        overdue.remove();
                                    }
                                    // Update the base event end time and flags if we received a return date
                                    const base = this.calendar?.getEventById(`contract-${contractId}`);
                                    const newReturnIso = data.return_datetime || statusData.return_datetime || null;
                                    if (base && newReturnIso) {
                                        base.setEnd(new Date(newReturnIso));
                                        base.setExtendedProp('is_returned', true);
                                        base.setExtendedProp('is_overdue', false);
                                        base.setExtendedProp('return_datetime', newReturnIso);
                                    }
                                } catch (e) {
                                    window.Logger?.warn('Calendar: immediate overdue cleanup failed', e);
                                }

                                // Update popup checkboxes if popover is open
                                this.updatePopoverAfterStatusChange(contractId, data);

                                // Ensure calendar reflects new styling/colors
                                this.updateCalendarEvents();
                            } else {
                                throw new Error(data.error || 'Failed to update contract status');
                            }
                        })
                        .catch(error => {
                            window.Logger?.error('Calendar: Error updating contract status', error);
                            alert('Failed to update contract status. Please try again.');
                        });

                } catch (error) {
                    window.Logger?.error('Calendar: Error preparing status update', error);
                    alert('Failed to update contract status. Please try again.');
                }
            }

            /**
 * Update popover content after status change
 * @param {string} contractId - Contract ID
 * @param {Object} statusData - Updated status data
 */
            updatePopoverAfterStatusChange(contractId, statusData) {
                if (!this.statusPopover) return;

                // Get the updated event from calendar
                const latestEvent = this.calendar?.getEventById(`contract-${contractId}`);
                if (!latestEvent) return;

                // Update checkboxes based on new status
                const checkboxes = {
                    'is_billed': this.statusPopover.querySelector('input[name="is_billed"]'),
                    'is_invoiced': this.statusPopover.querySelector('input[name="is_invoiced"]'),
                    'is_picked_up': this.statusPopover.querySelector('input[name="is_picked_up"]'),
                    'is_returned': this.statusPopover.querySelector('input[name="is_returned"]')
                };

                // Update checkbox states
                Object.keys(checkboxes).forEach(fieldName => {
                    const checkbox = checkboxes[fieldName];
                    if (checkbox && statusData[fieldName] !== undefined) {
                        checkbox.checked = statusData[fieldName];
                    }
                });

                // Update the "Returned" label to show/hide date based on status
                const returnedCheckbox = checkboxes['is_returned'];
                if (returnedCheckbox) {
                    const label = returnedCheckbox.parentElement.querySelector('span');
                    if (label) {
                        if (statusData.is_returned && statusData.return_datetime) {
                            // Show date when returned
                            const formatReturnDate = (isoDateString) => {
                                try {
                                    const date = new Date(isoDateString);
                                    return date.toLocaleDateString('en-US', {
                                        month: 'short',
                                        day: 'numeric',
                                        hour: 'numeric',
                                        minute: '2-digit',
                                        hour12: true
                                    });
                                } catch (error) {
                                    return '';
                                }
                            };

                            const returnDate = formatReturnDate(statusData.return_datetime);
                            label.textContent = `Returned (${returnDate})`;
                        } else {
                            // Hide date when not returned
                            label.textContent = 'Returned';
                        }
                    }
                }

                window.Logger?.debug('Calendar: Popover updated after status change', { contractId, statusData });
            }

            /**
             * Get CSRF token for API requests
             * @returns {string} CSRF token
             */
            getCSRFToken() {
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    const [name, value] = cookie.trim().split('=');
                    if (name === 'csrftoken') {
                        return value;
                    }
                }

                // Fallback to meta tag
                const csrfMeta = document.querySelector('meta[name="csrf-token"]');
                if (csrfMeta) {
                    return csrfMeta.getAttribute('content');
                }

                return '';
            }

            /**
             * Convert Date object to datetime-local input format
             * @param {Date} date - Date object  
             * @returns {string} datetime-local format (YYYY-MM-DDTHH:MM)
             */
            toDateTimeLocalFormat(date) {
                try {
                    // Handle both Date objects and strings
                    if (typeof date === 'string') {
                        date = new Date(date);
                    }

                    if (!(date instanceof Date) || isNaN(date.getTime())) {
                        // Fallback to current date at 6:59 PM if invalid
                        const now = new Date();
                        date = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 18, 59);
                    }

                    // Convert to local time and format for datetime-local input
                    const year = date.getFullYear();
                    const month = String(date.getMonth() + 1).padStart(2, '0');
                    const day = String(date.getDate()).padStart(2, '0');
                    const hours = String(date.getHours()).padStart(2, '0');
                    const minutes = String(date.getMinutes()).padStart(2, '0');

                    return `${year}-${month}-${day}T${hours}:${minutes}`;
                } catch (error) {
                    window.Logger?.warn('Calendar: Error formatting datetime', error);
                    // Return current date at 6:59 PM as fallback
                    const now = new Date();
                    const fallback = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 18, 59);
                    const year = fallback.getFullYear();
                    const month = String(fallback.getMonth() + 1).padStart(2, '0');
                    const day = String(fallback.getDate()).padStart(2, '0');
                    return `${year}-${month}-${day}T18:59`;
                }
            }

            closeStatusPopover() {
                if (this.statusPopover && this.statusPopover.parentNode) {
                    this.statusPopover.parentNode.removeChild(this.statusPopover);
                }
                this.statusPopover = null;
                if (this.boundCloseStatusPopover) {
                    document.removeEventListener('click', this.boundCloseStatusPopover);
                    this.boundCloseStatusPopover = null;
                }
                if (this.activeEventEl) {
                    this.activeEventEl.classList.remove('event-active');
                    this.activeEventEl = null;
                }

                // Clear any pending click timer when closing popover
                if (this.clickTimer) {
                    clearTimeout(this.clickTimer);
                    this.clickTimer = null;
                }

                // Also close any open return date dialog
                this.removeReturnDateDialog();
            }

            /**
             * Open comprehensive event details dialog
             * @param {Object} info - FullCalendar event info
             */
            openEventDetailsDialog(info) {
                try {
                    // Close any existing popover first
                    this.closeStatusPopover();

                    // Get the latest event data from the calendar to ensure we have fresh info
                    const latestEvent = this.calendar?.getEventById(info.event.id);
                    const eventProps = latestEvent ? latestEvent.extendedProps : info.event.extendedProps;
                    const event = latestEvent || info.event;

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
                    dialog.className = 'event-details-dialog';
                    dialog.style.cssText = `
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                        max-width: 600px;
                        width: 100%;
                        max-height: 80vh;
                        overflow-y: auto;
                        position: relative;
                    `;

                    // Build dialog content based on event type
                    let content = '';
                    const eventType = eventProps.type || 'unknown';

                    if (eventType === 'contract') {
                        content = this.buildContractEventContent(event, eventProps);
                    } else if (eventType === 'service') {
                        content = this.buildServiceEventContent(event, eventProps);
                    } else if (eventType === 'job') {
                        content = this.buildJobEventContent(event, eventProps);
                    } else {
                        content = this.buildGenericEventContent(event, eventProps);
                    }

                    dialog.innerHTML = content;

                    // Add to DOM
                    backdrop.appendChild(dialog);
                    document.body.appendChild(backdrop);

                    // Setup event listeners
                    this.setupEventDetailsDialogListeners(backdrop, dialog, event, eventProps);

                    // Store reference for cleanup
                    this.eventDetailsDialog = backdrop;

                } catch (error) {
                    window.Logger?.error('Calendar: Error opening event details dialog', error);
                    this.showError('Unable to open event details. Please try again.');
                }
            }

            /**
             * Build content for contract events
             * @param {Object} event - FullCalendar event
             * @param {Object} props - Event extended properties
             * @returns {string} HTML content
             */
            buildContractEventContent(event, props) {
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

                const getStatusBadge = (props) => {
                    if (props.is_overdue) {
                        return '<span class="status-badge overdue">Overdue</span>';
                    } else if (props.is_returned) {
                        return '<span class="status-badge returned">Returned</span>';
                    } else if (props.is_picked_up) {
                        return '<span class="status-badge picked-up">Picked Up</span>';
                    } else {
                        return '<span class="status-badge pending">Pending</span>';
                    }
                };

                const getLicenseBadge = (scanned) => {
                    const badgeClass = scanned ? 'license-scanned' : 'license-not-scanned';
                    const badgeText = scanned ? 'License Scanned' : 'License Not Scanned';
                    return `<span class="license-badge ${badgeClass}">${badgeText}</span>`;
                };

                return `
                    <div class="event-details-header">
                        <h3 class="event-title">${event.title}</h3>
                        <button class="close-btn" type="button">&times;</button>
                    </div>
                    <div class="event-details-body">
                        <div class="status-section">
                            ${getStatusBadge(props)}
                            ${getLicenseBadge(props.drivers_license_scanned)}
                        </div>
                        
                        <div class="details-grid">
                            <div class="detail-group">
                                <h4>Customer Information</h4>
                                <div class="detail-item">
                                    <span class="label">Name:</span>
                                    <span class="value">${props.customer_name || 'N/A'}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Phone:</span>
                                    <span class="value">${props.customer_phone || 'N/A'}</span>
                                </div>
                            </div>
                            
                            <div class="detail-group">
                                <h4>Trailer Information</h4>
                                <div class="detail-item">
                                    <span class="label">Number:</span>
                                    <span class="value">${props.trailer_number || 'N/A'}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Model:</span>
                                    <span class="value">${props.trailer_model || 'N/A'}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Includes Winch:</span>
                                    <span class="value">${props.includes_winch ? 'Yes' : 'No'}</span>
                                </div>
                            </div>
                            
                            <div class="detail-group">
                                <h4>Schedule</h4>
                                <div class="detail-item">
                                    <span class="label">Start:</span>
                                    <span class="value">${formatDateTime(event.start)}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">End:</span>
                                    <span class="value">${formatDateTime(event.end)}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Pickup:</span>
                                    <span class="value">${formatDateTime(props.pickup_datetime)}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Return:</span>
                                    <span class="value">${formatDateTime(props.return_datetime)}</span>
                                </div>
                            </div>
                            
                            <div class="detail-group">
                                <h4>Status</h4>
                                <div class="detail-item">
                                    <span class="label">Billed:</span>
                                    <span class="value">${props.is_billed ? 'Yes' : 'No'}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Invoiced:</span>
                                    <span class="value">${props.is_invoiced ? 'Yes' : 'No'}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="event-details-footer">
                        <button class="btn btn-secondary cancel-btn" type="button">Close</button>
                        <button class="btn btn-primary edit-btn" type="button">Edit Contract</button>
                    </div>
                `;
            }

            /**
             * Build content for service events
             * @param {Object} event - FullCalendar event
             * @param {Object} props - Event extended properties
             * @returns {string} HTML content
             */
            buildServiceEventContent(event, props) {
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

                const getServiceStatusBadge = (props) => {
                    if (props.is_past) {
                        return '<span class="status-badge completed">Completed</span>';
                    } else if (props.is_future) {
                        return '<span class="status-badge scheduled">Scheduled</span>';
                    } else {
                        return '<span class="status-badge active">Active</span>';
                    }
                };

                return `
                    <div class="event-details-header">
                        <h3 class="event-title">${event.title}</h3>
                        <button class="close-btn" type="button">&times;</button>
                    </div>
                    <div class="event-details-body">
                        <div class="status-section">
                            ${getServiceStatusBadge(props)}
                        </div>
                        
                        <div class="details-grid">
                            <div class="detail-group">
                                <h4>Service Information</h4>
                                <div class="detail-item">
                                    <span class="label">Description:</span>
                                    <span class="value">${props.description || 'No description provided'}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Active:</span>
                                    <span class="value">${props.is_active ? 'Yes' : 'No'}</span>
                                </div>
                            </div>
                            
                            <div class="detail-group">
                                <h4>Trailer Information</h4>
                                <div class="detail-item">
                                    <span class="label">Number:</span>
                                    <span class="value">${props.trailer_number || 'N/A'}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Model:</span>
                                    <span class="value">${props.trailer_model || 'N/A'}</span>
                                </div>
                            </div>
                            
                            <div class="detail-group">
                                <h4>Schedule</h4>
                                <div class="detail-item">
                                    <span class="label">Start:</span>
                                    <span class="value">${formatDateTime(event.start)}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">End:</span>
                                    <span class="value">${formatDateTime(event.end)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="event-details-footer">
                        <button class="btn btn-secondary cancel-btn" type="button">Close</button>
                        <button class="btn btn-primary edit-btn" type="button">Edit Service</button>
                    </div>
                `;
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
                    const statusClass = status.toLowerCase().replace(' ', '-');
                    return `<span class="status-badge ${statusClass}">${props.status_display || status}</span>`;
                };

                return `
                    <div class="event-details-header">
                        <h3 class="event-title">${event.title}</h3>
                        <button class="close-btn" type="button">&times;</button>
                    </div>
                    <div class="event-details-body">
                        <div class="status-section">
                            ${getJobStatusBadge(props.status)}
                        </div>
                        
                        <div class="details-grid">
                            <div class="detail-group">
                                <h4>Customer Information</h4>
                                <div class="detail-item">
                                    <span class="label">Name:</span>
                                    <span class="value">${props.customer_name || 'N/A'}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Phone:</span>
                                    <span class="value">${props.customer_phone || 'N/A'}</span>
                                </div>
                            </div>
                            
                            <div class="detail-group">
                                <h4>Trailer Information</h4>
                                <div class="detail-item">
                                    <span class="label">Number:</span>
                                    <span class="value">${props.trailer_number || 'N/A'}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Model:</span>
                                    <span class="value">${props.trailer_model || 'N/A'}</span>
                                </div>
                            </div>
                            
                            <div class="detail-group">
                                <h4>Schedule</h4>
                                <div class="detail-item">
                                    <span class="label">Start:</span>
                                    <span class="value">${formatDateTime(event.start)}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">End:</span>
                                    <span class="value">${formatDateTime(event.end)}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">All Day:</span>
                                    <span class="value">${event.allDay ? 'Yes' : 'No'}</span>
                                </div>
                            </div>
                            
                            ${props.repair_notes ? `
                            <div class="detail-group">
                                <h4>Repair Notes</h4>
                                <div class="detail-item full-width">
                                    <span class="value">${props.repair_notes}</span>
                                </div>
                            </div>
                            ` : ''}
                            
                            ${props.quote_text ? `
                            <div class="detail-group">
                                <h4>Quote</h4>
                                <div class="detail-item full-width">
                                    <span class="value">${props.quote_text}</span>
                                </div>
                            </div>
                            ` : ''}
                            
                            ${props.calendar_name ? `
                            <div class="detail-group">
                                <h4>Calendar</h4>
                                <div class="detail-item">
                                    <span class="label">Name:</span>
                                    <span class="value">${props.calendar_name}</span>
                                </div>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                    <div class="event-details-footer">
                        <button class="btn btn-secondary cancel-btn" type="button">Close</button>
                        <button class="btn btn-primary edit-btn" type="button">Edit Job</button>
                    </div>
                `;
            }

            /**
             * Build content for generic/unknown events
             * @param {Object} event - FullCalendar event
             * @param {Object} props - Event extended properties
             * @returns {string} HTML content
             */
            buildGenericEventContent(event, props) {
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

                return `
                    <div class="event-details-header">
                        <h3 class="event-title">${event.title}</h3>
                        <button class="close-btn" type="button">&times;</button>
                    </div>
                    <div class="event-details-body">
                        <div class="details-grid">
                            <div class="detail-group">
                                <h4>Event Information</h4>
                                <div class="detail-item">
                                    <span class="label">Type:</span>
                                    <span class="value">${props.type || 'Unknown'}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Start:</span>
                                    <span class="value">${formatDateTime(event.start)}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">End:</span>
                                    <span class="value">${formatDateTime(event.end)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="event-details-footer">
                        <button class="btn btn-secondary cancel-btn" type="button">Close</button>
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

                // Edit button
                const editBtn = dialog.querySelector('.edit-btn');
                if (editBtn) {
                    editBtn.addEventListener('click', () => {
                        closeDialog();
                        this.handleEventDoubleClick({ event: event });
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
             * Handle calendar loading state
             * @param {boolean} isLoading - Whether calendar is loading
             */
            handleLoadingState(isLoading) {
                this.isLoading = isLoading;

                if (this.loadingEl) {
                    if (isLoading) {
                        this.loadingEl.classList.remove('hidden');
                        window.Logger?.debug('Calendar: Loading state activated');
                    } else {
                        this.loadingEl.classList.add('hidden');
                        window.Logger?.debug('Calendar: Loading state deactivated');
                    }
                }
            }

            /**
             * Update trailer options based on selected category
             */
            async updateTrailerOptions() {
                if (!this.categoryFilter || !this.trailerFilter) return;

                const categoryId = this.categoryFilter.value;
                this.trailerFilter.disabled = !categoryId;

                if (!categoryId) {
                    this.trailerFilter.innerHTML = '<option value="">Select a category first</option>';
                    return;
                }

                try {
                    window.Logger?.showLoading(this.trailerFilter, 'Loading trailers...');

                    const response = await fetch(
                        `${window.RentalConfig.getApiUrl('getAvailableTrailers')}?category=${categoryId}`,
                        {
                            headers: window.RentalConfig.getApiHeaders()
                        }
                    );

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const data = await response.json();

                    // Clear and populate trailer options
                    this.trailerFilter.innerHTML = '<option value="">All Trailers</option>';
                    data.trailers.forEach(trailer => {
                        const option = document.createElement('option');
                        option.value = trailer.id;

                        // Build display text: Number - Model - Hauling capacity (if exists and > 0) - Size
                        let displayText = `${trailer.number} - ${trailer.model}`;
                        if (trailer.hauling_capacity && trailer.hauling_capacity > 0) {
                            displayText += ` - ${trailer.hauling_capacity.toLocaleString()} lbs`;
                        }
                        if (trailer.size) {
                            displayText += ` (${trailer.size})`;
                        }

                        option.textContent = displayText;
                        this.trailerFilter.appendChild(option);
                    });

                    window.Logger?.debug('Calendar: Trailer options updated', {
                        categoryId,
                        trailerCount: data.trailers.length
                    });

                } catch (error) {
                    window.Logger?.error('Calendar: Error fetching trailers', error);
                    this.trailerFilter.innerHTML = '<option value="">Unable to load trailers</option>';
                    this.showError('Failed to load trailers. Please try again.');
                } finally {
                    window.Logger?.hideLoading(this.trailerFilter);
                }
            }

            /**
             * Update calendar events based on current filter selections
             */
            async updateCalendarEvents() {
                if (!this.calendar) return;

                const filters = {
                    categoryId: this.categoryFilter?.value || '',
                    trailerId: this.trailerFilter?.value || '',
                    status: this.statusFilter?.value || ''
                };

                try {
                    window.Logger?.debug('Calendar: Updating events', filters);

                    const params = new URLSearchParams();
                    if (filters.categoryId) params.append('category', filters.categoryId);
                    if (filters.trailerId) params.append('trailer', filters.trailerId);

                    const response = await fetch(
                        `${window.RentalConfig.getApiUrl('calendarData')}?${params.toString()}`,
                        {
                            headers: window.RentalConfig.getApiHeaders()
                        }
                    );

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const data = await response.json();

                    // Clear existing events
                    this.calendar.removeAllEvents();

                    // Filter events based on status
                    const filteredEvents = this.filterEventsByStatus(data.events, filters.status);

                    // Add new events
                    this.calendar.addEventSource(filteredEvents);

                    window.Logger?.debug('Calendar: Events updated', {
                        totalEvents: data.events.length,
                        filteredEvents: filteredEvents.length,
                        filters
                    });

                } catch (error) {
                    window.Logger?.error('Calendar: Error fetching calendar data', error);
                    this.showError('Failed to load calendar events. Please try again.');
                }
            }

            /**
             * Filter events by status
             * @param {Array} events - Array of calendar events
             * @param {string} status - Status filter ('pending', 'picked_up', 'returned', or '')
             * @returns {Array} Filtered events
             */
            filterEventsByStatus(events, status) {
                if (!status) return events; // Show all if no status filter

                return events.filter(event => {
                    if (status === 'pending') {
                        return !event.extendedProps.is_picked_up && !event.extendedProps.is_returned;
                    } else if (status === 'picked_up') {
                        return event.extendedProps.is_picked_up && !event.extendedProps.is_returned;
                    } else if (status === 'returned') {
                        return event.extendedProps.is_returned;
                    }
                    return true;
                });
            }

            /**
             * Get event status for logging
             * @param {Object} extendedProps - Event extended properties
             * @returns {string} Status string
             */
            getEventStatus(extendedProps) {
                if (extendedProps.is_returned) return 'returned';
                if (extendedProps.is_picked_up) return 'picked_up';
                return 'pending';
            }

            /**
             * Load initial data
             */
            async loadInitialData() {
                try {
                    await this.updateTrailerOptions();
                    await this.updateCalendarEvents();
                    window.Logger?.info('Calendar: Initial data loaded successfully');
                } catch (error) {
                    window.Logger?.error('Calendar: Error loading initial data', error);
                }
            }

            /**
             * Show error message to user
             * @param {string} message - Error message to display
             */
            showError(message) {
                // Create a temporary error notification
                const errorDiv = document.createElement('div');
                errorDiv.className = 'fixed top-4 right-4 bg-red-50 border border-red-200 rounded-md p-4 z-50';
                errorDiv.innerHTML = `
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm text-red-700">${message}</p>
                        </div>
                        <div class="ml-auto pl-3">
                            <button class="text-red-400 hover:text-red-600" onclick="this.parentElement.parentElement.parentElement.remove()">
                                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                                </svg>
                            </button>
                        </div>
                    </div>
                `;

                document.body.appendChild(errorDiv);

                // Auto-remove after 5 seconds
                setTimeout(() => {
                    if (errorDiv && errorDiv.parentNode) {
                        errorDiv.parentNode.removeChild(errorDiv);
                    }
                }, 5000);
            }

            /**
             * Refresh calendar data
             */
            async refresh() {
                if (!this.isInitialized) {
                    window.Logger?.warn('Calendar: Cannot refresh - not initialized');
                    return;
                }

                window.Logger?.debug('Calendar: Refreshing data');
                await this.updateCalendarEvents();
            }

            /**
             * Cleanup method for removing event listeners and resetting state
             */
            destroy() {
                // Clear any pending click timer
                if (this.clickTimer) {
                    clearTimeout(this.clickTimer);
                    this.clickTimer = null;
                }

                // Close any open popover and dialogs
                this.closeStatusPopover();
                this.removeReturnDateDialog();
                
                // Close event details dialog if open
                if (this.eventDetailsDialog && this.eventDetailsDialog.parentNode) {
                    this.eventDetailsDialog.parentNode.removeChild(this.eventDetailsDialog);
                    this.eventDetailsDialog = null;
                }

                if (this.calendar) {
                    this.calendar.destroy();
                }
                this.isInitialized = false;
                window.Logger?.debug('Calendar: Destroyed');
            }
        }

        // Export Calendar class to global scope
        window.Calendar = Calendar;

        // Auto-initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', function () {
            // Wait for dependencies to be available
            if (window.RentalConfig && window.FullCalendar) {
                window.calendarInstance = new Calendar();
            } else {
                // Wait a bit for dependencies to load
                setTimeout(() => {
                    if (window.RentalConfig && window.FullCalendar) {
                        window.calendarInstance = new Calendar();
                    } else {
                        console.error('Calendar: Required dependencies not available (RentalConfig, FullCalendar)');
                    }
                }, 200);
            }
        });

        // Enhanced HTMX event handling with debugging
        document.body.addEventListener('htmx:configRequest', function (e) {
            window.Logger?.debug('Calendar: HTMX request config', {
                verb: e.detail.verb,
                path: e.detail.path,
                headers: e.detail.headers
            });
        });

        document.body.addEventListener('htmx:beforeRequest', function (e) {
            window.Logger?.debug('Calendar: HTMX request starting', {
                verb: e.detail.verb,
                path: e.detail.path
            });
        });

        document.body.addEventListener('htmx:afterRequest', function (e) {
            window.Logger?.debug('Calendar: HTMX request completed', {
                verb: e.detail.verb,
                path: e.detail.path,
                status: e.detail.xhr.status,
                response: e.detail.xhr.responseText
            });
        });

        document.body.addEventListener('htmx:afterOnLoad', function (e) {
            const xhr = e.detail.xhr;
            const ct = (xhr.getResponseHeader && xhr.getResponseHeader('Content-Type')) || '';

            window.Logger?.debug('Calendar: HTMX afterOnLoad event', {
                contentType: ct,
                status: xhr.status,
                responseText: xhr.responseText
            });

            if (ct.includes('application/json')) {
                let data;
                try {
                    data = JSON.parse(xhr.responseText);
                    window.Logger?.debug('Calendar: Parsed JSON response', data);
                } catch (err) {
                    window.Logger?.error('Calendar: Failed to parse JSON response', err);
                    return;
                }

                if (data && data.id) {
                    const calendar = window.calendarInstance?.calendar;
                    const eventId = String(data.id);
                    const ev = calendar?.getEventById(`contract-${eventId}`);

                    window.Logger?.debug('Calendar: Looking for event to update', {
                        searchId: eventId,
                        foundEvent: !!ev,
                        hasElement: !!(ev && ev.el)
                    });

                    if (ev) {
                        // Get the current event data before removing it
                        const eventData = {
                            id: ev.id,
                            title: ev.title,
                            start: ev.start,
                            end: ev.end,
                            backgroundColor: ev.backgroundColor,
                            borderColor: ev.borderColor,
                            extendedProps: {
                                ...ev.extendedProps,
                                // Update with new status
                                is_picked_up: data.is_picked_up,
                                is_returned: data.is_returned,
                                is_billed: data.is_billed,
                                is_invoiced: data.is_invoiced
                            }
                        };

                        // Determine new colors based on status using centralized config
                        let backgroundColor, borderColor;
                        if (data.is_returned) {
                            backgroundColor = window.RentalConfig.getStatusColor('returned');
                            borderColor = backgroundColor;
                        } else if (data.is_picked_up) {
                            backgroundColor = window.RentalConfig.getStatusColor('pickedUp');
                            borderColor = backgroundColor;
                        } else {
                            backgroundColor = window.RentalConfig.getStatusColor('pending');
                            borderColor = backgroundColor;
                        }

                        eventData.backgroundColor = backgroundColor;
                        eventData.borderColor = borderColor;

                        window.Logger?.debug('Calendar: Removing and re-adding event with updated properties', {
                            eventId: data.id,
                            oldColors: { bg: ev.backgroundColor, border: ev.borderColor },
                            newColors: { bg: backgroundColor, border: borderColor },
                            statusUpdate: data.changes
                        });

                        // Remove the old event
                        ev.remove();

                        // Add the updated event
                        calendar.addEvent(eventData);

                        window.Logger?.info('Calendar: Event status updated successfully via remove/add', {
                            eventId: data.id,
                            changes: data.changes,
                            newColors: { backgroundColor, borderColor }
                        });

                    } else {
                        window.Logger?.warn('Calendar: Could not find event to update', {
                            eventId: data.id,
                            searchId: eventId,
                            allEventIds: calendar?.getEvents().map(e => e.id) || []
                        });
                    }
                } else {
                    window.Logger?.warn('Calendar: Response missing required data', data);
                }
            }
        });

    } else {
        window.Logger?.debug('Calendar already exists, skipping initialization');
    }

})(); // End of IIFE 