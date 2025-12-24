/**
 * Calendar Tooltips Module
 * 
 * Handles event tooltips with hover delay.
 * Registers: showEventTooltip, hideEventTooltip, showJobRowTooltip,
 *            handleEventMouseEnter, handleEventMouseLeave
 */
(function() {
    'use strict';

    GTS.calendar.register('tooltips', function(proto) {
        /**
         * Show event tooltip for any event
         */
        proto.showEventTooltip = function(event, targetElement) {
            var self = this;
            var props = event.extendedProps || {};

            // Create tooltip if it doesn't exist
            var tooltip = document.getElementById('event-tooltip');
            if (!tooltip) {
                tooltip = document.createElement('div');
                tooltip.id = 'event-tooltip';
                tooltip.style.cssText = 
                    'position: fixed;' +
                    'z-index: 10000;' +
                    'background: white;' +
                    'border: 1px solid #d1d5db;' +
                    'border-radius: 8px;' +
                    'box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);' +
                    'padding: 12px;' +
                    'min-width: 250px;' +
                    'max-width: 350px;' +
                    'font-size: 13px;' +
                    'pointer-events: none;' +
                    'display: none;';
                document.body.appendChild(tooltip);
            }

            // Format dates
            var formatDate = function(date) {
                if (!date) return 'N/A';
                return self.calendar.formatDate(date, {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                    hour: event.allDay ? undefined : 'numeric',
                    minute: event.allDay ? undefined : '2-digit',
                    meridiem: event.allDay ? undefined : 'short'
                });
            };

            // For multi-day events, use the full job date range instead of the split day
            var startDate, endDate;
            if (props.is_multi_day && props.job_start_date && props.job_end_date) {
                // Use the full job date range
                var jobStartDate = new Date(props.job_start_date + 'T12:00:00');
                var jobEndDate = new Date(props.job_end_date + 'T12:00:00');
                startDate = formatDate(jobStartDate);
                endDate = formatDate(jobEndDate);
            } else {
                // Use the event's own dates
                startDate = formatDate(event.start);
                endDate = formatDate(event.end || event.start);
            }

            // Build tooltip content
            var content = '<div style="border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-bottom: 8px;">' +
                '<div style="font-weight: 600; font-size: 14px; color: #111827; margin-bottom: 4px;">' +
                    (event.title || '(No Title)') +
                '</div>' +
                '<div style="font-size: 11px; color: #6b7280;">' +
                    (props.calendar_name || 'Calendar') +
                '</div>' +
                '</div>' +
                '<div style="display: flex; flex-direction: column; gap: 6px;">';

            // Date/Time
            if (event.allDay || (props.is_multi_day && props.job_start_date)) {
                var isSingleDay = startDate === endDate;
                var dateRange = isSingleDay ? startDate : startDate + ' - ' + endDate;

                content += '<div style="display: flex; align-items: start;">' +
                    '<svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">' +
                        '<path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"></path>' +
                    '</svg>' +
                    '<div style="flex: 1;">' +
                        '<div style="color: #374151; font-weight: 500;">All Day</div>' +
                        '<div style="color: #6b7280; font-size: 12px;">' + dateRange + '</div>' +
                    '</div></div>';
            } else {
                content += '<div style="display: flex; align-items: start;">' +
                    '<svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">' +
                        '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path>' +
                    '</svg>' +
                    '<div style="flex: 1;">' +
                        '<div style="color: #374151; font-weight: 500;">' + startDate + '</div>' +
                        (endDate !== startDate ? '<div style="color: #6b7280; font-size: 12px;">to ' + endDate + '</div>' : '') +
                    '</div></div>';
            }

            // Business/Contact
            if (props.business_name) {
                content += '<div style="display: flex; align-items: start;">' +
                    '<svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">' +
                        '<path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>' +
                    '</svg>' +
                    '<div style="flex: 1; color: #374151;">' +
                        props.business_name +
                        (props.contact_name ? '<div style="color: #6b7280; font-size: 12px;">' + props.contact_name + '</div>' : '') +
                    '</div></div>';
            }

            // Phone
            if (props.phone) {
                content += '<div style="display: flex; align-items: start;">' +
                    '<svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">' +
                        '<path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"></path>' +
                    '</svg>' +
                    '<div style="flex: 1; color: #374151;">' + props.phone + '</div></div>';
            }

            // Trailer Information
            if (props.trailer_details || props.trailer_color || props.trailer_serial) {
                content += '<div style="display: flex; align-items: start;">' +
                    '<svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">' +
                        '<path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"></path>' +
                        '<path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1V8a1 1 0 00-1-1h-3z"></path>' +
                    '</svg>' +
                    '<div style="flex: 1; color: #374151;">' +
                        (props.trailer_details ? '<div style="font-weight: 500;">Trailer: ' + (props.trailer_details.length > 80 ? props.trailer_details.substring(0, 80) + '...' : props.trailer_details) + '</div>' : '') +
                        (props.trailer_color ? '<div style="color: #6b7280; font-size: 12px; margin-top: 2px;">Color: ' + props.trailer_color + '</div>' : '') +
                        (props.trailer_serial ? '<div style="color: #6b7280; font-size: 12px; margin-top: 2px;">Serial: ' + props.trailer_serial + '</div>' : '') +
                    '</div></div>';
            }

            // Status
            if (props.status) {
                var statusColors = {
                    'pending': '#fbbf24',
                    'confirmed': '#3b82f6',
                    'in_progress': '#f97316',
                    'completed': '#10b981',
                    'cancelled': '#ef4444',
                    'uncompleted': '#6b7280'
                };
                var statusColor = statusColors[props.status] || '#6b7280';
                var statusText = props.status.replace('_', ' ').replace(/\b\w/g, function(l) { return l.toUpperCase(); });

                content += '<div style="display: flex; align-items: start;">' +
                    '<svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">' +
                        '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>' +
                    '</svg>' +
                    '<div style="flex: 1;">' +
                        '<span style="display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; background-color: ' + statusColor + '20; color: ' + statusColor + ';">' +
                            statusText +
                        '</span>' +
                    '</div></div>';
            }

            // Recurring indicator
            if (props.is_recurring_parent || props.is_recurring_instance) {
                content += '<div style="display: flex; align-items: start;">' +
                    '<svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">' +
                        '<path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"></path>' +
                    '</svg>' +
                    '<div style="flex: 1; color: #6b7280; font-size: 12px;">Recurring Event</div></div>';
            }

            content += '</div>';

            tooltip.innerHTML = content;
            tooltip.style.display = 'block';

            // Position tooltip near the event
            var rect = targetElement.getBoundingClientRect();
            var tooltipRect = tooltip.getBoundingClientRect();

            var margin = 10;
            var viewportWidth = window.innerWidth;
            var viewportHeight = window.innerHeight;

            var left = rect.right + margin;
            var top = rect.top;

            // Adjust horizontal position if tooltip goes off right edge
            if (left + tooltipRect.width > viewportWidth - margin) {
                left = rect.left - tooltipRect.width - margin;
                if (left < margin) {
                    left = margin;
                }
            }

            // Ensure tooltip doesn't go off edges
            if (left < margin) left = margin;
            if (left + tooltipRect.width > viewportWidth - margin) {
                left = viewportWidth - tooltipRect.width - margin;
            }
            if (top + tooltipRect.height > viewportHeight - margin) {
                top = viewportHeight - tooltipRect.height - margin;
            }
            if (top < margin) top = margin;

            tooltip.style.left = left + 'px';
            tooltip.style.top = top + 'px';
        };

        /**
         * Hide event tooltip
         */
        proto.hideEventTooltip = function() {
            var tooltip = document.getElementById('event-tooltip');
            if (tooltip) {
                tooltip.style.display = 'none';
            }
        };

        /**
         * Show tooltip for a job row in the search results table.
         * Fetches job details from the API and reuses the calendar tooltip renderer.
         */
        proto.showJobRowTooltip = function(rowElement) {
            var self = this;
            var jobId = rowElement && rowElement.getAttribute ? rowElement.getAttribute('data-job-id') : null;
            if (!jobId) return;

            fetch(GTS.urls.jobDetailApi(jobId))
                .then(function(response) {
                    if (!response.ok) return null;
                    return response.json();
                })
                .then(function(jobData) {
                    if (!jobData) return;

                    var fakeEvent = {
                        title: jobData.display_name || jobData.business_name || '(No Title)',
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

                    self.showEventTooltip(fakeEvent, rowElement);
                })
                .catch(function(error) {
                    console.error('Error showing job row tooltip:', error);
                });
        };

        /**
         * Handle event mouse enter for tooltip
         */
        proto.handleEventMouseEnter = function(info) {
            var self = this;
            // Clear any existing timeout
            if (this.tooltipTimeout) {
                clearTimeout(this.tooltipTimeout);
            }

            // Set a 500ms delay before showing the tooltip
            this.tooltipTimeout = setTimeout(function() {
                self.showEventTooltip(info.event, info.el);
                self.tooltipTimeout = null;
            }, 500);
        };

        /**
         * Handle event mouse leave to hide tooltip
         */
        proto.handleEventMouseLeave = function(info) {
            // Clear the timeout if user stops hovering before delay completes
            if (this.tooltipTimeout) {
                clearTimeout(this.tooltipTimeout);
                this.tooltipTimeout = null;
            }

            // Hide the tooltip if it's already showing
            this.hideEventTooltip();
        };
    });

})();
