/**
 * Calendar Rendering Module
 * 
 * Handles event rendering and styling for FullCalendar events.
 * Registers: handleEventMount, lightenColor, getEventClassNames,
 *            renderEventContent, renderDayCellContent
 */
(function() {
    'use strict';

    GTS.calendar.register('rendering', function(proto) {
        /**
         * Handle event mount for styling
         * OPTIMIZED: Server already provides backgroundColor/borderColor in event data.
         * We only add CSS classes here - no setProp() calls or per-event timers.
         */
        proto.handleEventMount = function(info) {
            var el = info.el;
            if (!el) return;

            var props = info.event.extendedProps;
            if (!props) return;

            // Apply completion styling via CSS class (styles defined in job_calendar.css)
            var isCompleted = props.status === 'completed' || props.is_completed ||
                (props.completed && (props.type === 'call_reminder' || props.type === 'standalone_call_reminder'));

            if (isCompleted) {
                el.classList.add('job-completed');
            }

            // Apply canceled styling via CSS class
            if (props.is_canceled) {
                el.classList.add('job-canceled');
            }

            // Add data attributes for E2E test selectors (non-functional)
            if (props.type) {
                el.setAttribute('data-gts-event-type', props.type);
            }
            if (props.job_id) {
                el.setAttribute('data-gts-job-id', props.job_id);
            }
            if (props.reminder_id) {
                el.setAttribute('data-gts-reminder-id', props.reminder_id);
            }
            if (props.recurrence_parent_id) {
                el.setAttribute('data-gts-recurrence-parent-id', props.recurrence_parent_id);
                // Also add the original start date for identifying specific occurrences
                var originalStartISO = props.recurrence_original_start;
                if (originalStartISO) {
                    el.setAttribute('data-gts-recurrence-original-start', originalStartISO.substring(0, 10));
                }
            }
        };

        /**
         * Lighten a hex color by a given factor (0-1)
         */
        proto.lightenColor = function(hexColor, factor) {
            // Remove # if present
            hexColor = hexColor.replace('#', '');

            // Convert to RGB
            var r = parseInt(hexColor.substr(0, 2), 16);
            var g = parseInt(hexColor.substr(2, 2), 16);
            var b = parseInt(hexColor.substr(4, 2), 16);

            // Lighten by mixing with white
            var newR = Math.round(r + (255 - r) * factor);
            var newG = Math.round(g + (255 - g) * factor);
            var newB = Math.round(b + (255 - b) * factor);

            // Convert back to hex
            return '#' + newR.toString(16).padStart(2, '0') + newG.toString(16).padStart(2, '0') + newB.toString(16).padStart(2, '0');
        };

        /**
         * Get event class names for styling
         */
        proto.getEventClassNames = function(info) {
            var classes = ['job-event'];
            var props = info.event.extendedProps;

            if (props.is_completed) {
                classes.push('job-completed');
            }
            if (props.is_canceled) {
                classes.push('job-canceled');
            }

            return classes;
        };

        /**
         * Render custom event content
         */
        proto.renderEventContent = function(info) {
            var event = info.event;
            var props = event.extendedProps;

            // Add strikethrough styling for completed jobs
            var isCompleted = props.status === 'completed';
            var titleClass = isCompleted ? 'job-title job-title-completed' : 'job-title';

            // Add recurring event icon
            var recurringIcon = (props.is_recurring_parent || props.is_recurring_instance)
                ? '<svg style="width: 12px; height: 12px; display: inline-block; margin-right: 4px; vertical-align: middle;" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"></path></svg>'
                : '';

            // Add multi-day indicator
            var multiDayIndicator = '';
            if (props.is_multi_day) {
                var dayNumber = props.multi_day_number + 1;  // Convert 0-indexed to 1-indexed
                var totalDays = props.multi_day_total + 1;   // Convert count to 1-indexed total
                multiDayIndicator = ' <span style="font-size: 0.85em; opacity: 0.8;">(Day ' + dayNumber + '/' + totalDays + ')</span>';
            }

            return {
                html: '<div class="job-event-content">' +
                    '<div class="' + titleClass + '">' + recurringIcon + event.title + multiDayIndicator + '</div>' +
                    '</div>'
            };
        };

        /**
         * Render custom day cell content with month name for first 7 days
         */
        proto.renderDayCellContent = function(info) {
            var dayOfMonth = info.date.getDate();

            // Only show month name for first 7 days of the month
            if (dayOfMonth >= 1 && dayOfMonth <= 7) {
                var monthName = info.date.toLocaleDateString('en-US', { month: 'short' });

                return {
                    html: '<div class="fc-daygrid-day-top">' +
                        '<a class="fc-daygrid-day-number">' + dayOfMonth + '</a>' +
                        '</div>' +
                        '<div class="fc-month-name-wrapper">' +
                        '<span class="fc-month-name">' + monthName + '</span>' +
                        '</div>'
                };
            }

            // Default rendering for other days
            return {
                html: '<div class="fc-daygrid-day-top">' +
                    '<a class="fc-daygrid-day-number">' + dayOfMonth + '</a>' +
                    '</div>'
            };
        };
    });

})();
