/**
 * Job Dialog - Reusable dialog component for job details and editing
 * Can be used on both Calendar and Jobs pages
 */

(function () {
    'use strict';

    class JobDialog {
        constructor() {
            this.currentDialog = null;
            this.csrfToken = this.getCSRFToken();
        }

        /**
         * Get CSRF token from cookies
         */
        getCSRFToken() {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {
                    return value;
                }
            }
            return '';
        }

        /**
         * Open job details dialog from job data
         * @param {Object} jobData - Job data object (can be minimal)
         */
        openJobDetailsDialog(jobData) {
            try {
                console.log('JobDialog: Opening job details dialog', jobData);
                
                // If we have minimal data, fetch full job details from API
                if (!jobData.business_name || !jobData.start_dt) {
                    this.fetchJobDetailsAndOpenDialog(jobData.job_id);
                } else {
                    // We have full data, open dialog directly
                    this.openDialogWithData(jobData);
                }

            } catch (error) {
                console.error('JobDialog: Error opening job details dialog', error);
                this.showError('Unable to open job details. Please try again.');
            }
        }

        /**
         * Fetch full job details from API and open dialog
         * @param {number} jobId - Job ID
         */
        fetchJobDetailsAndOpenDialog(jobId) {
            try {
                console.log('JobDialog: Fetching job details for ID', jobId);
                
                fetch(`/api/jobs/${jobId}/detail/`, {
                    method: 'GET',
                    credentials: 'same-origin',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(jobData => {
                    console.log('JobDialog: Fetched job data', jobData);
                    this.openDialogWithData(jobData);
                })
                .catch(error => {
                    console.error('JobDialog: Error fetching job details', error);
                    this.showError('Unable to load job details. Please try again.');
                });
                
            } catch (error) {
                console.error('JobDialog: Error fetching job details', error);
                this.showError('Unable to load job details. Please try again.');
            }
        }

        /**
         * Open dialog with full job data
         * @param {Object} jobData - Full job data object
         */
        openDialogWithData(jobData) {
            try {
                // Create mock event and props objects to match calendar format
                const mockEvent = {
                    id: `job-${jobData.id}`,
                    start: jobData.start_dt ? new Date(jobData.start_dt) : new Date(),
                    end: jobData.end_dt ? new Date(jobData.end_dt) : null,
                    allDay: jobData.all_day || false,
                    title: jobData.display_name || jobData.business_name || 'Job'
                };

                const mockProps = {
                    job_id: jobData.id,
                    business_name: jobData.business_name,
                    contact_name: jobData.contact_name,
                    phone: jobData.phone,
                    trailer_color: jobData.trailer_color,
                    trailer_serial: jobData.trailer_serial,
                    trailer_details: jobData.trailer_details,
                    status: jobData.status,
                    notes: jobData.notes,
                    repair_notes: jobData.repair_notes
                };

                this.openEventDetailsDialog(mockEvent, mockProps);

            } catch (error) {
                console.error('JobDialog: Error opening dialog with data', error);
                this.showError('Unable to open job details. Please try again.');
            }
        }

        /**
         * Open comprehensive event details dialog
         * @param {Object} event - Event object (can be mock)
         * @param {Object} props - Event properties
         * @param {boolean} isNewJob - Whether this is a new job creation
         */
        openEventDetailsDialog(event, props, isNewJob = false) {
            try {
                console.log('JobDialog: Opening event details dialog', { event, props });
                
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

                // Build dialog content - show edit form directly for new jobs
                let content;
                if (isNewJob) {
                    content = this.buildJobEventEditContent(event, props);
                } else {
                    content = this.buildJobEventContent(event, props);
                }
                dialog.innerHTML = content;

                // Add to DOM
                backdrop.appendChild(dialog);
                document.body.appendChild(backdrop);

                // Setup event listeners - use edit mode listeners for new jobs
                if (isNewJob) {
                    this.setupEditModeListeners(backdrop, dialog, event, props);
                } else {
                    this.setupEventDetailsDialogListeners(backdrop, dialog, event, props);
                }

                // Store reference for cleanup
                this.currentDialog = backdrop;

            } catch (error) {
                console.error('JobDialog: Error opening event details dialog', error);
                this.showError('Unable to open event details. Please try again.');
            }
        }

        /**
         * Build content for job events
         * @param {Object} event - Event object
         * @param {Object} props - Event properties
         * @returns {string} HTML content
         */
        buildJobEventContent(event, props) {
            const formatDateTime = (dateObj) => {
                if (!dateObj) return 'Not set';
                try {
                    const date = new Date(dateObj);
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
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px; display: flex; align-items: center;">
                                            <svg style="width: 16px; height: 16px; margin-right: 6px; color: #6b7280;" fill="currentColor" viewBox="0 0 20 20">
                                                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"></path>
                                            </svg>
                                            Date Call was Received
                                        </div>
                                        <div style="color: #6b7280; font-size: 14px;">${props.date_call_received ? new Date(props.date_call_received).toLocaleDateString() : 'N/A'}</div>
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
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">All Day Event</div>
                                        <div style="color: #6b7280; font-size: 14px;">${event.allDay ? 'Yes' : 'No'}</div>
                                    </div>
                                    <div></div>
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">Start Date & Time</div>
                                        <div style="color: #6b7280; font-size: 14px;">${formatDateTime(event.start)}</div>
                                    </div>
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">End Date & Time</div>
                                        <div style="color: #6b7280; font-size: 14px;">${event.end ? formatDateTime(event.end) : 'Not set'}</div>
                                    </div>
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">Repeat</div>
                                        <div style="color: #6b7280; font-size: 14px;">${props.repeat_type ? (props.repeat_type === 'annually' ? 'Annually' : `Monthly (${props.repeat_months || 1} months)`) : 'N/A'}</div>
                                    </div>
                                    <div style="grid-column: 1 / -1;">
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">General Notes</div>
                                        <div style="color: #6b7280; font-size: 14px; line-height: 1.5;">${props.notes || 'N/A'}</div>
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
                                    <div style="grid-column: 1 / -1;">
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">Repair Notes</div>
                                        <div style="color: #6b7280; font-size: 14px; line-height: 1.5;">${props.repair_notes || 'N/A'}</div>
                                    </div>
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 4px; font-size: 14px;">Quote</div>
                                        <div style="color: #6b7280; font-size: 14px;">${props.quote ? `$${props.quote}` : 'N/A'}</div>
                                    </div>
                                </div>
                            </div>
                        </div>


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
                        <button class="print-wo-btn" style="
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
                            Print WO
                        </button>
                        <button class="print-customer-copy-wo-btn" style="
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
                            Print Customer Copy WO
                        </button>
                    </div>
                </div>
            `;
        }

        /**
         * Setup event listeners for the event details dialog
         * @param {HTMLElement} backdrop - Dialog backdrop element
         * @param {HTMLElement} dialog - Dialog element
         * @param {Object} event - Event object
         * @param {Object} props - Event properties
         */
        setupEventDetailsDialogListeners(backdrop, dialog, event, props) {
            const closeDialog = () => {
                if (backdrop && backdrop.parentNode) {
                    backdrop.parentNode.removeChild(backdrop);
                }
                this.currentDialog = null;
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
                    // Switch to edit mode instead of navigating
                    this.switchToEditMode(backdrop, dialog, event, props);
                });
            }

            // Print WO button
            const printWoBtn = dialog.querySelector('.print-wo-btn');
            if (printWoBtn) {
                printWoBtn.addEventListener('click', () => {
                    // Do nothing when clicked
                });
            }

            // Print Customer Copy WO button
            const printCustomerCopyWoBtn = dialog.querySelector('.print-customer-copy-wo-btn');
            if (printCustomerCopyWoBtn) {
                printCustomerCopyWoBtn.addEventListener('click', () => {
                    // Do nothing when clicked
                });
            }

            // Backdrop click
            backdrop.addEventListener('click', (e) => {
                if (e.target === backdrop) {
                    closeDialog();
                }
            });
        }

        /**
         * Update job status
         * @param {Object} event - Event object
         * @param {Object} props - Event properties
         * @param {string} newStatus - New status
         * @param {Function} callback - Callback function
         */
        updateJobStatus(event, props, newStatus, callback) {
            try {
                console.log('JobDialog: Updating job status', { jobId: props.job_id, newStatus });
                
                const jobId = props.job_id;
                if (!jobId) {
                    this.showError('Job ID not found');
                    return;
                }

                // Send update request
                fetch(`/api/jobs/${jobId}/update/`, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        job_id: jobId,
                        status: newStatus
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            throw new Error(`HTTP ${response.status}: ${text}`);
                        });
                    }
                    return response.json();
                })
                .then(result => {
                    console.log('JobDialog: Job status updated successfully', result);
                    this.showSuccess('Job status updated successfully!');
                    
                    // Update the props with new status
                    props.status = newStatus;
                    
                    // Call callback if provided
                    if (callback) {
                        callback();
                    }
                    
                    // Refresh the calendar to show updated status
                    setTimeout(() => {
                        if (window.jobCalendar && window.jobCalendar.calendar) {
                            window.jobCalendar.calendar.refetchEvents();
                        }
                    }, 1000);
                })
                .catch(error => {
                    console.error('JobDialog: Error updating job status', error);
                    this.showError(`Error updating job status: ${error.message}`);
                });
                
            } catch (error) {
                console.error('JobDialog: Error updating job status', error);
                this.showError('Unable to update job status. Please try again.');
            }
        }

        /**
         * Show success message
         * @param {string} message - Success message
         */
        showSuccess(message) {
            this.showMessage(message, 'success');
        }

        /**
         * Show error message
         * @param {string} message - Error message
         */
        showError(message) {
            this.showMessage(message, 'error');
        }

        /**
         * Switch dialog to edit mode
         * @param {HTMLElement} backdrop - Dialog backdrop
         * @param {HTMLElement} dialog - Dialog container
         * @param {Object} event - Event object
         * @param {Object} props - Event properties
         */
        switchToEditMode(backdrop, dialog, event, props) {
            try {
                console.log('JobDialog: Switching to edit mode', { event, props });
                
                // Build edit content
                const editContent = this.buildJobEventEditContent(event, props);
                dialog.innerHTML = editContent;
                
                // Setup edit mode listeners
                this.setupEditModeListeners(backdrop, dialog, event, props);
                
            } catch (error) {
                console.error('JobDialog: Error switching to edit mode', error);
                this.showError('Unable to switch to edit mode. Please try again.');
            }
        }

        /**
         * Build edit content for job events
         * @param {Object} event - Event object
         * @param {Object} props - Event properties
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
            const formatDateForInput = (dateObj) => {
                if (!dateObj) return '';
                const date = new Date(dateObj);
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
                        <h2 style="font-size: 24px; font-weight: bold; color: #111827; margin: 0;">${jobId ? 'Edit Job' : 'Create New Job'}</h2>
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
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="date_call_received">Date Call was Received</label>
                                            <input type="date" id="date_call_received" name="date_call_received" value="${props.date_call_received ? props.date_call_received.split('T')[0] : ''}" 
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
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
                                            <label style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;">
                                                <input type="checkbox" id="all_day" name="all_day" ${event.allDay ? 'checked' : ''} 
                                                       style="width: 16px; height: 16px; accent-color: #3b82f6;">
                                                All Day Event
                                            </label>
                                        </div>
                                        <div></div>
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
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="status">Status</label>
                                            <select id="status" name="status" style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                                <option value="uncompleted" ${status === 'uncompleted' ? 'selected' : ''}>Uncompleted</option>
                                                <option value="completed" ${status === 'completed' ? 'selected' : ''}>Completed</option>
                                                <option value="cancelled" ${status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="repeat_type">Repeat</label>
                                            <select id="repeat_type" name="repeat_type" style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                                <option value="">No Repeat</option>
                                                <option value="annually" ${props.repeat_type === 'annually' ? 'selected' : ''}>Annually</option>
                                                <option value="monthly" ${props.repeat_type === 'monthly' ? 'selected' : ''}>Monthly</option>
                                            </select>
                                        </div>
                                        <div id="repeat_months_container" style="display: ${props.repeat_type === 'monthly' ? 'block' : 'none'};">
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="repeat_months">Months</label>
                                            <input type="number" id="repeat_months" name="repeat_months" value="${props.repeat_months || 1}" min="1" max="12"
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;">
                                        </div>
                                        <div style="grid-column: 1 / -1;">
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="notes">General Notes</label>
                                            <textarea id="notes" name="notes" rows="4" 
                                                      style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff; resize: vertical;">${props.notes || ''}</textarea>
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
                                        <div style="grid-column: 1 / -1;">
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="repair_notes">Repair Notes</label>
                                            <textarea id="repair_notes" name="repair_notes" rows="4" 
                                                      style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff; resize: vertical;">${props.repair_notes || ''}</textarea>
                                        </div>
                                        <div>
                                            <label style="display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px;" for="quote">Quote</label>
                                            <input type="number" id="quote" name="quote" value="${props.quote || ''}" step="0.01" min="0"
                                                   style="width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background-color: #ffffff;" placeholder="0.00">
                                        </div>
                                    </div>
                                </div>
                            </div>

                        </form>
                    </div>

                    <!-- Footer -->
                    <div style="display: flex; justify-content: flex-end; gap: 12px; padding: 20px 24px; border-top: 1px solid #e5e7eb; background-color: #ffffff;">
                        <button type="button" class="cancel-btn" style="padding: 10px 20px; border: 1px solid #d1d5db; border-radius: 8px; background-color: #ffffff; color: #374151; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;">Cancel</button>
                        <button type="button" class="print-wo-btn" style="padding: 10px 20px; border: 1px solid #d1d5db; border-radius: 8px; background-color: #ffffff; color: #374151; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;">Print WO</button>
                        <button type="button" class="print-customer-copy-wo-btn" style="padding: 10px 20px; border: 1px solid #d1d5db; border-radius: 8px; background-color: #ffffff; color: #374151; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;">Print Customer Copy WO</button>
                        <button type="button" class="save-btn" style="padding: 10px 20px; border: none; border-radius: 8px; background-color: #3b82f6; color: #ffffff; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;">${jobId ? 'Save Changes' : 'Create Job'}</button>
                    </div>
                </div>
            `;
        }

        /**
         * Setup edit mode event listeners
         * @param {HTMLElement} backdrop - Dialog backdrop
         * @param {HTMLElement} dialog - Dialog container
         * @param {Object} event - Event object
         * @param {Object} props - Event properties
         */
        setupEditModeListeners(backdrop, dialog, event, props) {
            const closeDialog = () => {
                if (backdrop && backdrop.parentNode) {
                    backdrop.parentNode.removeChild(backdrop);
                }
                this.currentDialog = null;
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
                saveBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.saveJobChanges(backdrop, dialog, event, props);
                });
            }

            // Print WO button
            const printWoBtn = dialog.querySelector('.print-wo-btn');
            if (printWoBtn) {
                printWoBtn.addEventListener('click', () => {
                    // Do nothing when clicked
                });
            }

            // Print Customer Copy WO button
            const printCustomerCopyWoBtn = dialog.querySelector('.print-customer-copy-wo-btn');
            if (printCustomerCopyWoBtn) {
                printCustomerCopyWoBtn.addEventListener('click', () => {
                    // Do nothing when clicked
                });
            }
            
            // Prevent form submission
            const form = dialog.querySelector('#edit-job-form');
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.saveJobChanges(backdrop, dialog, event, props);
                });
            }
            
            // Setup repeat type dropdown change handler
            const repeatTypeSelect = dialog.querySelector('#repeat_type');
            const repeatMonthsContainer = dialog.querySelector('#repeat_months_container');
            if (repeatTypeSelect && repeatMonthsContainer) {
                repeatTypeSelect.addEventListener('change', (e) => {
                    if (e.target.value === 'monthly') {
                        repeatMonthsContainer.style.display = 'block';
                    } else {
                        repeatMonthsContainer.style.display = 'none';
                    }
                });
            }

            // Backdrop click
            backdrop.addEventListener('click', (e) => {
                if (e.target === backdrop) {
                    closeDialog();
                }
            });
        }

        /**
         * Switch back to detail mode
         * @param {HTMLElement} backdrop - Dialog backdrop
         * @param {HTMLElement} dialog - Dialog container
         * @param {Object} event - Event object
         * @param {Object} props - Event properties
         */
        switchToDetailMode(backdrop, dialog, event, props) {
            try {
                console.log('JobDialog: Switching back to detail mode');
                
                // Build detail content
                const detailContent = this.buildJobEventContent(event, props);
                dialog.innerHTML = detailContent;
                
                // Setup detail mode listeners
                this.setupEventDetailsDialogListeners(backdrop, dialog, event, props);
                
            } catch (error) {
                console.error('JobDialog: Error switching to detail mode', error);
                this.showError('Unable to switch to detail mode. Please try again.');
            }
        }

        /**
         * Save job changes
         * @param {HTMLElement} backdrop - Dialog backdrop
         * @param {HTMLElement} dialog - Dialog container
         * @param {Object} event - Event object
         * @param {Object} props - Event properties
         */
        saveJobChanges(backdrop, dialog, event, props) {
            try {
                console.log('JobDialog: Saving job changes');
                
                const form = dialog.querySelector('#edit-job-form');
                const formData = new FormData(form);
                
                // Convert FormData to object
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                
                // Determine if this is a new job or update
                const isNewJob = !props.job_id || props.job_id === null;
                
                console.log('JobDialog: Saving data', data, 'isNewJob:', isNewJob);
                
                // Choose the appropriate API endpoint
                const url = isNewJob ? '/api/jobs/create/' : `/api/jobs/${props.job_id}/update/`;
                const method = 'POST';
                
                // Send request with proper CSRF headers
                fetch(url, {
                    method: method,
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(data)
                })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            console.error('JobDialog: Save failed', response.status, text);
                            throw new Error(`HTTP ${response.status}: ${text}`);
                        });
                    }
                    return response.json();
                })
                .then(result => {
                    console.log('JobDialog: Job saved successfully', result);
                    
                    // Update the props with new data
                    Object.assign(props, result);
                    
                    // Update the event object with new dates
                    if (result.start_dt) {
                        event.start = new Date(result.start_dt);
                    }
                    if (result.end_dt) {
                        event.end = new Date(result.end_dt);
                    }
                    event.allDay = result.all_day;
                    
                    // Show success message
                    const successMessage = isNewJob ? 'Job created successfully!' : 'Job updated successfully!';
                    this.showSuccess(successMessage);
                    
                    // Close dialog and refresh page
                    setTimeout(() => {
                        if (backdrop && backdrop.parentNode) {
                            backdrop.parentNode.removeChild(backdrop);
                        }
                        this.currentDialog = null;
                        // Refresh the calendar to show the new/updated job
                        if (window.jobCalendar && window.jobCalendar.calendar) {
                            window.jobCalendar.calendar.refetchEvents();
                        }
                    }, 1000);
                })
                .catch(error => {
                    console.error('JobDialog: Error saving job', error);
                    this.showError(`Error saving job: ${error.message}`);
                });
                
            } catch (error) {
                console.error('JobDialog: Error saving job changes', error);
                this.showError('Unable to save changes. Please try again.');
            }
        }

        /**
         * Show success message
         * @param {string} message - Success message
         */
        showSuccess(message) {
            this.showMessage(message, 'success');
        }

        /**
         * Show error message
         * @param {string} message - Error message
         */
        showError(message) {
            this.showMessage(message, 'error');
        }

        /**
         * Open new job creation dialog
         * @param {Date} clickedDate - Optional date to pre-fill (from calendar date click)
         */
        openNewJobDialog(clickedDate = null) {
            try {
                console.log('JobDialog: Opening new job dialog', { clickedDate });
                
                // Use clicked date or current time
                const startDate = clickedDate || new Date();
                const mockEvent = {
                    id: 'new-job',
                    start: startDate,
                    end: new Date(startDate.getTime() + (2 * 60 * 60 * 1000)), // Default 2 hours duration
                    allDay: false,
                    title: 'New Job'
                };

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

                this.openEventDetailsDialog(mockEvent, mockProps, true); // true indicates new job mode

            } catch (error) {
                console.error('JobDialog: Error opening new job dialog', error);
                this.showError('Unable to open new job dialog. Please try again.');
            }
        }

        /**
         * Show message
         * @param {string} message - Message text
         * @param {string} type - Message type (success, error)
         */
        showMessage(message, type) {
            const messageEl = document.createElement('div');
            messageEl.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 1001;
                max-width: 400px;
                word-wrap: break-word;
                ${type === 'success' ? 'background-color: #10b981;' : 'background-color: #ef4444;'}
            `;
            messageEl.textContent = message;
            
            document.body.appendChild(messageEl);
            
            // Remove after 3 seconds
            setTimeout(() => {
                if (messageEl.parentNode) {
                    messageEl.parentNode.removeChild(messageEl);
                }
            }, 3000);
        }
    }

    // Make JobDialog available globally
    window.JobDialog = JobDialog;

})();
