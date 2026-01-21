/**
 * Calendar Core Module
 * 
 * Handles lifecycle and FullCalendar wiring.
 * Registers: initialize, initializeElements, setupCalendar, setupEventListeners, destroy
 */
(function() {
    'use strict';

    GTS.calendar.register('core', function(proto) {
        /**
         * Initialize the job calendar
         */
        proto.initialize = function() {
            this.initializeElements();
            this.setupCalendar();
            this.setupEventListeners();
            // Note: No need to call loadCalendarData() here - FullCalendar automatically
            // fetches events on initial render via the 'events' property
        };

        /**
         * Initialize DOM element references
         */
        proto.initializeElements = function() {
            this.calendarEl = document.getElementById('calendar');
            this.calendarFilter = document.getElementById('calendar-filter');
            this.statusFilter = document.getElementById('status-filter');
            this.searchFilter = document.getElementById('search-filter');
            this.loadingEl = document.getElementById('calendar-loading');
            this.noCalendarsOverlay = document.getElementById('calendar-no-calendars');
        };

        /**
         * Setup FullCalendar instance
         */
        proto.setupCalendar = function() {
            var self = this;

            if (!this.calendarEl || typeof FullCalendar === 'undefined') {
                console.error('JobCalendar: FullCalendar not available');
                return;
            }

            this.calendar = new FullCalendar.Calendar(this.calendarEl, {
                timeZone: 'local',  // Use local timezone to prevent UTC midnight shift
                initialView: 'monthSlidingWeek',
                initialDate: this.getSavedDate() || '2025-09-01',
                headerToolbar: {
                    left: 'prev title next',
                    center: '',
                    right: 'searchButton jobsButton settingsButton todaySidebarButton'
                },
                buttonText: {
                    today: 'Today'
                },
                views: {
                    monthSlidingWeek: {
                        type: 'dayGrid',
                        duration: { weeks: 4 },
                        dateIncrement: { weeks: 1 },
                        dateAlignment: 'week',
                        buttonText: 'Month',
                        fixedWeekCount: false,
                        showNonCurrentDates: true,
                        titleFormat: { month: 'short', day: 'numeric', year: 'numeric' },
                        titleRangeSeparator: ' – ',
                        displayEventEnd: true  // Show end time/date for multi-day events
                    }
                },
                customButtons: {
                    searchButton: {
                        text: '🔍',
                        hint: 'Toggle Search',
                        click: function() {
                            self.toggleSearchPanel();
                        }
                    },
                    jobsButton: {
                        text: 'Jobs',
                        click: function() {
                            window.location.href = GTS.urls.jobList;
                        }
                    },
                    settingsButton: {
                        text: 'Settings',
                        click: function() {
                            window.location.href = GTS.urls.calendarList;
                        }
                    },
                    todaySidebarButton: {
                        text: '📅',
                        hint: 'Toggle Today column',
                        click: function() {
                            self.toggleTodaySidebar();
                        }
                    },
                    calendarFilterButton: {
                        text: 'Calendar',
                        click: function() {
                            // This will be replaced with a dropdown after render
                        }
                    },
                    statusFilterButton: {
                        text: 'Status',
                        click: function() {
                            // This will be replaced with a dropdown after render
                        }
                    }
                },
                height: '100%',        // Fill parent container
                expandRows: true,      // Allow rows to expand to fill space
                windowResizeDelay: 50, // better resizing behavior
                displayEventTime: true,
                eventDisplay: 'block', // Force block display to ensure colors always show (not dot events)
                // Event ordering: sort by start time, then by title for consistent display
                eventOrder: 'start,-duration,allDay,title'
                eventTimeFormat: {
                    hour: 'numeric',
                    minute: '2-digit',
                    meridiem: 'short',
                    omitZeroMinute: false
                },
                events: function(info, successCallback, failureCallback) {
                    self.fetchEvents(info, successCallback, failureCallback);
                },
                eventsSet: function(events) {
                    // Build per-day index for O(1) Today panel lookups
                    self._buildEventDayIndex(events);
                },
                dateClick: function(info) {
                    self.handleDateClick(info);
                },
                eventClick: function(info) {
                    self.handleEventClick(info);
                },
                eventMouseEnter: function(info) {
                    self.handleEventMouseEnter(info);
                },
                eventMouseLeave: function(info) {
                    self.handleEventMouseLeave(info);
                },
                eventDidMount: function(info) {
                    self.handleEventMount(info);
                },
                eventContent: function(info) {
                    return self.renderEventContent(info);
                },
                eventClassNames: function(info) {
                    return self.getEventClassNames(info);
                },
                dayCellContent: function(info) {
                    return self.renderDayCellContent(info);
                },
                // FIXED: Single datesSet handler that does everything needed
                // Previously there was a duplicate key that shadowed handleDatesSet
                datesSet: function(info) {
                    // Update filter state
                    self.handleDatesSet(info);
                    // Save current date for persistence
                    self.saveCurrentDate();
                    // Schedule debounced UI update
                    self.scheduleUIUpdate();
                },
                windowResize: function(view) {
                    self.forceEqualWeekHeights();
                }
            });

            this.calendar.render();

            // Add class for custom views
            this.calendarEl.classList.add('fc-month-view');

            // Custom button styling
            this.styleCustomButtons();

            // Set up day number click handlers (for popover)
            this.setupDayNumberClicks();

            // Initialize date picker controls for Today panel
            this.initializeDatePickerControls();

            // Ensure calendar is visible
            this.ensureCalendarVisible();

            // Force equal week heights after a brief delay
            var heightSelf = this;
            setTimeout(function() {
                heightSelf.forceEqualWeekHeights();
            }, 100);

            // Wire up the "Select All Calendars" button in the no-calendars overlay
            var selectAllBtn = document.getElementById('calendar-select-all-btn');
            if (selectAllBtn) {
                selectAllBtn.addEventListener('click', function() {
                    self.selectAllCalendars();
                });
            }
        };

        /**
         * Setup event listeners for filters
         */
        proto.setupEventListeners = function() {
            if (this.calendarFilter) {
                this.calendarFilter.addEventListener('change', this.handleFilterChange.bind(this));
            }
            if (this.statusFilter) {
                this.statusFilter.addEventListener('change', this.handleFilterChange.bind(this));
            }
            if (this.searchFilter) {
                this.searchFilter.addEventListener('input', this.debounce(this.handleFilterChange.bind(this), 300));
            }

            // Enable scrolling within day cells
            this.enableDayCellScrolling();
        };

        /**
         * Cleanup method for removing event listeners and resetting state
         */
        proto.destroy = function() {
            if (this.calendar) {
                this.calendar.destroy();
            }
        };
    });

})();
