/**
 * Calendar Day Interactions Module
 * 
 * Handles day cell clicks, double-clicks, and event popovers.
 * Registers: setupDayNumberClicks, showDayEventsPopover, openCreateFormForDate, handleDateClick
 */
(function() {
    'use strict';

    GTS.calendar.register('day_interactions', function(proto) {
        /**
         * Setup click handlers for day numbers to show event list popover
         */
        proto.setupDayNumberClicks = function() {
            var self = this;

            // Add CSS to make day numbers look clickable
            var style = document.createElement('style');
            style.textContent = 
                '.fc-daygrid-day-number {' +
                    'cursor: pointer !important;' +
                    'padding: 2px 6px;' +
                    'border-radius: 4px;' +
                    'transition: background-color 0.2s;' +
                '}' +
                '.fc-daygrid-day-number:hover {' +
                    'background-color: #e5e7eb !important;' +
                '}';
            document.head.appendChild(style);

            // Handle single clicks on day numbers - show popover with events
            this.calendarEl.addEventListener('click', function(e) {
                // Check if clicked element is a day number
                var dayNumber = e.target.closest('.fc-daygrid-day-number');
                if (!dayNumber) return;

                // Prevent default browser navigation (day number is an anchor)
                e.preventDefault();

                // Get the day cell
                var dayCell = dayNumber.closest('.fc-daygrid-day');
                if (!dayCell) return;

                // Get the date from the day cell's data attribute
                var dateStr = dayCell.getAttribute('data-date');
                if (!dateStr) return;

                // Clear any existing timer
                if (self.dayNumberClickTimer) {
                    clearTimeout(self.dayNumberClickTimer);
                }

                // Set timer to show popover after threshold + 150ms (allows time for double-click)
                self.dayNumberClickTimer = setTimeout(function() {
                    // Get all events for this date
                    var events = self.calendar.getEvents().filter(function(event) {
                        // Get date in YYYY-MM-DD format without timezone conversion
                        var getLocalDateStr = function(d) {
                            var year = d.getFullYear();
                            var month = String(d.getMonth() + 1).padStart(2, '0');
                            var day = String(d.getDate()).padStart(2, '0');
                            return year + '-' + month + '-' + day;
                        };

                        var eventStartDate = getLocalDateStr(event.start);
                        var clickedDate = dateStr; // Already in YYYY-MM-DD format

                        // Check if event starts on this day
                        return eventStartDate === clickedDate;
                    });

                    // If there are events, show the popover
                    if (events.length > 0) {
                        // Parse the date for popover
                        var date = new Date(dateStr + 'T00:00:00');
                        self.showDayEventsPopover(events, dayNumber, date);
                    }
                }, self.doubleClickThreshold + 150);
            });

            // Handle double-clicks anywhere in a day cell - open new job/reminder form
            this.calendarEl.addEventListener('dblclick', function(e) {
                // Ignore double-clicks on events themselves (let event click handlers handle those)
                if (e.target.closest('.fc-event')) {
                    return;
                }

                // Find the day cell that was double-clicked
                var dayCell = e.target.closest('.fc-daygrid-day');
                if (!dayCell) return;

                // Prevent default navigation
                e.preventDefault();

                // Cancel the single-click timer
                if (self.dayNumberClickTimer) {
                    clearTimeout(self.dayNumberClickTimer);
                    self.dayNumberClickTimer = null;
                }

                // Get the date from the day cell's data attribute
                var dateStr = dayCell.getAttribute('data-date');
                if (!dateStr) return;

                // Parse the date
                var date = new Date(dateStr + 'T00:00:00');
                var now = Date.now();
                var dateMs = date.getTime();

                // If this double-click was already handled via dateClick logic, skip duplicate load
                if (self.lastOpenedDateByDoubleClick === dateMs && (now - self.lastOpenedDateTimestamp) < (self.doubleClickThreshold + 150)) {
                    return;
                }

                // Record this handled double click
                self.lastOpenedDateByDoubleClick = dateMs;
                self.lastOpenedDateTimestamp = now;

                // Open the appropriate form
                self.openCreateFormForDate(date);
            });
        };

        /**
         * Open the create job or call reminder form for the provided date
         */
        proto.openCreateFormForDate = function(date) {
            var self = this;
            try {
                if (!window.JobPanel) {
                    console.error('JobPanel not available');
                    this.showError('Job panel functionality not available. Please refresh the page.');
                    return;
                }

                var isSunday = date.getDay() === 0;
                var yyyy = date.getFullYear();
                var mm = String(date.getMonth() + 1).padStart(2, '0');
                var dd = String(date.getDate()).padStart(2, '0');
                var dateStr = yyyy + '-' + mm + '-' + dd;

                var loadForm = function() {
                    // Close any open day popovers before loading the form
                    document.querySelectorAll('.fc-more-popover').forEach(function(pop) {
                        pop.remove();
                    });

                    if (isSunday) {
                        var url = '/call-reminders/new/partial/?date=' + dateStr;
                        if (self.defaultCalendar) {
                            url += '&calendar=' + self.defaultCalendar;
                        }
                        window.JobPanel.setTitle('New Call Reminder');
                        window.JobPanel.load(url);
                    } else {
                        var url = '/jobs/new/partial/?date=' + dateStr;
                        if (self.defaultCalendar) {
                            url += '&calendar=' + self.defaultCalendar;
                        }
                        window.JobPanel.setTitle('New Job');
                        window.JobPanel.load(url);
                    }
                };

                if (window.JobPanel.hasUnsavedChanges && window.JobPanel.hasUnsavedChanges()) {
                    window.JobPanel.saveForm(function() {
                        var currentJobId = window.JobPanel.currentJobId;
                        if (currentJobId && window.JobWorkspace && !window.JobWorkspace.hasJob(currentJobId)) {
                            var form = document.querySelector('#job-panel .panel-body form');
                            var businessNameEl = form ? form.querySelector('input[name="business_name"]') : null;
                            var contactNameEl = form ? form.querySelector('input[name="contact_name"]') : null;
                            var trailerColorEl = form ? form.querySelector('input[name="trailer_color"]') : null;
                            var businessName = (businessNameEl && businessNameEl.value) || (contactNameEl && contactNameEl.value) || 'Unnamed Job';
                            var trailerColor = (trailerColorEl && trailerColorEl.value) || '';

                            window.JobWorkspace.addJobMinimized(currentJobId, {
                                customerName: businessName,
                                trailerColor: trailerColor,
                                calendarColor: '#3B82F6'
                            });
                        }
                        loadForm();
                    });
                } else {
                    loadForm();
                }
            } catch (error) {
                console.error('JobCalendar: Error opening form for date', error);
                this.showError('Unable to open form. Please try again.');
            }
        };

        /**
         * Show a popover with all events for a specific day
         */
        proto.showDayEventsPopover = function(events, anchorEl, date) {
            var self = this;

            // Create popover element
            var popover = document.createElement('div');
            popover.className = 'fc-popover fc-more-popover';
            popover.style.cssText = 
                'position: absolute;' +
                'z-index: 10000;' +
                'background: white;' +
                'border: 1px solid #ddd;' +
                'border-radius: 4px;' +
                'box-shadow: 0 2px 8px rgba(0,0,0,0.15);' +
                'min-width: 300px;' +
                'max-width: 400px;';

            // Format date for header
            var dateStr = this.calendar.formatDate(date, { weekday: 'long', month: 'long', day: 'numeric' });

            // Build popover content
            var headerHtml = '<div class="fc-popover-header" style="padding: 8px 12px; background: #f8f9fa; border-bottom: 1px solid #ddd; border-radius: 4px 4px 0 0; display: flex; justify-content: space-between; align-items: center;">' +
                '<span class="fc-popover-title" style="font-weight: 600;">' + dateStr + '</span>' +
                '<button class="fc-popover-close" style="background: none; border: none; cursor: pointer; font-size: 18px; color: #666; padding: 0 4px;" title="Close">×</button>' +
                '</div>';

            var bodyHtml = '<div class="fc-popover-body" style="padding: 8px;">';

            // Sort events: all-day first, then by start time
            events.sort(function(a, b) {
                if (a.allDay && !b.allDay) return -1;
                if (!a.allDay && b.allDay) return 1;
                var aTime = a.start ? a.start.getTime() : 0;
                var bTime = b.start ? b.start.getTime() : 0;
                return aTime - bTime;
            });

            events.forEach(function(event) {
                var props = event.extendedProps || {};
                var bgColor = event.backgroundColor || props.calendar_color || '#3B82F6';
                var isCompleted = props.status === 'completed';
                var textStyle = isCompleted ? 'text-decoration: line-through; opacity: 0.7;' : '';

                // Format time
                var timeStr = event.allDay ? 'All day' : self.calendar.formatDate(event.start, { hour: 'numeric', minute: '2-digit' });

                bodyHtml += '<div class="fc-popover-event" style="' +
                    'padding: 6px 8px; ' +
                    'margin-bottom: 4px; ' +
                    'background-color: ' + bgColor + '; ' +
                    'color: white; ' +
                    'border-radius: 4px; ' +
                    'cursor: pointer; ' +
                    textStyle +
                    '" data-event-id="' + (event.id || '') + '">' +
                    '<div style="font-size: 11px; opacity: 0.9;">' + timeStr + '</div>' +
                    '<div style="font-weight: 500;">' + (event.title || '(no title)') + '</div>' +
                    '</div>';
            });

            bodyHtml += '</div>';

            popover.innerHTML = headerHtml + bodyHtml;

            // Add to document
            document.body.appendChild(popover);

            // Position popover near the anchor
            var rect = anchorEl.getBoundingClientRect();
            var popoverRect = popover.getBoundingClientRect();

            var left = rect.left + window.scrollX;
            var top = rect.bottom + window.scrollY + 4;

            // Adjust if goes off screen
            if (left + popoverRect.width > window.innerWidth) {
                left = window.innerWidth - popoverRect.width - 8;
            }
            if (top + popoverRect.height > window.innerHeight + window.scrollY) {
                top = rect.top + window.scrollY - popoverRect.height - 4;
            }

            popover.style.left = left + 'px';
            popover.style.top = top + 'px';

            // Close button handler
            popover.querySelector('.fc-popover-close').addEventListener('click', function() {
                popover.remove();
            });

            // Event click handlers
            popover.querySelectorAll('.fc-popover-event').forEach(function(eventEl) {
                eventEl.addEventListener('click', function() {
                    var eventId = eventEl.getAttribute('data-event-id');
                    if (eventId) {
                        var calEvent = self.calendar.getEventById(eventId);
                        if (calEvent) {
                            self.handleEventClick({ event: calEvent });
                        }
                    }
                    popover.remove();
                });
            });

            // Close on outside click
            var outsideClickHandler = function(e) {
                if (!popover.contains(e.target)) {
                    popover.remove();
                    document.removeEventListener('click', outsideClickHandler);
                }
            };
            setTimeout(function() {
                document.addEventListener('click', outsideClickHandler);
            }, 0);
        };

        /**
         * Handle date click with proper double-click detection
         */
        proto.handleDateClick = function(info) {
            var self = this;
            try {
                // Check if click is on or near a scrollbar (only if scrollbar is present)
                if (info.jsEvent) {
                    var dayEventsContainer = info.jsEvent.target.closest('.fc-daygrid-day-events');
                    if (dayEventsContainer) {
                        // Only check for scrollbar clicks if there's actually a scrollbar
                        var hasScrollbar = dayEventsContainer.scrollHeight > dayEventsContainer.clientHeight;

                        if (hasScrollbar) {
                            var rect = dayEventsContainer.getBoundingClientRect();
                            var clickX = info.jsEvent.clientX;
                            var rightEdge = rect.right;
                            var isScrollbarClick = (rightEdge - clickX) <= 18;

                            if (isScrollbarClick) {
                                // Click is on scrollbar - ignore it
                                return;
                            }
                        }
                    }
                }

                var currentTime = Date.now();
                var currentDate = info.date.getTime();

                // Check if this is a double-click (same date within threshold)
                if (this.lastClickDate === currentDate &&
                    this.lastClickTime &&
                    (currentTime - this.lastClickTime) < this.doubleClickThreshold) {

                    // Double click detected - clear timer
                    if (this.clickTimer) {
                        clearTimeout(this.clickTimer);
                        this.clickTimer = null;
                    }

                    // Record handled double click
                    var dateStr = (info.dateStr || '').substring(0, 10);
                    var dateForForm = dateStr ? new Date(dateStr + 'T00:00:00') : info.date;
                    var dateMs = dateForForm.getTime();
                    this.lastOpenedDateByDoubleClick = dateMs;
                    this.lastOpenedDateTimestamp = currentTime;

                    // Open the appropriate form
                    this.openCreateFormForDate(dateForForm);

                    // Reset tracking
                    this.lastClickDate = null;
                    this.lastClickTime = null;

                } else {
                    // First click or too much time has passed - set up for potential double-click
                    this.lastClickDate = currentDate;
                    this.lastClickTime = currentTime;

                    // Clear any existing timer
                    if (this.clickTimer) {
                        clearTimeout(this.clickTimer);
                    }

                    // Set timer to reset after threshold if no second click
                    this.clickTimer = setTimeout(function() {
                        self.lastClickDate = null;
                        self.lastClickTime = null;
                        self.clickTimer = null;
                    }, this.doubleClickThreshold);
                }

            } catch (error) {
                console.error('JobCalendar: Error handling date click', error);
                this.showError('Unable to create new job. Please try again.');
            }
        };
    });

})();
