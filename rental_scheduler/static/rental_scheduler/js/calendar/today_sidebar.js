/**
 * Calendar Today Sidebar Module
 * 
 * Handles the Today sidebar panel with event list and date navigation.
 * Registers: toggleTodaySidebar, applyTodaySidebarState, renderTodayPanel,
 *            initializeDatePickerControls, focusEventInCalendar,
 *            startOfDay, endOfDay, isSameDay, formatDateForInput,
 *            eventOverlapsDay, _dateKey, _buildEventDayIndex, _getEventsForDay
 */
(function() {
    'use strict';

    GTS.calendar.register('today_sidebar', function(proto) {
        /**
         * Utility: Get start of day
         */
        proto.startOfDay = function(date) {
            var d = new Date(date);
            d.setHours(0, 0, 0, 0);
            return d;
        };

        /**
         * Format date as YYYY-MM-DD in local timezone (not UTC)
         */
        proto.formatDateForInput = function(date) {
            var year = date.getFullYear();
            var month = String(date.getMonth() + 1).padStart(2, '0');
            var day = String(date.getDate()).padStart(2, '0');
            return year + '-' + month + '-' + day;
        };

        /**
         * Utility: Get end of day
         */
        proto.endOfDay = function(date) {
            var d = new Date(date);
            d.setHours(23, 59, 59, 999);
            return d;
        };

        /**
         * Utility: Check if two dates are the same day
         */
        proto.isSameDay = function(a, b) {
            return a.getFullYear() === b.getFullYear() &&
                a.getMonth() === b.getMonth() &&
                a.getDate() === b.getDate();
        };

        /**
         * Format a date as YYYY-MM-DD key for the event index
         */
        proto._dateKey = function(date) {
            var d = date instanceof Date ? date : new Date(date);
            return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
        };

        /**
         * Build a per-day index of events for O(1) Today panel lookups
         * Called from eventsSet hook
         */
        proto._buildEventDayIndex = function(events) {
            var self = this;
            // Initialize or clear the index
            this._eventsByDay = new Map();

            for (var i = 0; i < events.length; i++) {
                var ev = events[i];
                if (!ev.start) continue;

                var evStart = new Date(ev.start);
                var evEnd = ev.end ? new Date(ev.end) : null;

                // Handle all-day events (exclusive end in FullCalendar)
                if (ev.allDay) {
                    evEnd = evEnd ? new Date(evEnd.getTime() - 1) : new Date(evStart);
                } else {
                    evEnd = evEnd || new Date(evStart);
                }

                // Add event to each day it spans
                var startDate = this.startOfDay(evStart);
                var endDate = this.startOfDay(evEnd);

                var current = new Date(startDate);
                var maxDays = 60; // Safety cap to prevent runaway loops
                var dayCount = 0;

                while (current <= endDate && dayCount < maxDays) {
                    var key = this._dateKey(current);
                    if (!this._eventsByDay.has(key)) {
                        this._eventsByDay.set(key, []);
                    }
                    this._eventsByDay.get(key).push(ev);
                    current.setDate(current.getDate() + 1);
                    dayCount++;
                }
            }
        };

        /**
         * Get events for a specific day from the pre-built index
         * Returns empty array if no events or index not built
         */
        proto._getEventsForDay = function(date) {
            if (!this._eventsByDay) return [];
            var key = this._dateKey(date);
            return this._eventsByDay.get(key) || [];
        };

        /**
         * Check if an event overlaps with a given day using robust exclusive-end logic
         */
        proto.eventOverlapsDay = function(ev, day) {
            var dayStart = this.startOfDay(day);
            var dayEnd = this.endOfDay(day);

            var evStart = ev.start ? new Date(ev.start) : null;
            var evEnd = ev.end ? new Date(ev.end) : null;

            if (!evStart) return false;

            if (ev.allDay) {
                // FullCalendar all-day: end is exclusive; if absent, treat as one day.
                // Convert to inclusive by subtracting 1 ms.
                evEnd = evEnd ? new Date(evEnd.getTime() - 1) : new Date(evStart);
            } else {
                // Timed event without end → point event
                evEnd = evEnd || new Date(evStart);
            }

            // Overlap test: [evStart, evEnd] intersects [dayStart, dayEnd]
            return (evStart <= dayEnd) && (evEnd >= dayStart);
        };

        /**
         * Toggle Today sidebar visibility
         */
        proto.toggleTodaySidebar = function() {
            var self = this;
            this.todaySidebarOpen = !this.todaySidebarOpen;
            this.applyTodaySidebarState();
            localStorage.setItem('gts-calendar-today-sidebar-open', this.todaySidebarOpen);

            setTimeout(function() {
                if (self.calendar) {
                    self.calendar.updateSize();
                    self.forceEqualWeekHeights();
                }
            }, 200);
        };

        /**
         * Apply Today sidebar state to DOM and button
         * @param {boolean} updateButton - whether to update the toggle button state
         */
        proto.applyTodaySidebarState = function(updateButton) {
            if (updateButton === undefined) updateButton = true;
            var todaySidebar = document.getElementById('todaySidebar');
            if (todaySidebar) {
                todaySidebar.classList.toggle('hidden', !this.todaySidebarOpen);
            }

            if (!updateButton) return;

            var todayToggleButton = document.querySelector('.fc-todaySidebarButton-button');
            if (todayToggleButton) {
                todayToggleButton.setAttribute('aria-pressed', this.todaySidebarOpen ? 'true' : 'false');
                todayToggleButton.classList.toggle('active', this.todaySidebarOpen);
                todayToggleButton.title = this.todaySidebarOpen ? 'Hide Today column' : 'Show Today column';
            }
        };

        /**
         * Render the Today panel with events for the selected day
         */
        proto.renderTodayPanel = function(selectedDate) {
            var self = this;
            var listEl = document.getElementById('todayList');
            var labelEl = document.getElementById('todayDateLabel');
            var titleEl = document.getElementById('todayPanelTitle');
            var datePicker = document.getElementById('todayDatePicker');

            if (!listEl || !labelEl || !titleEl) return;

            var targetDate = selectedDate || new Date(); // Use provided date or today
            var today = new Date();
            var isToday = targetDate.toDateString() === today.toDateString();

            // Update title
            titleEl.textContent = isToday ? 'Today' : 'Events';

            // Update date label
            labelEl.textContent = this.calendar.formatDate(targetDate, {
                weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
            });

            // Update date picker value only if it's different
            if (datePicker) {
                // Check if we have a flatpickr instance
                if (this._todayPickerInstance && this._todayPickerInstance.setDate) {
                    var currentSelected = this._todayPickerInstance.selectedDates[0];
                    // Only update if dates are different (avoid infinite loops)
                    if (!currentSelected || !this.isSameDay(currentSelected, targetDate)) {
                        this._todayPickerInstance.setDate(targetDate, false);
                    }
                } else {
                    // Fallback to native input
                    var dateStr = this.formatDateForInput(targetDate);
                    if (datePicker.value !== dateStr) {
                        datePicker.value = dateStr;
                    }
                }
            }

            // OPTIMIZED: Use pre-built per-day index for O(1) lookup instead of filtering all events
            // Fallback to filter if index isn't built yet (e.g., during initial render)
            var events;
            if (this._eventsByDay) {
                events = this._getEventsForDay(targetDate).slice(); // Copy to avoid mutating index
            } else {
                // Fallback: scan all events (only during initial load before eventsSet fires)
                events = this.calendar.getEvents().filter(function(ev) {
                    return self.eventOverlapsDay(ev, targetDate);
                });
            }

            // Sort: all-day first, then by start time
            events.sort(function(a, b) {
                if (a.allDay && !b.allDay) return -1;
                if (!a.allDay && b.allDay) return 1;
                return (a.start ? a.start.getTime() : 0) - (b.start ? b.start.getTime() : 0);
            });

            listEl.innerHTML = '';
            if (!events.length) {
                var emptyText = isToday ? 'No events today.' : 'No events for this day.';
                listEl.innerHTML = '<div class="today-empty">' + emptyText + '</div>';
                return;
            }

            for (var i = 0; i < events.length; i++) {
                var ev = events[i];
                var timeStr = ev.allDay
                    ? 'All day'
                    : this.calendar.formatDate(ev.start, { hour: 'numeric', minute: '2-digit' }) + '–' +
                      this.calendar.formatDate(ev.end || ev.start, { hour: 'numeric', minute: '2-digit' });

                // Get calendar color from extendedProps or use default
                var calendarColor = (ev.extendedProps && ev.extendedProps.calendar_color) || '#3B82F6';

                // Check if job is completed for strikethrough styling and lighter color
                var isCompleted = ev.extendedProps && ev.extendedProps.status === 'completed';
                var textDecoration = isCompleted ? 'text-decoration: line-through;' : '';

                // Apply lighter shade for completed events (same as calendar events)
                var finalColor = calendarColor;
                if (isCompleted) {
                    finalColor = this.lightenColor(calendarColor, 0.3);
                }

                // Use event's backgroundColor if available, otherwise use the calculated color
                var backgroundColor = ev.backgroundColor || finalColor;

                var item = document.createElement('div');
                item.className = 'today-item';
                item.dataset.eventId = ev.id || '';
                item.style.backgroundColor = backgroundColor;
                item.style.borderLeft = '4px solid ' + backgroundColor;
                item.innerHTML = '<div style="' + textDecoration + '"><span class="today-item-time">' + timeStr + '</span>' +
                    '<span class="today-item-title">' + (ev.title || '(no title)') + '</span></div>';

                // Add click handler using a closure to capture the current event
                (function(event) {
                    item.addEventListener('click', function() {
                        self._handleTodayItemClick(event);
                    });
                })(ev);

                // Add hover tooltip for today sidebar items
                (function(event) {
                    item.addEventListener('mouseenter', function(e) {
                        // Clear any existing timeout
                        if (self.tooltipTimeout) {
                            clearTimeout(self.tooltipTimeout);
                        }

                        // Set a 500ms delay before showing the tooltip
                        self.tooltipTimeout = setTimeout(function() {
                            self.showEventTooltip(event, e.target);
                            self.tooltipTimeout = null;
                        }, 500);
                    });

                    item.addEventListener('mouseleave', function() {
                        // Clear the timeout if user stops hovering before delay completes
                        if (self.tooltipTimeout) {
                            clearTimeout(self.tooltipTimeout);
                            self.tooltipTimeout = null;
                        }

                        self.hideEventTooltip();
                    });
                })(ev);

                listEl.appendChild(item);
            }
        };

        /**
         * Handle click on a Today panel item
         * @private
         */
        proto._handleTodayItemClick = function(ev) {
            var self = this;
            var extendedProps = ev.extendedProps || {};
            var jobId = extendedProps.job_id;

            if (jobId && window.JobPanel) {
                // Check if there are unsaved changes
                if (window.JobPanel.hasUnsavedChanges && window.JobPanel.hasUnsavedChanges()) {
                    // Set flag to prevent panel from auto-closing
                    window.JobPanel.isSwitchingJobs = true;
                    // Save the form first
                    window.JobPanel.saveForm(function() {
                        // After saving, add to workspace if it has a job ID
                        var currentJobId = window.JobPanel.currentJobId;
                        if (currentJobId && window.JobWorkspace && !window.JobWorkspace.hasJob(currentJobId)) {
                            // Get job details from the form
                            var form = document.querySelector('#job-panel .panel-body form');
                            var businessName = (form && form.querySelector('input[name="business_name"]') ? form.querySelector('input[name="business_name"]').value : null) ||
                                (form && form.querySelector('input[name="contact_name"]') ? form.querySelector('input[name="contact_name"]').value : null) ||
                                'Unnamed Job';
                            var trailerColor = (form && form.querySelector('input[name="trailer_color"]')) ? form.querySelector('input[name="trailer_color"]').value : '';

                            // Add to workspace as minimized
                            window.JobWorkspace.addJobMinimized(currentJobId, {
                                customerName: businessName,
                                trailerColor: trailerColor,
                                calendarColor: '#3B82F6'
                            });
                        }

                        // Now open the new job
                        self._openJobFromTodayPanel(ev, jobId);

                        // Clear the switching flag after a delay to allow new form to load
                        setTimeout(function() {
                            window.JobPanel.isSwitchingJobs = false;
                        }, 500);
                    });
                } else {
                    // No unsaved changes, open directly
                    self._openJobFromTodayPanel(ev, jobId);
                }
            } else {
                console.error('JobPanel not available or job ID missing for event:', ev.id);
                // Fallback: navigate to the date
                this.calendar.gotoDate(ev.start || new Date());
                // optional: highlight after render
                var evId = ev.id || '';
                setTimeout(function() {
                    var el = self.calendar.el.querySelector('[data-event-id="' + evId + '"]');
                    if (el) {
                        el.classList.add('ring-2');
                        setTimeout(function() {
                            el.classList.remove('ring-2');
                        }, 1200);
                    }
                }, 30);
            }
        };

        /**
         * Open a job from the Today panel
         * @private
         */
        proto._openJobFromTodayPanel = function(ev, jobId) {
            var props = ev.extendedProps || {};
            if (window.JobWorkspace) {
                // Check if the clicked job is already in the workspace
                if (window.JobWorkspace.hasJob(jobId)) {
                    // Job is in workspace, switch to it
                    window.JobWorkspace.switchToJob(jobId);
                } else {
                    // Job is not in workspace, open it fresh
                    window.JobWorkspace.openJob(jobId, {
                        customerName: props.display_name || props.business_name || props.contact_name || ev.title || 'Job',
                        trailerColor: props.trailer_color || '',
                        calendarColor: props.calendar_color || '#3B82F6'
                    });
                }
            } else {
                // Fallback to direct panel opening if workspace not available
                this.openJobInPanel(ev, jobId);
            }
        };

        /**
         * Initialize date picker controls for the Today panel
         */
        proto.initializeDatePickerControls = function() {
            var self = this;
            var prevDayBtn = document.getElementById('prevDayBtn');
            var nextDayBtn = document.getElementById('nextDayBtn');
            var todayBtn = document.getElementById('todayBtn');
            var datePicker = document.getElementById('todayDatePicker');
            var titleBtn = document.getElementById('todayPanelTitle');

            if (!prevDayBtn || !nextDayBtn || !todayBtn || !datePicker || !titleBtn) {
                console.warn('Date picker controls not found');
                return;
            }

            // Helper: get current date from picker (flatpickr instance or input value)
            var getCurrentDate = function() {
                if (self._todayPickerInstance && self._todayPickerInstance.selectedDates.length > 0) {
                    return self._todayPickerInstance.selectedDates[0];
                }
                // Fallback: parse from input value
                var val = datePicker.value;
                if (!val) return new Date();
                if (window.GtsDateInputs && window.GtsDateInputs.parseISOLocal) {
                    var parsed = window.GtsDateInputs.parseISOLocal(val);
                    if (parsed && !isNaN(parsed.getTime())) return parsed;
                }
                // Manual parse fallback
                var parts = val.split('-').map(Number);
                if (parts.length === 3) {
                    return new Date(parts[0], parts[1] - 1, parts[2]);
                }
                return new Date();
            };

            // Helper: set date on picker
            var setPickerDate = function(date) {
                if (self._todayPickerInstance && self._todayPickerInstance.setDate) {
                    self._todayPickerInstance.setDate(date, false);
                } else {
                    datePicker.value = self.formatDateForInput(date);
                }
                self.renderTodayPanel(date);
            };

            // Set initial date to today
            var today = new Date();

            // Initialize with friendly date input when available
            if (window.GtsDateInputs && window.GtsDateInputs.initFriendlyDateInput) {
                this._todayPickerInstance = window.GtsDateInputs.initFriendlyDateInput(datePicker, {
                    enableTime: false,
                    defaultDate: today,
                    onChange: function(selectedDates, dateStr, instance) {
                        var d = selectedDates && selectedDates[0];
                        if (d && !isNaN(d.getTime())) {
                            self.renderTodayPanel(d);
                        }
                    }
                });
            } else {
                // Fallback: use native date input
                datePicker.value = this.formatDateForInput(today);
                datePicker.addEventListener('change', function() {
                    var date = getCurrentDate();
                    self.renderTodayPanel(date);
                });
            }

            // Initial render with today's date
            this.renderTodayPanel(today);

            // Previous day button
            prevDayBtn.addEventListener('click', function() {
                var currentDate = getCurrentDate();
                currentDate.setDate(currentDate.getDate() - 1);
                setPickerDate(currentDate);
            });

            // Next day button
            nextDayBtn.addEventListener('click', function() {
                var currentDate = getCurrentDate();
                currentDate.setDate(currentDate.getDate() + 1);
                setPickerDate(currentDate);
            });

            // Today button
            todayBtn.addEventListener('click', function() {
                var today = new Date();
                setPickerDate(today);
            });

            // Title button click - go to today
            titleBtn.addEventListener('click', function() {
                var today = new Date();
                setPickerDate(today);
            });
        };

        /**
         * Focus an event in the calendar by jumping to its date
         */
        proto.focusEventInCalendar = function(ev) {
            // Jump to the event's start week inside our sliding 4-week view
            this.calendar.gotoDate(ev.start || new Date());

            // Save the new position
            this.saveCurrentDate();
        };
    });

})();
