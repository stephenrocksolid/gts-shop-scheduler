/**
 * Job Calendar - Manages job calendar display with HTMX integration
 * Handles calendar rendering, filtering, and job status updates
 * VERSION: 2.0 - Calendar Color Coding Update
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

            // Click tracking for double-click detection
            this.clickTimer = null;
            this.lastClickDate = null;
            this.lastClickTime = null;

            // Day number click timer for popover delay
            this.dayNumberClickTimer = null;

            // Double-click detection threshold (ms)
            this.doubleClickThreshold = 650;

            // Track last opened date when creating new items to prevent duplicate loads
            this.lastOpenedDateByDoubleClick = null;
            this.lastOpenedDateTimestamp = 0;

            // Tooltip hover delay tracking
            this.tooltipTimeout = null;

            // Debounced refetch tracking - prevents rapid successive refetches
            this.refetchDebounceTimer = null;
            this.refetchDebounceMs = 150; // Debounce refetch calls within this window

            // Search panel state - load from localStorage
            const savedSearchPanelState = localStorage.getItem('gts-calendar-search-open');
            this.searchPanelOpen = savedSearchPanelState === 'true';

            // Today sidebar state - default to open if not stored
            const savedTodaySidebarState = localStorage.getItem('gts-calendar-today-sidebar-open');
            this.todaySidebarOpen = savedTodaySidebarState === null ? true : savedTodaySidebarState === 'true';
            this.applyTodaySidebarState(false);

            // Initialize search panel state on page load
            if (this.searchPanelOpen) {
                setTimeout(() => {
                    const searchPanel = document.getElementById('calendar-search-panel');
                    const calendarShell = document.getElementById('calendar-shell');
                    const searchInput = document.getElementById('calendar-search-input');
                    const searchButton = document.querySelector('.fc-searchButton-button');

                    if (searchPanel && calendarShell) {
                        searchPanel.style.height = '50vh';
                        calendarShell.style.height = 'calc(50vh - 45px)';

                        // Add active class to button
                        if (searchButton) {
                            searchButton.classList.add('active');
                        }

                        // Focus search input if panel is open
                        if (searchInput) {
                            searchInput.focus();
                        }
                    }
                }, 0);
            }

            // State management
            this.currentFilters = {
                calendar: '',
                status: '',
                search: '',
                month: new Date().getMonth() + 1,
                year: new Date().getFullYear()
            };

            // Load saved filters from localStorage
            this.loadSavedFilters();

            // Initialize selected calendars BEFORE calendar is set up
            this.initializeSelectedCalendars();

            this.initialize();
        }

        /**
         * Initialize the job calendar
         */
        initialize() {
            this.initializeElements();
            this.setupCalendar();
            this.setupEventListeners();
            // Note: No need to call loadCalendarData() here - FullCalendar automatically
            // fetches events on initial render via the 'events' property
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
                        click: () => {
                            this.toggleSearchPanel();
                        }
                    },
                    jobsButton: {
                        text: 'Jobs',
                        click: function () {
                            window.location.href = '/jobs/';
                        }
                    },
                    settingsButton: {
                        text: 'Settings',
                        click: function () {
                            window.location.href = '/calendars/';
                        }
                    },
                    todaySidebarButton: {
                        text: '📅',
                        hint: 'Toggle Today column',
                        click: () => {
                            this.toggleTodaySidebar();
                        }
                    },
                    calendarFilterButton: {
                        text: 'Calendar',
                        click: function () {
                            // This will be replaced with a dropdown after render
                        }
                    },
                    statusFilterButton: {
                        text: 'Status',
                        click: function () {
                            // This will be replaced with a dropdown after render
                        }
                    }
                },
                height: '100%',        // Fill parent container
                expandRows: true,      // Allow rows to expand to fill space
                windowResizeDelay: 50, // better resizing behavior
                events: this.fetchEvents.bind(this),
                dateClick: this.handleDateClick.bind(this),
                eventClick: this.handleEventClick.bind(this),
                eventDidMount: this.handleEventMount.bind(this),
                datesSet: this.handleDatesSet.bind(this),
                eventTimeFormat: {
                    hour: 'numeric',
                    minute: '2-digit',
                    meridiem: 'short'
                },
                dayMaxEvents: false,  // Show all events, enable scrolling in day cells
                moreLinkClick: 'popover',
                eventDisplay: 'block',
                nextDayThreshold: '00:00:00',  // Events that end at midnight or later span to next day
                eventClassNames: this.getEventClassNames.bind(this),
                eventContent: this.renderEventContent.bind(this),
                dayCellContent: this.renderDayCellContent.bind(this),
                // Hook calendar events to update Today panel and save position
                eventsSet: () => {
                    this.renderTodayPanel();
                    this.forceEqualWeekHeights();
                },
                datesSet: () => {
                    this.renderTodayPanel();
                    this.saveCurrentDate();
                    this.forceEqualWeekHeights();
                },
                loading: (isLoading) => {
                    if (!isLoading) {
                        this.renderTodayPanel();
                    }
                },
                eventAdd: () => this.renderTodayPanel(),
                eventChange: () => this.renderTodayPanel(),
                eventRemove: () => this.renderTodayPanel(),
                eventMouseEnter: this.handleEventMouseEnter.bind(this),
                eventMouseLeave: this.handleEventMouseLeave.bind(this)
            });

            this.calendar.render();

            // Force equal week heights after render
            this.forceEqualWeekHeights();

            // Style the custom buttons after render
            this.styleCustomButtons();

            // Apply Today sidebar state (button exists after render)
            setTimeout(() => {
                this.applyTodaySidebarState();
            }, 0);

            // Ensure calendar content is visible
            setTimeout(() => {
                this.ensureCalendarVisible();
            }, 100);

            // Initial render will happen after events are loaded via eventsSet/loading hooks

            // Hook Today button to update Today panel and save position
            const todayBtn = document.querySelector('.fc-today-button');
            if (todayBtn) {
                todayBtn.addEventListener('click', () => {
                    setTimeout(() => {
                        this.renderTodayPanel();
                        this.saveCurrentDate();
                    }, 100);
                });
            }

            // Initialize date picker controls
            this.initializeDatePickerControls();

            // Setup day number clicks to show event list
            this.setupDayNumberClicks();

            // Make calendar instance globally available
            window.jobCalendar = this;

            // Add window resize listener to maintain equal heights
            let resizeTimeout;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(() => {
                    this.forceEqualWeekHeights();
                }, 150);
            });
        }

        /**
         * Setup click handlers for day numbers to show event list popover
         */
        setupDayNumberClicks() {
            // Add CSS to make day numbers look clickable
            const style = document.createElement('style');
            style.textContent = `
                .fc-daygrid-day-number {
                    cursor: pointer !important;
                    padding: 2px 6px;
                    border-radius: 4px;
                    transition: background-color 0.2s;
                }
                .fc-daygrid-day-number:hover {
                    background-color: #e5e7eb !important;
                }
            `;
            document.head.appendChild(style);

            // Handle single clicks on day numbers - show popover with events
            this.calendarEl.addEventListener('click', (e) => {
                // Check if clicked element is a day number
                const dayNumber = e.target.closest('.fc-daygrid-day-number');
                if (!dayNumber) return;

                // Prevent default browser navigation (day number is an anchor)
                e.preventDefault();

                // Get the day cell
                const dayCell = dayNumber.closest('.fc-daygrid-day');
                if (!dayCell) return;

                // Get the date from the day cell's data attribute
                const dateStr = dayCell.getAttribute('data-date');
                if (!dateStr) return;

                // Clear any existing timer
                if (this.dayNumberClickTimer) {
                    clearTimeout(this.dayNumberClickTimer);
                }

                // Set timer to show popover after threshold + 150ms (allows time for double-click)
                this.dayNumberClickTimer = setTimeout(() => {
                    // Get all events for this date
                    const events = this.calendar.getEvents().filter(event => {
                        // Get date in YYYY-MM-DD format without timezone conversion
                        const getLocalDateStr = (d) => {
                            const year = d.getFullYear();
                            const month = String(d.getMonth() + 1).padStart(2, '0');
                            const day = String(d.getDate()).padStart(2, '0');
                            return `${year}-${month}-${day}`;
                        };

                        const eventStartDate = getLocalDateStr(event.start);
                        const clickedDate = dateStr; // Already in YYYY-MM-DD format

                        // Check if event starts on this day
                        return eventStartDate === clickedDate;
                    });

                    // If there are events, show the popover
                    if (events.length > 0) {
                        // Parse the date for popover
                        const date = new Date(dateStr + 'T00:00:00');
                        this.showDayEventsPopover(events, dayNumber, date);
                    }
                }, this.doubleClickThreshold + 150);
            });

            // Handle double-clicks anywhere in a day cell - open new job/reminder form
            this.calendarEl.addEventListener('dblclick', (e) => {
                // Ignore double-clicks on events themselves (let event click handlers handle those)
                if (e.target.closest('.fc-event')) {
                    return;
                }

                // Find the day cell that was double-clicked
                const dayCell = e.target.closest('.fc-daygrid-day');
                if (!dayCell) return;

                // Prevent default navigation
                e.preventDefault();

                // Cancel the single-click timer
                if (this.dayNumberClickTimer) {
                    clearTimeout(this.dayNumberClickTimer);
                    this.dayNumberClickTimer = null;
                }

                // Get the date from the day cell's data attribute
                const dateStr = dayCell.getAttribute('data-date');
                if (!dateStr) return;

                // Parse the date
                const date = new Date(dateStr + 'T00:00:00');
                const now = Date.now();
                const dateMs = date.getTime();

                // If this double-click was already handled via dateClick logic, skip duplicate load
                if (this.lastOpenedDateByDoubleClick === dateMs && (now - this.lastOpenedDateTimestamp) < (this.doubleClickThreshold + 150)) {
                    return;
                }

                // Record this handled double click
                this.lastOpenedDateByDoubleClick = dateMs;
                this.lastOpenedDateTimestamp = now;

                // Open the appropriate form
                this.openCreateFormForDate(date);
            });
        }

        /**
         * Open the create job or call reminder form for the provided date
         */
        openCreateFormForDate(date) {
            try {
                if (!window.JobPanel) {
                    console.error('JobPanel not available');
                    this.showError('Job panel functionality not available. Please refresh the page.');
                    return;
                }

                const isSunday = date.getDay() === 0;
                const dateStr = date.toISOString().split('T')[0];

                const loadForm = () => {
                    // Close any open day popovers before loading the form
                    document.querySelectorAll('.fc-more-popover').forEach(pop => pop.remove());

                    if (isSunday) {
                        let url = `/call-reminders/new/partial/?date=${dateStr}`;
                        if (this.defaultCalendar) {
                            url += `&calendar=${this.defaultCalendar}`;
                        }
                        window.JobPanel.setTitle('New Call Reminder');
                        window.JobPanel.load(url);
                    } else {
                        let url = `/jobs/new/partial/?date=${dateStr}`;
                        if (this.defaultCalendar) {
                            url += `&calendar=${this.defaultCalendar}`;
                        }
                        window.JobPanel.setTitle('New Job');
                        window.JobPanel.load(url);
                    }
                };

                if (window.JobPanel.hasUnsavedChanges && window.JobPanel.hasUnsavedChanges()) {
                    window.JobPanel.saveForm(() => {
                        const currentJobId = window.JobPanel.currentJobId;
                        if (currentJobId && window.JobWorkspace && !window.JobWorkspace.hasJob(currentJobId)) {
                            const form = document.querySelector('#job-panel .panel-body form');
                            const businessName = form?.querySelector('input[name="business_name"]')?.value ||
                                form?.querySelector('input[name="contact_name"]')?.value ||
                                'Unnamed Job';
                            const trailerColor = form?.querySelector('input[name="trailer_color"]')?.value || '';

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
        }

        /**
         * Show a popover with all events for a specific day
         */
        showDayEventsPopover(events, anchorEl, date) {
            // Create popover element
            const popover = document.createElement('div');
            popover.className = 'fc-popover fc-more-popover';
            popover.style.cssText = `
                position: absolute;
                z-index: 10000;
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                min-width: 300px;
                max-width: 400px;
                max-height: 600px;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            `;

            // Format date for header
            const dateStr = this.calendar.formatDate(date, {
                month: 'long',
                day: 'numeric',
                year: 'numeric'
            });

            // Create header
            const header = document.createElement('div');
            header.style.cssText = `
                padding: 10px 12px;
                background: #f8f9fa;
                border-bottom: 1px solid #ddd;
                font-weight: 600;
                display: flex;
                justify-content: space-between;
                align-items: center;
            `;
            header.innerHTML = `
                <span>${dateStr}</span>
                <button class="fc-popover-close" style="
                    background: none;
                    border: none;
                    font-size: 20px;
                    cursor: pointer;
                    padding: 0;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #666;
                    line-height: 1;
                ">&times;</button>
            `;

            // Create event list container
            const eventList = document.createElement('div');
            eventList.style.cssText = `
                padding: 8px;
                overflow-y: auto;
                max-height: 550px;
            `;

            // Sort events by start time
            events.sort((a, b) => {
                if (a.allDay && !b.allDay) return -1;
                if (!a.allDay && b.allDay) return 1;
                return a.start - b.start;
            });

            // Add events to list
            events.forEach(event => {
                // Get calendar color and apply lighter shade for completed events
                const calendarColor = event.extendedProps?.calendar_color || '#3788d8';
                const isCompleted = event.extendedProps?.status === 'completed';

                let finalColor = calendarColor;
                if (isCompleted) {
                    finalColor = this.lightenColor(calendarColor, 0.3);
                }

                const backgroundColor = event.backgroundColor || finalColor;
                const textDecoration = isCompleted ? 'text-decoration: line-through;' : '';

                const eventEl = document.createElement('div');
                eventEl.style.cssText = `
                    padding: 2px 4px;
                    margin-bottom: 2px;
                    border-radius: 2px;
                    cursor: pointer;
                    background: ${backgroundColor};
                    color: white;
                    font-size: 12px;
                    line-height: 1.3;
                    min-height: 20px;
                    display: flex;
                    align-items: center;
                    transition: opacity 0.2s;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    ${textDecoration}
                `;

                // Format time
                let timeStr = '';
                if (!event.allDay) {
                    timeStr = this.calendar.formatDate(event.start, {
                        hour: 'numeric',
                        minute: '2-digit',
                        meridiem: 'short'
                    }) + ' ';
                }

                eventEl.innerHTML = `<strong style="margin-right: 4px;">${timeStr}</strong><span>${event.title}</span>`;

                // Add hover tooltip
                eventEl.addEventListener('mouseenter', (e) => {
                    // Clear any existing timeout
                    if (this.tooltipTimeout) {
                        clearTimeout(this.tooltipTimeout);
                    }

                    // Set a 500ms delay before showing the tooltip
                    this.tooltipTimeout = setTimeout(() => {
                        this.showEventTooltip(event, eventEl);
                        this.tooltipTimeout = null;
                    }, 500);
                });
                eventEl.addEventListener('mouseleave', () => {
                    // Clear the timeout if user stops hovering before delay completes
                    if (this.tooltipTimeout) {
                        clearTimeout(this.tooltipTimeout);
                        this.tooltipTimeout = null;
                    }

                    // Hide tooltip
                    this.hideEventTooltip();
                });

                // Add click handler to open the event
                eventEl.addEventListener('click', (e) => {
                    e.stopPropagation();
                    // Hide tooltip
                    this.hideEventTooltip();
                    // Close popover (using idempotent close function)
                    closePopover();
                    // Trigger event click
                    this.handleEventClick({ event });
                });

                eventList.appendChild(eventEl);
            });

            // Assemble popover
            popover.appendChild(header);
            popover.appendChild(eventList);

            // Idempotent close function - safe to call multiple times
            let outsideClickHandler = null;
            const closePopover = () => {
                // Remove document click listener first
                if (outsideClickHandler) {
                    document.removeEventListener('click', outsideClickHandler);
                    outsideClickHandler = null;
                }
                // Only remove from DOM if still attached
                if (popover.isConnected) {
                    this.hideEventTooltip();
                    popover.remove();
                }
            };

            // Add close button handler
            const closeBtn = header.querySelector('.fc-popover-close');
            closeBtn.addEventListener('click', () => {
                closePopover();
            });

            // Add to body
            document.body.appendChild(popover);

            // Position the popover near the anchor element
            const anchorRect = anchorEl.getBoundingClientRect();
            const popoverRect = popover.getBoundingClientRect();

            // Calculate position (try to show below, but above if no room)
            let top = anchorRect.bottom + 5;
            let left = anchorRect.left;

            // Check if popover goes off bottom of screen
            if (top + popoverRect.height > window.innerHeight) {
                top = anchorRect.top - popoverRect.height - 5;
            }

            // Check if popover goes off right of screen
            if (left + popoverRect.width > window.innerWidth) {
                left = window.innerWidth - popoverRect.width - 10;
            }

            // Ensure popover doesn't go off left of screen
            if (left < 10) {
                left = 10;
            }

            popover.style.top = top + 'px';
            popover.style.left = left + 'px';

            // Close popover when clicking outside
            outsideClickHandler = (e) => {
                if (!popover.contains(e.target)) {
                    closePopover();
                }
            };
            setTimeout(() => {
                document.addEventListener('click', outsideClickHandler);
            }, 0);
        }

        /**
         * Ensure calendar content is visible
         */
        ensureCalendarVisible() {
            // Ensure all day numbers are visible
            const dayNumbers = document.querySelectorAll('.fc-daygrid-day-number');
            dayNumbers.forEach(dayNumber => {
                dayNumber.style.display = 'block';
                dayNumber.style.visibility = 'visible';
                dayNumber.style.opacity = '1';
            });

            // Adjust header column widths to match content
            this.adjustHeaderColumnWidths();
        }

        /**
         * Adjust header column widths to match content columns
         */
        adjustHeaderColumnWidths() {
            // Find the header row
            const headerRow = document.querySelector('.fc-col-header');
            if (!headerRow) return;

            // Find all header cells and make them all equal width
            const headerCells = headerRow.querySelectorAll('th');
            headerCells.forEach((cell) => {
                // All days equal width (100% / 7 days = 14.29%)
                cell.style.width = '14.29%';
                cell.style.minWidth = '14.29%';
                cell.style.maxWidth = '14.29%';
            });
        }

        /**
         * Save current calendar date to localStorage
         */
        saveCurrentDate() {
            if (this.calendar) {
                const currentDate = this.calendar.getDate();
                localStorage.setItem('gts-calendar-current-date', currentDate.toISOString());
            }
        }

        /**
         * Force all week rows to have equal height (25% each)
         */
        forceEqualWeekHeights() {
            // Use multiple timeouts to catch different render stages
            const applyHeights = () => {
                // Find the daygrid body
                const daygridBody = document.querySelector('.fc-daygrid-body');
                if (!daygridBody) return;

                // Get the total available height
                const totalHeight = daygridBody.offsetHeight;
                const weekHeight = Math.floor(totalHeight / 4); // Exact pixel height for each week

                // Find all week rows
                const weekRows = document.querySelectorAll('.fc-daygrid-body table tbody tr');

                if (weekRows.length === 4 && weekHeight > 0) {
                    weekRows.forEach((row) => {
                        // Set explicit pixel heights
                        row.style.setProperty('height', `${weekHeight}px`, 'important');
                        row.style.setProperty('max-height', `${weekHeight}px`, 'important');
                        row.style.setProperty('min-height', `${weekHeight}px`, 'important');
                        row.style.setProperty('overflow', 'hidden', 'important');

                        // Also set on the cells within the row
                        const cells = row.querySelectorAll('td');
                        cells.forEach(cell => {
                            cell.style.setProperty('height', `${weekHeight}px`, 'important');
                            cell.style.setProperty('max-height', `${weekHeight}px`, 'important');
                            cell.style.setProperty('overflow', 'hidden', 'important');
                        });
                    });
                }
            };

            // Apply immediately
            setTimeout(applyHeights, 10);
            // Apply again after a delay to catch late renders
            setTimeout(applyHeights, 100);
            setTimeout(applyHeights, 250);
        }

        /**
         * Get saved calendar date from localStorage
         */
        getSavedDate() {
            try {
                const savedDate = localStorage.getItem('gts-calendar-current-date');
                return savedDate ? new Date(savedDate) : null;
            } catch (error) {
                console.warn('Error loading saved calendar date:', error);
                return null;
            }
        }

        /**
         * Utility functions for Today panel
         */
        startOfDay(date) {
            const d = new Date(date);
            d.setHours(0, 0, 0, 0);
            return d;
        }

        /**
         * Format date as YYYY-MM-DD in local timezone (not UTC)
         */
        formatDateForInput(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }

        endOfDay(date) {
            const d = new Date(date);
            d.setHours(23, 59, 59, 999);
            return d;
        }

        isSameDay(a, b) {
            return a.getFullYear() === b.getFullYear() &&
                a.getMonth() === b.getMonth() &&
                a.getDate() === b.getDate();
        }

        /**
         * Check if an event overlaps with a given day using robust exclusive-end logic
         */
        eventOverlapsDay(ev, day) {
            const dayStart = this.startOfDay(day);
            const dayEnd = this.endOfDay(day);

            const evStart = ev.start ? new Date(ev.start) : null;
            let evEnd = ev.end ? new Date(ev.end) : null;

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
        }

        /**
         * Render the Today panel with events for the selected day
         */
        renderTodayPanel(selectedDate = null) {
            const listEl = document.getElementById('todayList');
            const labelEl = document.getElementById('todayDateLabel');
            const titleEl = document.getElementById('todayPanelTitle');
            const datePicker = document.getElementById('todayDatePicker');

            if (!listEl || !labelEl || !titleEl) return;

            const targetDate = selectedDate || new Date(); // Use provided date or today
            const today = new Date();
            const isToday = targetDate.toDateString() === today.toDateString();

            // Update title
            titleEl.textContent = isToday ? 'Today' : 'Events';

            // Update date label
            labelEl.textContent = this.calendar.formatDate(targetDate, {
                weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
            });

            // Update date picker value only if it's different
            if (datePicker) {
                const dateStr = this.formatDateForInput(targetDate);
                if (datePicker.value !== dateStr) {
                    datePicker.value = dateStr;
                }
            }

            // Pull the current client-side set (after fetch)
            const events = this.calendar.getEvents().filter(ev => this.eventOverlapsDay(ev, targetDate));

            // Sort: all-day first, then by start time
            events.sort((a, b) => {
                if (a.allDay && !b.allDay) return -1;
                if (!a.allDay && b.allDay) return 1;
                return (a.start?.getTime() || 0) - (b.start?.getTime() || 0);
            });

            listEl.innerHTML = '';
            if (!events.length) {
                const emptyText = isToday ? 'No events today.' : 'No events for this day.';
                listEl.innerHTML = `<div class="today-empty">${emptyText}</div>`;
                return;
            }

            for (const ev of events) {
                const timeStr = ev.allDay
                    ? 'All day'
                    : `${this.calendar.formatDate(ev.start, { hour: 'numeric', minute: '2-digit' })}–${this.calendar.formatDate(ev.end || ev.start, { hour: 'numeric', minute: '2-digit' })}`;

                // Get calendar color from extendedProps or use default
                const calendarColor = ev.extendedProps?.calendar_color || '#3B82F6';

                // Check if job is completed for strikethrough styling and lighter color
                const isCompleted = ev.extendedProps?.status === 'completed';
                const textDecoration = isCompleted ? 'text-decoration: line-through;' : '';

                // Apply lighter shade for completed events (same as calendar events)
                let finalColor = calendarColor;
                if (isCompleted) {
                    finalColor = this.lightenColor(calendarColor, 0.3);
                }

                // Use event's backgroundColor if available, otherwise use the calculated color
                const backgroundColor = ev.backgroundColor || finalColor;

                const item = document.createElement('div');
                item.className = 'today-item';
                item.dataset.eventId = ev.id || '';
                item.style.backgroundColor = backgroundColor;
                item.style.borderLeft = `4px solid ${backgroundColor}`;
                item.innerHTML = `
                    <div style="${textDecoration}"><span class="today-item-time">${timeStr}</span>
                    <span class="today-item-title">${ev.title || '(no title)'}</span></div>
                `;

                // Add click handler
                item.addEventListener('click', () => {
                    // Open job edit form when clicking on today sidebar event
                    const extendedProps = ev.extendedProps || {};
                    const jobId = extendedProps.job_id;

                    if (jobId && window.JobPanel) {
                        // Check if there are unsaved changes
                        if (window.JobPanel.hasUnsavedChanges && window.JobPanel.hasUnsavedChanges()) {
                            // Set flag to prevent panel from auto-closing
                            window.JobPanel.isSwitchingJobs = true;
                            // Save the form first
                            window.JobPanel.saveForm(() => {
                                // After saving, add to workspace if it has a job ID
                                const currentJobId = window.JobPanel.currentJobId;
                                if (currentJobId && window.JobWorkspace && !window.JobWorkspace.hasJob(currentJobId)) {
                                    // Get job details from the form
                                    const form = document.querySelector('#job-panel .panel-body form');
                                    const businessName = form?.querySelector('input[name="business_name"]')?.value ||
                                        form?.querySelector('input[name="contact_name"]')?.value ||
                                        'Unnamed Job';
                                    const trailerColor = form?.querySelector('input[name="trailer_color"]')?.value || '';

                                    // Add to workspace as minimized
                                    window.JobWorkspace.addJobMinimized(currentJobId, {
                                        customerName: businessName,
                                        trailerColor: trailerColor,
                                        calendarColor: '#3B82F6'
                                    });
                                }

                                // Now open the new job
                                if (window.JobWorkspace) {
                                    // Check if the clicked job is already in the workspace
                                    if (window.JobWorkspace.hasJob(jobId)) {
                                        // Job is in workspace, switch to it
                                        window.JobWorkspace.switchToJob(jobId);
                                    } else {
                                        // Job is not in workspace, open it fresh
                                        const props = ev.extendedProps;
                                        window.JobWorkspace.openJob(jobId, {
                                            customerName: props.business_name || props.contact_name || 'Job',
                                            trailerColor: props.trailer_color || '',
                                            calendarColor: props.calendar_color || '#3B82F6'
                                        });
                                    }
                                } else {
                                    // Fallback to direct panel opening if workspace not available
                                    this.openJobInPanel(ev, jobId);
                                }

                                // Clear the switching flag after a delay to allow new form to load
                                setTimeout(() => {
                                    window.JobPanel.isSwitchingJobs = false;
                                }, 500);
                            });
                        } else {
                            // No unsaved changes, open directly
                            if (window.JobWorkspace) {
                                // Check if the clicked job is already in the workspace
                                if (window.JobWorkspace.hasJob(jobId)) {
                                    // Job is in workspace, switch to it
                                    window.JobWorkspace.switchToJob(jobId);
                                } else {
                                    // Job is not in workspace, open it fresh
                                    const props = ev.extendedProps;
                                    window.JobWorkspace.openJob(jobId, {
                                        customerName: props.business_name || props.contact_name || 'Job',
                                        trailerColor: props.trailer_color || '',
                                        calendarColor: props.calendar_color || '#3B82F6'
                                    });
                                }
                            } else {
                                // Fallback to direct panel opening if workspace not available
                                this.openJobInPanel(ev, jobId);
                            }
                        }
                    } else {
                        console.error('JobPanel not available or job ID missing for event:', ev.id);
                        // Fallback: navigate to the date
                        this.calendar.gotoDate(ev.start || new Date());
                        // optional: highlight after render
                        setTimeout(() => {
                            const el = this.calendar.el.querySelector('[data-event-id="' + (ev.id || '') + '"]');
                            el?.classList.add('ring-2');
                            setTimeout(() => el?.classList.remove('ring-2'), 1200);
                        }, 30);
                    }
                });

                // Add hover tooltip for today sidebar items
                item.addEventListener('mouseenter', (e) => {
                    // Clear any existing timeout
                    if (this.tooltipTimeout) {
                        clearTimeout(this.tooltipTimeout);
                    }

                    // Set a 500ms delay before showing the tooltip
                    this.tooltipTimeout = setTimeout(() => {
                        this.showEventTooltip(ev, e.target);
                        this.tooltipTimeout = null;
                    }, 500);
                });

                item.addEventListener('mouseleave', () => {
                    // Clear the timeout if user stops hovering before delay completes
                    if (this.tooltipTimeout) {
                        clearTimeout(this.tooltipTimeout);
                        this.tooltipTimeout = null;
                    }

                    this.hideEventTooltip();
                });

                listEl.appendChild(item);
            }
        }

        /**
         * Initialize date picker controls for the Today panel
         */
        initializeDatePickerControls() {
            const prevDayBtn = document.getElementById('prevDayBtn');
            const nextDayBtn = document.getElementById('nextDayBtn');
            const todayBtn = document.getElementById('todayBtn');
            const datePicker = document.getElementById('todayDatePicker');
            const titleBtn = document.getElementById('todayPanelTitle');

            if (!prevDayBtn || !nextDayBtn || !todayBtn || !datePicker || !titleBtn) {
                console.warn('Date picker controls not found');
                return;
            }

            // Set initial date to today
            const today = new Date();
            datePicker.value = this.formatDateForInput(today);

            // Initial render with today's date
            this.renderTodayPanel(today);

            // Previous day button
            prevDayBtn.addEventListener('click', () => {
                const [year, month, day] = datePicker.value.split('-').map(Number);
                const currentDate = new Date(year, month - 1, day);
                currentDate.setDate(currentDate.getDate() - 1);
                datePicker.value = this.formatDateForInput(currentDate);
                // Trigger change event to update the panel
                datePicker.dispatchEvent(new Event('change'));
            });

            // Next day button
            nextDayBtn.addEventListener('click', () => {
                const [year, month, day] = datePicker.value.split('-').map(Number);
                const currentDate = new Date(year, month - 1, day);
                currentDate.setDate(currentDate.getDate() + 1);
                datePicker.value = this.formatDateForInput(currentDate);
                // Trigger change event to update the panel
                datePicker.dispatchEvent(new Event('change'));
            });

            // Today button
            todayBtn.addEventListener('click', () => {
                const today = new Date();
                datePicker.value = this.formatDateForInput(today);
                // Trigger change event to update the panel
                datePicker.dispatchEvent(new Event('change'));
            });

            // Date picker change
            datePicker.addEventListener('change', () => {
                const [year, month, day] = datePicker.value.split('-').map(Number);
                const selectedDate = new Date(year, month - 1, day);
                this.renderTodayPanel(selectedDate);
            });

            // Title button click - go to today
            titleBtn.addEventListener('click', () => {
                const today = new Date();
                datePicker.value = this.formatDateForInput(today);
                // Trigger change event to update the panel
                datePicker.dispatchEvent(new Event('change'));
            });
        }

        /**
         * Focus an event in the calendar by jumping to its date
         */
        focusEventInCalendar(ev) {
            // Jump to the event's start week inside our sliding 4-week view
            this.calendar.gotoDate(ev.start || new Date());

            // Save the new position
            this.saveCurrentDate();
        }

        /**
         * Adjust all day column widths to be equal
         */
        adjustSundayColumnWidth() {
            // Find the table body
            const tableBody = document.querySelector('.fc-daygrid-body');
            if (!tableBody) return;

            // Find all rows in the table
            const rows = tableBody.querySelectorAll('tr');

            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                cells.forEach((cell) => {
                    // All days equal width (100% / 7 days = 14.29%)
                    cell.style.width = '14.29%';
                    cell.style.minWidth = '14.29%';
                    cell.style.maxWidth = '14.29%';
                });
            });

            // Also target the day columns directly
            const dayColumns = document.querySelectorAll('.fc-daygrid-day');
            dayColumns.forEach(column => {
                // All days equal width (100% / 7 days = 14.29%)
                column.style.width = '14.29%';
                column.style.minWidth = '14.29%';
                column.style.maxWidth = '14.29%';
            });
        }

        /**
         * Style the custom buttons for better appearance
         */
        styleCustomButtons() {
            // Wait a bit for the DOM to be ready
            setTimeout(() => {
                // Adjust Sunday column width
                this.adjustSundayColumnWidth();

                // Hide the original calendar filter button since we moved it
                const calendarFilterBtn = document.querySelector('.fc-calendarFilterButton-button');
                if (calendarFilterBtn) {
                    calendarFilterBtn.style.display = 'none';
                }

                // Hide the original status filter button since we moved it
                const statusFilterBtn = document.querySelector('.fc-statusFilterButton-button');
                if (statusFilterBtn) {
                    statusFilterBtn.style.display = 'none';
                }

                // Add Jump to Date control
                this.addJumpToDateControl();
            }, 100);
        }

        /**
         * Add Jump to Date, Calendar, and Status controls to the calendar toolbar
         */
        addJumpToDateControl() {
            // Find the calendar toolbar
            const toolbar = document.querySelector('.fc-header-toolbar');
            if (!toolbar) return;

            // Create the controls container
            const controlsContainer = document.createElement('div');
            controlsContainer.className = 'fc-unified-controls';
            controlsContainer.style.cssText = `
                display: flex;
                align-items: center;
                gap: 12px;
                margin-right: 16px;
            `;

            // Create Jump to Date section
            const jumpToDateSection = document.createElement('div');
            jumpToDateSection.style.cssText = `
                display: flex;
                align-items: center;
                gap: 8px;
            `;

            // Create Jump to Date label - REMOVED
            // const dateLabel = document.createElement('label');
            // dateLabel.setAttribute('for', 'jump-to-date');
            // dateLabel.textContent = 'Jump to date';
            // dateLabel.style.cssText = `
            //     font-size: 14px;
            //     color: #666;
            //     white-space: nowrap;
            //     cursor: pointer;
            // `;

            // Create Jump to Date input
            const dateInput = document.createElement('input');
            dateInput.id = 'jump-to-date';
            dateInput.name = 'jump_to_date';
            dateInput.type = 'text';
            dateInput.placeholder = 'YYYY-MM-DD';
            dateInput.autocomplete = 'off';
            dateInput.style.cssText = `
                height: 36px;
                width: 176px;
                border-radius: 6px;
                border: 1px solid #d1d5db;
                padding: 0 12px;
                font-size: 14px;
                color: #374151;
                background: #ffffff;
                transition: border-color 0.2s ease;
            `;

            // Add hover and focus styles for date input
            dateInput.addEventListener('mouseenter', () => {
                dateInput.style.borderColor = '#9ca3af';
            });
            dateInput.addEventListener('mouseleave', () => {
                if (document.activeElement !== dateInput) {
                    dateInput.style.borderColor = '#d1d5db';
                }
            });
            dateInput.addEventListener('focus', () => {
                dateInput.style.borderColor = '#3b82f6';
                dateInput.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
            });
            dateInput.addEventListener('blur', () => {
                dateInput.style.borderColor = '#d1d5db';
                dateInput.style.boxShadow = 'none';
            });

            // Create Today button
            const todayButton = document.createElement('button');
            todayButton.type = 'button';
            todayButton.title = 'Jump to Today';
            todayButton.style.cssText = `
                height: 36px;
                width: 36px;
                padding: 0;
                border-radius: 6px;
                border: 1px solid #d1d5db;
                background: #ffffff;
                color: #374151;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            `;

            // Add calendar icon SVG
            todayButton.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="16" y1="2" x2="16" y2="6"></line>
                    <line x1="8" y1="2" x2="8" y2="6"></line>
                    <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
            `;

            // Add hover styles for today button
            todayButton.addEventListener('mouseenter', () => {
                todayButton.style.borderColor = '#3b82f6';
                todayButton.style.backgroundColor = '#eff6ff';
                todayButton.style.color = '#3b82f6';
            });
            todayButton.addEventListener('mouseleave', () => {
                todayButton.style.borderColor = '#d1d5db';
                todayButton.style.backgroundColor = '#ffffff';
                todayButton.style.color = '#374151';
            });

            // Add click handler to jump to today
            todayButton.addEventListener('click', () => {
                const today = new Date();
                this.calendar.gotoDate(today);

                // Update the date input
                const fmt = (d) => {
                    const pad = (n) => String(n).padStart(2, '0');
                    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
                };
                dateInput.value = fmt(today);

                // Update URL param
                const sp = new URLSearchParams(window.location.search);
                sp.set('date', fmt(today));
                history.replaceState({}, '', `${location.pathname}?${sp.toString()}`);
            });

            // Create Calendar dropdown section
            const calendarSection = document.createElement('div');
            calendarSection.style.cssText = `
                display: flex;
                align-items: center;
                gap: 8px;
            `;

            // Create Calendar multi-select button and popover
            const calendarMultiSelect = this.createCalendarMultiSelect();

            // Create Status dropdown section
            const statusSection = document.createElement('div');
            statusSection.style.cssText = `
                display: flex;
                align-items: center;
                gap: 8px;
            `;

            // Create Status label - REMOVED
            // const statusLabel = document.createElement('label');
            // statusLabel.setAttribute('for', 'status-filter-moved');
            // statusLabel.textContent = 'Status';
            // statusLabel.style.cssText = `
            //             font-size: 14px;
            //     color: #666;
            //     white-space: nowrap;
            //             cursor: pointer;
            // `;

            // Create Status dropdown
            const statusDropdown = document.createElement('select');
            statusDropdown.id = 'status-filter-moved';
            statusDropdown.style.cssText = `
                height: 36px;
                        min-width: 120px;
                border-radius: 6px;
                border: 1px solid #d1d5db;
                padding: 0 12px;
                font-size: 14px;
                color: #374151;
                background: #ffffff;
                cursor: pointer;
                transition: border-color 0.2s ease;
            `;

            // Build status options
            statusDropdown.innerHTML = `
                <option value="">All Status</option>
                <option value="uncompleted">Uncompleted</option>
                <option value="completed">Completed</option>
            `;

            // Add hover and focus styles for status dropdown
            statusDropdown.addEventListener('mouseenter', () => {
                statusDropdown.style.borderColor = '#9ca3af';
            });
            statusDropdown.addEventListener('mouseleave', () => {
                if (document.activeElement !== statusDropdown) {
                    statusDropdown.style.borderColor = '#d1d5db';
                }
            });
            statusDropdown.addEventListener('focus', () => {
                statusDropdown.style.borderColor = '#3b82f6';
                statusDropdown.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
            });
            statusDropdown.addEventListener('blur', () => {
                statusDropdown.style.borderColor = '#d1d5db';
                statusDropdown.style.boxShadow = 'none';
            });

            // Assemble the sections
            // jumpToDateSection.appendChild(dateLabel); // Label removed
            jumpToDateSection.appendChild(dateInput);
            jumpToDateSection.appendChild(todayButton);
            // calendarSection.appendChild(calendarLabel); // Label removed
            calendarSection.appendChild(calendarMultiSelect);
            // statusSection.appendChild(statusLabel); // Label removed
            statusSection.appendChild(statusDropdown);

            controlsContainer.appendChild(jumpToDateSection);
            controlsContainer.appendChild(calendarSection);
            controlsContainer.appendChild(statusSection);
            toolbar.insertBefore(controlsContainer, toolbar.firstChild);

            // Initialize the jump to date functionality
            this.initializeJumpToDate(dateInput);

            // Calendar multi-select is initialized within createCalendarMultiSelect()
            // Update the calendar button text now that it's in the DOM
            this.updateCalendarButtonText();

            // Initialize the status dropdown functionality
            this.initializeMovedStatusDropdown(statusDropdown);
        }

        /**
         * Create calendar multi-select checkbox UI
         */
        createCalendarMultiSelect() {
            const container = document.createElement('div');
            container.style.cssText = 'position: relative; display: inline-block;';

            // Create button
            const button = document.createElement('button');
            button.id = 'calendar-multi-select-button';
            button.type = 'button';
            button.style.cssText = `
                height: 36px;
                min-width: 140px;
                border-radius: 6px;
                border: 1px solid #d1d5db;
                padding: 0 32px 0 12px;
                font-size: 14px;
                color: #374151;
                background: #ffffff;
                cursor: pointer;
                transition: border-color 0.2s ease;
                text-align: left;
                position: relative;
                white-space: nowrap;
            `;

            // Add dropdown arrow
            button.innerHTML = `
                <span id="calendar-button-text">All Calendars</span>
                <svg style="position: absolute; right: 8px; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; pointer-events: none;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
            `;

            // Create popover
            const popover = document.createElement('div');
            popover.id = 'calendar-multi-select-popover';
            popover.style.cssText = `
                position: absolute;
                top: calc(100% + 4px);
                left: 0;
                min-width: 220px;
                max-height: 400px;
                overflow-y: auto;
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
                z-index: 1000;
                display: none;
                padding: 8px;
            `;

            // selectedCalendars and defaultCalendar are already initialized in the constructor
            // Just get the list of available calendars
            const calendars = window.calendarConfig?.calendars || [];

            // Build checkboxes
            let checkboxesHTML = '';

            // Add "All" checkbox
            const allChecked = this.selectedCalendars.size === calendars.length;
            checkboxesHTML += `
                <label style="display: flex; align-items: center; padding: 8px; cursor: pointer; border-radius: 4px; transition: background 0.15s;" 
                       onmouseover="this.style.background='#f3f4f6'" onmouseout="this.style.background='transparent'">
                    <input type="checkbox" data-calendar-id="all" ${allChecked ? 'checked' : ''} 
                           style="width: 16px; height: 16px; margin-right: 8px; cursor: pointer;">
                    <span style="font-weight: 600; color: #111827;">All Calendars</span>
                </label>
                <div style="border-top: 1px solid #e5e7eb; margin: 4px 0;"></div>
            `;

            // Add individual calendar checkboxes with clickable name areas
            calendars.forEach(cal => {
                const isChecked = this.selectedCalendars.has(cal.id);
                const isDefault = this.defaultCalendar === cal.id;
                const backgroundColor = isDefault ? '#e0f2fe' : 'transparent';

                checkboxesHTML += `
                    <div class="calendar-item" data-calendar-id="${cal.id}" 
                         style="display: flex; align-items: center; padding: 8px; border-radius: 4px; transition: background 0.15s; background: ${backgroundColor};">
                        <input type="checkbox" data-calendar-id="${cal.id}" ${isChecked ? 'checked' : ''} 
                               style="width: 16px; height: 16px; margin-right: 8px; cursor: pointer; accent-color: ${cal.color};">
                        <div class="calendar-name-area" data-calendar-id="${cal.id}" 
                             style="display: flex; align-items: center; flex: 1; cursor: pointer;">
                            <span style="display: inline-block; width: 12px; height: 12px; border-radius: 3px; background: ${cal.color}; margin-right: 8px;"></span>
                            <span style="color: #374151; flex: 1;">${cal.name}</span>
                        </div>
                    </div>
                `;
            });

            popover.innerHTML = checkboxesHTML;

            // Prevent scroll events from propagating to calendar (prevents week navigation)
            popover.addEventListener('wheel', (e) => {
                e.stopPropagation();
            }, { passive: false });

            // Toggle popover on button click
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = popover.style.display === 'block';
                popover.style.display = isVisible ? 'none' : 'block';
            });

            // Close popover when clicking outside
            document.addEventListener('click', (e) => {
                if (!container.contains(e.target)) {
                    popover.style.display = 'none';
                }
            });

            // Handle calendar name clicks (set as default)
            popover.addEventListener('click', (e) => {
                const nameArea = e.target.closest('.calendar-name-area');
                if (nameArea) {
                    e.stopPropagation();
                    const calendarId = parseInt(nameArea.dataset.calendarId);

                    // Set as default calendar
                    this.defaultCalendar = calendarId;

                    // Auto-check the checkbox if not already checked
                    if (!this.selectedCalendars.has(calendarId)) {
                        this.selectedCalendars.add(calendarId);
                        const checkbox = popover.querySelector(`input[type="checkbox"][data-calendar-id="${calendarId}"]`);
                        if (checkbox) {
                            checkbox.checked = true;
                        }

                        // Update "All" checkbox
                        const allCheckbox = popover.querySelector('input[data-calendar-id="all"]');
                        allCheckbox.checked = this.selectedCalendars.size === calendars.length;

                        // Save selected calendars
                        try {
                            localStorage.setItem('gts-selected-calendars', JSON.stringify(Array.from(this.selectedCalendars)));
                        } catch (error) {
                            console.warn('Error saving calendar selection:', error);
                        }
                    }

                    // Update visual highlighting
                    popover.querySelectorAll('.calendar-item').forEach(item => {
                        const itemId = parseInt(item.dataset.calendarId);
                        item.style.background = itemId === calendarId ? '#e0f2fe' : 'transparent';
                    });

                    // Save default calendar to localStorage
                    try {
                        localStorage.setItem('gts-default-calendar', calendarId.toString());
                    } catch (error) {
                        console.warn('Error saving default calendar:', error);
                    }

                    // Update button text
                    this.updateCalendarButtonText();

                    // Refresh calendar (debounced to prevent rapid successive calls)
                    this.debouncedRefetch();
                }
            });

            // Handle checkbox changes
            popover.addEventListener('change', (e) => {
                if (e.target.type === 'checkbox') {
                    const calendarId = e.target.dataset.calendarId;

                    if (calendarId === 'all') {
                        // Toggle all calendars
                        const allCheckbox = e.target;
                        const checkboxes = popover.querySelectorAll('input[type="checkbox"][data-calendar-id]:not([data-calendar-id="all"])');

                        if (allCheckbox.checked) {
                            // Select all
                            this.selectedCalendars = new Set(calendars.map(cal => cal.id));
                            checkboxes.forEach(cb => cb.checked = true);
                        } else {
                            // Deselect all
                            this.selectedCalendars.clear();
                            checkboxes.forEach(cb => cb.checked = false);
                        }
                    } else {
                        // Toggle individual calendar
                        const id = parseInt(calendarId);
                        if (e.target.checked) {
                            this.selectedCalendars.add(id);
                        } else {
                            this.selectedCalendars.delete(id);
                        }

                        // Update "All" checkbox
                        const allCheckbox = popover.querySelector('input[data-calendar-id="all"]');
                        allCheckbox.checked = this.selectedCalendars.size === calendars.length;
                    }

                    // Update button text
                    this.updateCalendarButtonText();

                    // Save to localStorage
                    try {
                        localStorage.setItem('gts-selected-calendars', JSON.stringify(Array.from(this.selectedCalendars)));
                    } catch (error) {
                        console.warn('Error saving calendar selection:', error);
                    }

                    // Refresh calendar (debounced to prevent rapid successive calls)
                    this.debouncedRefetch();
                }
            });

            // Note: Button text will be updated after the element is added to the DOM
            // See updateCalendarButtonText() call in addJumpToDateControl()

            container.appendChild(button);
            container.appendChild(popover);

            return container;
        }

        /**
         * Update calendar button text based on selection
         */
        updateCalendarButtonText() {
            const buttonText = document.getElementById('calendar-button-text');
            if (!buttonText) return;

            const calendars = window.calendarConfig?.calendars || [];
            const selectedCount = this.selectedCalendars.size;

            if (selectedCount === 0) {
                buttonText.textContent = 'No Calendars';
            } else if (selectedCount === calendars.length) {
                buttonText.textContent = 'All Calendars';
            } else if (selectedCount === 1) {
                const selectedId = Array.from(this.selectedCalendars)[0];
                const calendar = calendars.find(cal => cal.id === selectedId);
                buttonText.textContent = calendar ? calendar.name : 'Calendars (1)';
            } else {
                buttonText.textContent = `Calendars (${selectedCount})`;
            }
        }

        /**
         * Initialize Jump to Date functionality
         */
        initializeJumpToDate(input) {
            // Helper: format Date -> YYYY-MM-DD (local)
            const fmt = (d) => {
                const pad = (n) => String(n).padStart(2, '0');
                return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
            };

            // Pick initial date from URL (?date=YYYY-MM-DD) or today
            const params = new URLSearchParams(window.location.search);
            const urlDate = params.get('date');
            const initialDate = urlDate ? new Date(urlDate) : new Date();

            // Set input value (works for both flatpickr + native date)
            input.value = fmt(initialDate);

            // If a date was provided via URL, navigate calendar there
            if (urlDate) {
                try {
                    this.calendar.gotoDate(initialDate);
                } catch (e) {
                    console.warn('Failed to navigate to URL date:', e);
                }
            }

            // If Flatpickr is available, use it; else fall back to native date
            if (window.flatpickr) {
                flatpickr(input, {
                    dateFormat: 'Y-m-d',
                    allowInput: true,
                    defaultDate: input.value,
                    onChange: function (selectedDates) {
                        const d = selectedDates?.[0];
                        if (!d) return;
                        this.calendar.gotoDate(d);

                        // update URL param without reloading
                        const sp = new URLSearchParams(window.location.search);
                        sp.set('date', fmt(d));
                        history.replaceState({}, '', `${location.pathname}?${sp.toString()}`);
                    }.bind(this)
                });
            } else {
                // Native <input type="date"> fallback
                input.type = 'date';
                input.addEventListener('change', (e) => {
                    const val = e.target.value; // YYYY-MM-DD
                    if (!val) return;
                    const d = new Date(val);
                    this.calendar.gotoDate(d);

                    const sp = new URLSearchParams(window.location.search);
                    sp.set('date', val);
                    history.replaceState({}, '', `${location.pathname}?${sp.toString()}`);
                });
            }

            // Keep picker synced when navigating via calendar arrows
            // (listen to FullCalendar's datesSet)
            this.calendar.on('datesSet', (info) => {
                // Use the current date in view (center)
                const center = info.view.currentStart; // for month view: first visible day
                // Use activeDate if you track it; otherwise use currentStart
                input.value = fmt(center);
            });
        }

        /**
         * Initialize the moved calendar dropdown functionality
         */
        initializeMovedCalendarDropdown(dropdown) {
            // Store reference for event handling
            this.calendarFilter = dropdown;
            dropdown.addEventListener('change', this.handleFilterChange.bind(this));

            // Set initial value from saved filters
            if (this.currentFilters.calendar) {
                dropdown.value = this.currentFilters.calendar;
            }
        }

        /**
         * Initialize the moved status dropdown functionality
         */
        initializeMovedStatusDropdown(dropdown) {
            // Store reference for event handling
            this.statusFilter = dropdown;
            dropdown.addEventListener('change', this.handleFilterChange.bind(this));

            // Set initial value from saved filters
            if (this.currentFilters.status) {
                dropdown.value = this.currentFilters.status;
            }
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

            // Enable scrolling within day cells
            this.enableDayCellScrolling();
        }

        /**
         * Enable scrolling within day event containers
         */
        enableDayCellScrolling() {
            const calendarEl = this.calendarEl;
            if (!calendarEl) return;

            // Wheel/scroll navigation for weeks
            let wheelTimeout = null;
            calendarEl.addEventListener('wheel', (e) => {
                // Check if we're scrolling inside a day events container
                const dayEventsContainer = e.target.closest('.fc-daygrid-day-events');

                if (dayEventsContainer) {
                    // Check if the container can actually scroll
                    const canScroll = dayEventsContainer.scrollHeight > dayEventsContainer.clientHeight;

                    if (canScroll) {
                        // We're inside a scrollable day events container - allow normal scrolling
                        e.stopPropagation();
                        // Don't preventDefault - let browser handle the scroll
                        return;
                    }
                }

                // Navigate weeks with scroll wheel
                e.preventDefault();

                // Debounce the wheel events to prevent too-fast navigation
                if (wheelTimeout) return;

                wheelTimeout = setTimeout(() => {
                    wheelTimeout = null;
                }, 150);

                // Get current date from calendar
                const currentDate = this.calendar.getDate();

                // Calculate new date (scroll down = next week, scroll up = prev week)
                const newDate = new Date(currentDate);
                if (e.deltaY > 0) {
                    // Scroll down - next week
                    newDate.setDate(newDate.getDate() + 7);
                } else {
                    // Scroll up - previous week
                    newDate.setDate(newDate.getDate() - 7);
                }

                // Navigate to new date
                this.calendar.gotoDate(newDate);
                this.saveCurrentDate();
            }, { passive: false });
        }

        /**
         * Fetch events from the server
         * Hardened to handle empty/non-JSON responses gracefully
         */
        fetchEvents(info, successCallback, failureCallback) {
            this.showLoading();

            // Build params with selected calendars
            const params = new URLSearchParams({
                start: info.startStr,
                end: info.endStr
            });

            // Add selected calendars as comma-separated string
            if (this.selectedCalendars && this.selectedCalendars.size > 0) {
                const calendarIds = Array.from(this.selectedCalendars).join(',');
                params.append('calendar', calendarIds);
            }

            // Add other filters
            if (this.currentFilters.status) {
                params.append('status', this.currentFilters.status);
            }
            if (this.currentFilters.search) {
                params.append('search', this.currentFilters.search);
            }

            // Use the correct API endpoint from calendarConfig
            const apiUrl = window.calendarConfig?.eventsUrl || '/api/job-calendar-data/';

            // Add cache-busting parameter
            params.append('_t', Date.now());

            const fullUrl = `${apiUrl}?${params}`;

            fetch(fullUrl, {
                headers: {
                    'Accept': 'application/json'
                }
            })
                .then(async (response) => {
                    // Read response as text first to handle empty/non-JSON safely
                    const text = await response.text();
                    const contentType = response.headers.get('content-type') || '';

                    // Check for non-OK status
                    if (!response.ok) {
                        const snippet = text.substring(0, 200);
                        console.error(`JobCalendar: HTTP ${response.status} from ${fullUrl}`);
                        console.error(`  Content-Type: ${contentType}`);
                        console.error(`  Body snippet: ${snippet}`);
                        throw new Error(`Server returned HTTP ${response.status}`);
                    }

                    // Check for empty body
                    if (!text || text.trim() === '') {
                        console.error(`JobCalendar: Empty response from ${fullUrl}`);
                        console.error(`  Content-Type: ${contentType}`);
                        // Return empty events rather than failing
                        return { status: 'success', events: [] };
                    }

                    // Try to parse JSON
                    try {
                        return JSON.parse(text);
                    } catch (parseError) {
                        const snippet = text.substring(0, 200);
                        console.error(`JobCalendar: JSON parse failed for ${fullUrl}`);
                        console.error(`  Content-Type: ${contentType}`);
                        console.error(`  Body snippet: ${snippet}`);
                        console.error(`  Parse error: ${parseError.message}`);
                        throw new Error('Invalid JSON response from server');
                    }
                })
                .then(data => {
                    if (data.status === 'success') {
                        successCallback(data.events || []);
                    } else {
                        console.error('JobCalendar: API error', data.error);
                        failureCallback(data.error || 'Unknown API error');
                    }
                })
                .catch(error => {
                    console.error('JobCalendar: Fetch failed', error);
                    // Return empty events so calendar doesn't break completely
                    successCallback([]);
                })
                .finally(() => {
                    this.hideLoading();
                });
        }

        /**
         * Debounced refetch - prevents rapid successive refetch calls
         * Use this instead of direct calendar.refetchEvents() for filter changes
         */
        debouncedRefetch() {
            if (this.refetchDebounceTimer) {
                clearTimeout(this.refetchDebounceTimer);
            }
            this.refetchDebounceTimer = setTimeout(() => {
                this.refetchDebounceTimer = null;
                if (this.calendar) {
                    this.calendar.refetchEvents();
                }
            }, this.refetchDebounceMs);
        }

        /**
         * Load saved filters from localStorage
         */
        loadSavedFilters() {
            try {
                // First, check if there are URL parameters (from direct links or browser back/forward)
                const urlParams = new URLSearchParams(window.location.search);
                const urlCalendar = urlParams.get('calendar') || '';
                const urlStatus = urlParams.get('status') || '';
                const urlSearch = urlParams.get('search') || '';

                // If URL has parameters, use them (they take priority)
                if (urlCalendar || urlStatus || urlSearch) {
                    this.currentFilters.calendar = urlCalendar;
                    this.currentFilters.status = urlStatus;
                    this.currentFilters.search = urlSearch;
                } else {
                    // Otherwise, load from localStorage
                    const savedFilters = localStorage.getItem('gts-calendar-filters');
                    if (savedFilters) {
                        const filters = JSON.parse(savedFilters);
                        this.currentFilters.calendar = filters.calendar || '';
                        this.currentFilters.status = filters.status || '';
                        this.currentFilters.search = filters.search || '';
                    }
                }
            } catch (error) {
                console.warn('JobCalendar: Error loading saved filters', error);
            }
        }

        /**
         * Initialize selected calendars from localStorage
         * This must happen BEFORE the calendar is rendered to ensure
         * the first event fetch includes the proper calendar filter
         */
        initializeSelectedCalendars() {
            let selectedCalendars = [];

            // Load selected calendars from storage
            try {
                const saved = localStorage.getItem('gts-selected-calendars');
                if (saved) {
                    selectedCalendars = JSON.parse(saved);
                }
            } catch (error) {
                console.warn('Error loading saved calendar selection:', error);
            }

            // If nothing saved, default to all calendars selected
            const calendars = window.calendarConfig?.calendars || [];
            if (selectedCalendars.length === 0 && calendars.length > 0) {
                selectedCalendars = calendars.map(cal => cal.id);
            }

            // Store selected calendars
            this.selectedCalendars = new Set(selectedCalendars);

            // Load default calendar from storage
            let defaultCalendar = null;
            try {
                const saved = localStorage.getItem('gts-default-calendar');
                if (saved) {
                    defaultCalendar = parseInt(saved);
                }
            } catch (error) {
                console.warn('Error loading default calendar:', error);
            }

            this.defaultCalendar = defaultCalendar;
        }

        /**
         * Save current filters to localStorage
         */
        saveFilters() {
            try {
                const filtersToSave = {
                    calendar: this.currentFilters.calendar,
                    status: this.currentFilters.status,
                    search: this.currentFilters.search
                };
                localStorage.setItem('gts-calendar-filters', JSON.stringify(filtersToSave));
            } catch (error) {
                console.warn('JobCalendar: Error saving filters', error);
            }
        }

        /**
         * Update URL parameters to reflect current filter state
         */
        updateURLParams() {
            try {
                const url = new URL(window.location);
                const params = url.searchParams;

                // Update or remove filter parameters
                if (this.currentFilters.calendar) {
                    params.set('calendar', this.currentFilters.calendar);
                } else {
                    params.delete('calendar');
                }

                if (this.currentFilters.status) {
                    params.set('status', this.currentFilters.status);
                } else {
                    params.delete('status');
                }

                if (this.currentFilters.search) {
                    params.set('search', this.currentFilters.search);
                } else {
                    params.delete('search');
                }

                // Update URL without page reload
                const newURL = url.pathname + (params.toString() ? '?' + params.toString() : '');
                window.history.replaceState({}, '', newURL);
            } catch (error) {
                console.warn('JobCalendar: Error updating URL params', error);
            }
        }

        /**
         * Clear all filters
         */
        clearFilters() {
            this.currentFilters.calendar = '';
            this.currentFilters.status = '';
            this.currentFilters.search = '';

            // Update dropdowns
            if (this.calendarFilter) {
                this.calendarFilter.value = '';
            }
            if (this.statusFilter) {
                this.statusFilter.value = '';
            }
            if (this.searchFilter) {
                this.searchFilter.value = '';
            }

            // Save and update URL
            this.saveFilters();
            this.updateURLParams();
            this.refreshCalendar();
        }

        /**
         * Handle filter changes
         */
        handleFilterChange() {
            this.currentFilters.calendar = this.calendarFilter?.value || '';
            this.currentFilters.status = this.statusFilter?.value || '';
            this.currentFilters.search = this.searchFilter?.value || '';

            // Save filters and update URL
            this.saveFilters();
            this.updateURLParams();

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
         * Show event tooltip for any event
         */
        showEventTooltip(event, targetElement) {
            const props = event.extendedProps || {};

            // Create tooltip if it doesn't exist
            let tooltip = document.getElementById('event-tooltip');
            if (!tooltip) {
                tooltip = document.createElement('div');
                tooltip.id = 'event-tooltip';
                tooltip.style.cssText = `
                    position: fixed;
                    z-index: 10000;
                    background: white;
                    border: 1px solid #d1d5db;
                    border-radius: 8px;
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                    padding: 12px;
                    min-width: 250px;
                    max-width: 350px;
                    font-size: 13px;
                    pointer-events: none;
                    display: none;
                `;
                document.body.appendChild(tooltip);
            }

            // Format dates
            const formatDate = (date) => {
                if (!date) return 'N/A';
                return this.calendar.formatDate(date, {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                    hour: event.allDay ? undefined : 'numeric',
                    minute: event.allDay ? undefined : '2-digit',
                    meridiem: event.allDay ? undefined : 'short'
                });
            };

            // For multi-day events, use the full job date range instead of the split day
            let startDate, endDate;
            if (props.is_multi_day && props.job_start_date && props.job_end_date) {
                // Use the full job date range
                // Append T12:00:00 to ensure local parsing without timezone shift
                const jobStartDate = new Date(props.job_start_date + 'T12:00:00');
                const jobEndDate = new Date(props.job_end_date + 'T12:00:00');
                startDate = formatDate(jobStartDate);
                endDate = formatDate(jobEndDate);
            } else {
                // Use the event's own dates
                startDate = formatDate(event.start);
                endDate = formatDate(event.end || event.start);
            }

            // Build tooltip content
            let content = `
                <div style="border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-bottom: 8px;">
                    <div style="font-weight: 600; font-size: 14px; color: #111827; margin-bottom: 4px;">
                        ${event.title || '(No Title)'}
                    </div>
                    <div style="font-size: 11px; color: #6b7280;">
                        ${props.calendar_name || 'Calendar'}
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 6px;">
            `;

            // Date/Time
            if (event.allDay || (props.is_multi_day && props.job_start_date)) {
                // For all-day and multi-day events, show date range
                const isSingleDay = startDate === endDate;
                const dateRange = isSingleDay ? startDate : `${startDate} - ${endDate}`;

                content += `
                    <div style="display: flex; align-items: start;">
                        <svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"></path>
                        </svg>
                        <div style="flex: 1;">
                            <div style="color: #374151; font-weight: 500;">All Day</div>
                            <div style="color: #6b7280; font-size: 12px;">${dateRange}</div>
                        </div>
                    </div>
                `;
            } else {
                content += `
                    <div style="display: flex; align-items: start;">
                        <svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path>
                        </svg>
                        <div style="flex: 1;">
                            <div style="color: #374151; font-weight: 500;">${startDate}</div>
                            ${endDate !== startDate ? `<div style="color: #6b7280; font-size: 12px;">to ${endDate}</div>` : ''}
                        </div>
                    </div>
                `;
            }

            // Business/Contact
            if (props.business_name) {
                content += `
                    <div style="display: flex; align-items: start;">
                        <svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                        </svg>
                        <div style="flex: 1; color: #374151;">
                            ${props.business_name}
                            ${props.contact_name ? `<div style="color: #6b7280; font-size: 12px;">${props.contact_name}</div>` : ''}
                        </div>
                    </div>
                `;
            }

            // Phone
            if (props.phone) {
                content += `
                    <div style="display: flex; align-items: start;">
                        <svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"></path>
                        </svg>
                        <div style="flex: 1; color: #374151;">${props.phone}</div>
                    </div>
                `;
            }

            // Trailer Information
            if (props.trailer_details || props.trailer_color || props.trailer_serial) {
                content += `
                    <div style="display: flex; align-items: start;">
                        <svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"></path>
                            <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1V8a1 1 0 00-1-1h-3z"></path>
                        </svg>
                        <div style="flex: 1; color: #374151;">
                            ${props.trailer_details ? `<div style="font-weight: 500;">Trailer: ${props.trailer_details.length > 80 ? props.trailer_details.substring(0, 80) + '...' : props.trailer_details}</div>` : ''}
                            ${props.trailer_color ? `<div style="color: #6b7280; font-size: 12px; margin-top: 2px;">Color: ${props.trailer_color}</div>` : ''}
                            ${props.trailer_serial ? `<div style="color: #6b7280; font-size: 12px; margin-top: 2px;">Serial: ${props.trailer_serial}</div>` : ''}
                        </div>
                    </div>
                `;
            }

            // Repair Notes
            if (props.repair_notes) {
                const truncatedRepairNotes = props.repair_notes.length > 100 ? props.repair_notes.substring(0, 100) + '...' : props.repair_notes;
                content += `
                    <div style="display: flex; align-items: start;">
                        <svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z"></path>
                        </svg>
                        <div style="flex: 1; color: #374151;">
                            <div style="font-weight: 500; font-size: 12px; margin-bottom: 2px;">Repair Notes</div>
                            <div style="color: #6b7280; font-size: 12px;">${truncatedRepairNotes}</div>
                        </div>
                    </div>
                `;
            }

            // Status
            if (props.status) {
                const statusColors = {
                    'pending': '#fbbf24',
                    'confirmed': '#3b82f6',
                    'in_progress': '#f97316',
                    'completed': '#10b981',
                    'cancelled': '#ef4444',
                    'uncompleted': '#6b7280'
                };
                const statusColor = statusColors[props.status] || '#6b7280';
                const statusText = props.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());

                content += `
                    <div style="display: flex; align-items: start;">
                        <svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                        </svg>
                        <div style="flex: 1;">
                            <span style="display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; background-color: ${statusColor}20; color: ${statusColor};">
                                ${statusText}
                            </span>
                        </div>
                    </div>
                `;
            }

            // Notes
            if (props.notes) {
                const truncatedNotes = props.notes.length > 100 ? props.notes.substring(0, 100) + '...' : props.notes;
                content += `
                    <div style="display: flex; align-items: start;">
                        <svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"></path>
                        </svg>
                        <div style="flex: 1; color: #6b7280; font-size: 12px;">${truncatedNotes}</div>
                    </div>
                `;
            }

            // Recurring indicator
            if (props.is_recurring_parent || props.is_recurring_instance) {
                content += `
                    <div style="display: flex; align-items: start;">
                        <svg style="width: 14px; height: 14px; margin-right: 8px; margin-top: 2px; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"></path>
                        </svg>
                        <div style="flex: 1; color: #6b7280; font-size: 12px;">Recurring Event</div>
                    </div>
                `;
            }

            content += `</div>`;

            tooltip.innerHTML = content;
            tooltip.style.display = 'block';

            // Position tooltip near the event
            const rect = targetElement.getBoundingClientRect();
            const tooltipRect = tooltip.getBoundingClientRect();

            const margin = 10; // Margin from edges and target element
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;

            let left = rect.right + margin;
            let top = rect.top;

            // Adjust horizontal position if tooltip goes off right edge
            if (left + tooltipRect.width > viewportWidth - margin) {
                // Try positioning to the left of the target
                left = rect.left - tooltipRect.width - margin;

                // If it still goes off the left edge, clamp it to the viewport
                if (left < margin) {
                    left = margin;
                }
            }

            // Ensure tooltip doesn't go off left edge (in case target is very close to left side)
            if (left < margin) {
                left = margin;
            }

            // Ensure tooltip doesn't go off right edge (in case it's still too wide)
            if (left + tooltipRect.width > viewportWidth - margin) {
                left = viewportWidth - tooltipRect.width - margin;
            }

            // Adjust vertical position if tooltip goes off bottom edge
            if (top + tooltipRect.height > viewportHeight - margin) {
                // Position tooltip above the bottom edge
                top = viewportHeight - tooltipRect.height - margin;
            }

            // Adjust if tooltip goes off top edge
            if (top < margin) {
                top = margin;
            }

            tooltip.style.left = left + 'px';
            tooltip.style.top = top + 'px';
        }

        /**
         * Hide event tooltip
         */
        hideEventTooltip() {
            const tooltip = document.getElementById('event-tooltip');
            if (tooltip) {
                tooltip.style.display = 'none';
            }
        }

        /**
         * Show tooltip for a job row in the search results table.
         * Fetches job details from the API and reuses the calendar tooltip renderer.
         */
        async showJobRowTooltip(rowElement) {
            const jobId = rowElement?.getAttribute?.('data-job-id');
            if (!jobId) return;

            try {
                const response = await fetch(`/api/jobs/${jobId}/detail/`);
                if (!response.ok) return;

                const jobData = await response.json();

                const fakeEvent = {
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

                this.showEventTooltip(fakeEvent, rowElement);
            } catch (error) {
                console.error('Error showing job row tooltip:', error);
            }
        }

        /**
         * Handle event mouse enter for tooltip
         */
        handleEventMouseEnter(info) {
            // Clear any existing timeout
            if (this.tooltipTimeout) {
                clearTimeout(this.tooltipTimeout);
            }

            // Set a 500ms delay before showing the tooltip
            this.tooltipTimeout = setTimeout(() => {
                this.showEventTooltip(info.event, info.el);
                this.tooltipTimeout = null;
            }, 500);
        }

        /**
         * Handle event mouse leave to hide tooltip
         */
        handleEventMouseLeave(info) {
            // Clear the timeout if user stops hovering before delay completes
            if (this.tooltipTimeout) {
                clearTimeout(this.tooltipTimeout);
                this.tooltipTimeout = null;
            }

            // Hide the tooltip if it's already showing
            this.hideEventTooltip();
        }

        /**
         * Handle event click to open edit form
         */
        handleEventClick(info) {
            try {
                const extendedProps = info.event.extendedProps || {};
                const eventType = extendedProps.type;
                const jobId = extendedProps.job_id;

                // Check if this is a call reminder event (job-related or standalone)
                if (eventType === 'call_reminder' || eventType === 'standalone_call_reminder') {
                    this.showCallReminderPanel(info.event);
                } else if (jobId && window.JobPanel) {
                    // Check if there are unsaved changes
                    const hasChanges = window.JobPanel.hasUnsavedChanges && window.JobPanel.hasUnsavedChanges();
                    console.log('Has unsaved changes:', hasChanges);
                    if (hasChanges) {
                        console.log('Auto-saving before switching jobs...');
                        // Set flag to prevent panel from auto-closing
                        window.JobPanel.isSwitchingJobs = true;
                        // Save the form first
                        window.JobPanel.saveForm(() => {
                            console.log('Save complete, adding to workspace...');
                            // After saving, add to workspace if it has a job ID
                            const currentJobId = window.JobPanel.currentJobId;
                            console.log('Current job ID after save:', currentJobId);
                            if (currentJobId && window.JobWorkspace && !window.JobWorkspace.hasJob(currentJobId)) {
                                // Get job details from the form
                                const form = document.querySelector('#job-panel .panel-body form');
                                const businessName = form?.querySelector('input[name="business_name"]')?.value ||
                                    form?.querySelector('input[name="contact_name"]')?.value ||
                                    'Unnamed Job';
                                const trailerColor = form?.querySelector('input[name="trailer_color"]')?.value || '';

                                console.log('Adding job to workspace (minimized):', currentJobId, businessName);
                                // Add to workspace as minimized (don't make it active)
                                window.JobWorkspace.addJobMinimized(currentJobId, {
                                    customerName: businessName,
                                    trailerColor: trailerColor,
                                    calendarColor: '#3B82F6'
                                });
                            }

                            // Now open the new job
                            console.log('Opening clicked job:', jobId);
                            if (window.JobWorkspace) {
                                // Check if the clicked job is already in the workspace
                                if (window.JobWorkspace.hasJob(jobId)) {
                                    // Job is in workspace, switch to it
                                    window.JobWorkspace.switchToJob(jobId);
                                } else {
                                    // Job is not in workspace, open it fresh
                                    const props = info.event.extendedProps;
                                    window.JobWorkspace.openJob(jobId, {
                                        customerName: props.business_name || props.contact_name || 'Job',
                                        trailerColor: props.trailer_color || '',
                                        calendarColor: props.calendar_color || '#3B82F6'
                                    });
                                }
                            } else {
                                // Fallback to direct panel opening if workspace not available
                                this.openJobInPanel(info.event, jobId);
                            }

                            // Clear the switching flag after a delay to allow new form to load
                            setTimeout(() => {
                                window.JobPanel.isSwitchingJobs = false;
                            }, 500);
                        });
                    } else {
                        // No unsaved changes, open directly
                        console.log('Opening clicked job:', jobId);
                        if (window.JobWorkspace) {
                            // Check if the clicked job is already in the workspace
                            if (window.JobWorkspace.hasJob(jobId)) {
                                // Job is in workspace, switch to it
                                window.JobWorkspace.switchToJob(jobId);
                            } else {
                                // Job is not in workspace, open it fresh
                                const props = info.event.extendedProps;
                                window.JobWorkspace.openJob(jobId, {
                                    customerName: props.business_name || props.contact_name || 'Job',
                                    trailerColor: props.trailer_color || '',
                                    calendarColor: props.calendar_color || '#3B82F6'
                                });
                            }
                        } else {
                            // Fallback to direct panel opening if workspace not available
                            this.openJobInPanel(info.event, jobId);
                        }
                    }
                } else {
                    console.error('JobPanel not available or job ID missing');
                    this.showError('Unable to open event for editing. Please try again.');
                }
            } catch (error) {
                console.error('JobCalendar: Error handling single click', error);
                this.showError('Unable to open event for editing. Please try again.');
            }
        }

        /**
         * Open a job in the panel
         */
        openJobInPanel(event, jobId) {
            console.log('openJobInPanel called for job:', jobId);
            const props = event.extendedProps;

            // Load job edit form in panel
            console.log('Loading job form for:', jobId);
            window.JobPanel.setTitle('Edit Job');
            window.JobPanel.load(`/jobs/new/partial/?edit=${jobId}`);

            // Track current job ID for workspace integration
            if (window.JobPanel.setCurrentJobId) {
                window.JobPanel.setCurrentJobId(jobId);
            }

            // Update minimize button after a short delay to ensure panel is ready
            setTimeout(() => {
                if (window.JobPanel.updateMinimizeButton) {
                    window.JobPanel.updateMinimizeButton();
                }
            }, 100);
        }

        /**
         * Show dialog for unsaved changes with options to save, minimize, or cancel
         */
        showUnsavedChangesDialog(onProceed) {
            const overlay = document.createElement('div');
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                animation: fadeIn 0.2s ease;
            `;

            const dialog = document.createElement('div');
            dialog.style.cssText = `
                background: white;
                border-radius: 12px;
                padding: 24px;
                max-width: 480px;
                width: 90%;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                animation: slideUp 0.2s ease;
            `;

            dialog.innerHTML = `
                <div style="display: flex; align-items: start; margin-bottom: 16px;">
                    <svg style="width: 24px; height: 24px; color: #f59e0b; margin-right: 12px; flex-shrink: 0;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                    </svg>
                    <div>
                        <h3 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 600; color: #111827;">Unsaved Changes</h3>
                        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">You have unsaved changes. What would you like to do?</p>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <button id="dialog-save-btn" style="width: 100%; padding: 10px 16px; background: #3b82f6; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;">
                        Save and Open New Job
                    </button>
                    <button id="dialog-minimize-btn" style="width: 100%; padding: 10px 16px; background: #f3f4f6; color: #374151; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;">
                        Minimize to Workspace
                    </button>
                    <button id="dialog-discard-btn" style="width: 100%; padding: 10px 16px; background: #fee2e2; color: #dc2626; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;">
                        Discard Changes
                    </button>
                    <button id="dialog-cancel-btn" style="width: 100%; padding: 10px 16px; background: white; color: #6b7280; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                        Cancel
                    </button>
                </div>
            `;

            // Add animations
            const style = document.createElement('style');
            style.textContent = `
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideUp {
                    from { transform: translateY(20px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);

            overlay.appendChild(dialog);
            document.body.appendChild(overlay);

            // Button hover effects
            const saveBtn = dialog.querySelector('#dialog-save-btn');
            const minimizeBtn = dialog.querySelector('#dialog-minimize-btn');
            const discardBtn = dialog.querySelector('#dialog-discard-btn');
            const cancelBtn = dialog.querySelector('#dialog-cancel-btn');

            saveBtn.addEventListener('mouseenter', () => saveBtn.style.background = '#2563eb');
            saveBtn.addEventListener('mouseleave', () => saveBtn.style.background = '#3b82f6');

            minimizeBtn.addEventListener('mouseenter', () => minimizeBtn.style.background = '#e5e7eb');
            minimizeBtn.addEventListener('mouseleave', () => minimizeBtn.style.background = '#f3f4f6');

            discardBtn.addEventListener('mouseenter', () => discardBtn.style.background = '#fecaca');
            discardBtn.addEventListener('mouseleave', () => discardBtn.style.background = '#fee2e2');

            cancelBtn.addEventListener('mouseenter', () => {
                cancelBtn.style.background = '#f9fafb';
                cancelBtn.style.borderColor = '#9ca3af';
            });
            cancelBtn.addEventListener('mouseleave', () => {
                cancelBtn.style.background = 'white';
                cancelBtn.style.borderColor = '#d1d5db';
            });

            // Close dialog function
            const closeDialog = () => {
                overlay.remove();
                style.remove();
            };

            // Save and proceed
            saveBtn.addEventListener('click', () => {
                if (window.JobPanel.saveForm) {
                    window.JobPanel.saveForm(() => {
                        closeDialog();
                        onProceed();
                    });
                } else {
                    closeDialog();
                    onProceed();
                }
            });

            // Minimize to workspace
            minimizeBtn.addEventListener('click', () => {
                const currentJobId = window.JobPanel.currentJobId;
                if (currentJobId && window.JobWorkspace) {
                    // Save first if there are changes
                    if (window.JobPanel.saveForm) {
                        window.JobPanel.saveForm(() => {
                            window.JobWorkspace.minimizeJob(currentJobId);
                            closeDialog();
                            onProceed();
                        });
                    } else {
                        window.JobWorkspace.minimizeJob(currentJobId);
                        closeDialog();
                        onProceed();
                    }
                } else {
                    // No workspace, just close and proceed
                    closeDialog();
                    onProceed();
                }
            });

            // Discard changes and proceed
            discardBtn.addEventListener('click', () => {
                closeDialog();
                onProceed();
            });

            // Cancel - don't open new job
            cancelBtn.addEventListener('click', closeDialog);

            // ESC key to cancel
            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    closeDialog();
                    document.removeEventListener('keydown', escHandler);
                }
            };
            document.addEventListener('keydown', escHandler);

            // Click overlay to cancel
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    closeDialog();
                }
            });
        }

        /**
         * Show call reminder panel with options
         */
        showCallReminderPanel(event) {
            const props = event.extendedProps;
            const isStandalone = props.type === 'standalone_call_reminder';
            const jobId = props.job_id;
            const reminderId = props.reminder_id;

            let html = `<div style="padding: 8px;">`;

            // Header
            html += `
                <div style="margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <div style="width: 32px; height: 32px; background-color: ${event.backgroundColor}; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px;">
                            📞
                        </div>
                        <div style="flex: 1;">
                            <h3 style="margin: 0; font-size: 14px; font-weight: 600; color: #111827;">Call Reminder</h3>`;

            if (!isStandalone && props.weeks_prior) {
                const weeksText = props.weeks_prior === 2 ? '1 week' : '2 weeks';
                html += `<p style="margin: 2px 0 0 0; font-size: 12px; color: #6b7280;">${weeksText} before job</p>`;
            } else if (props.reminder_date) {
                html += `<p style="margin: 2px 0 0 0; font-size: 12px; color: #6b7280;">${props.reminder_date}</p>`;
            }

            html += `</div></div>`;

            // Job details (only for job-related reminders)
            if (!isStandalone && jobId) {
                const jobDate = new Date(props.job_date);
                const formattedDate = this.calendar.formatDate(jobDate, {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric'
                });

                html += `
                    <div style="background-color: #f9fafb; border-radius: 6px; padding: 8px; margin-bottom: 8px;">
                        <div style="margin-bottom: 6px;">
                            <div style="font-weight: 600; color: #374151; margin-bottom: 2px; font-size: 12px;">Job Details</div>
                            <div style="color: #6b7280; font-size: 12px;">
                                <strong style="color: #111827;">${props.business_name || 'No business name'}</strong>
                                ${props.contact_name ? `<br>${props.contact_name}` : ''}
                                ${props.phone ? `<br>📱 ${props.phone}` : ''}
                            </div>
                        </div>
                        <div style="padding-top: 6px; border-top: 1px solid #e5e7eb;">
                            <div style="font-weight: 600; color: #374151; margin-bottom: 2px; font-size: 12px;">Job Date</div>
                            <div style="color: #6b7280; font-size: 12px;">${formattedDate}</div>
                        </div>
                    </div>`;
            }

            // Notes section
            html += `
                <div style="margin-bottom: 8px;">
                    <label style="font-weight: 600; color: #374151; margin-bottom: 4px; display: block; font-size: 12px;">
                        Notes
                    </label>
                    <textarea id="reminder-notes" 
                              style="width: 100%; min-height: 60px; padding: 4px 8px; border: 1px solid #d1d5db; border-radius: 6px; font-family: inherit; font-size: 12px; resize: vertical;"
                              placeholder="Add notes about this call reminder...">${props.notes || ''}</textarea>
                </div>
                </div>`;

            // Action buttons
            html += `<div style="display: flex; gap: 4px; justify-content: center;">`;

            if (isStandalone && reminderId) {
                // Standalone reminder buttons
                html += `
                    <button onclick="jobCalendar.saveStandaloneReminderNotes(${reminderId})" 
                            style="flex: 1; padding: 6px 12px; background-color: #3b82f6; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;"
                            onmouseover="this.style.backgroundColor='#2563eb'" 
                            onmouseout="this.style.backgroundColor='#3b82f6'">
                        💾 Save & Close
                    </button>
                    <button onclick="jobCalendar.markStandaloneReminderComplete(${reminderId})" 
                            style="flex: 1; padding: 6px 12px; background-color: #10b981; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;"
                            onmouseover="this.style.backgroundColor='#059669'" 
                            onmouseout="this.style.backgroundColor='#10b981'">
                        ✓ Complete
                    </button>
                    <button onclick="jobCalendar.deleteStandaloneReminder(${reminderId})" 
                            style="padding: 6px 12px; background-color: #ef4444; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;"
                            onmouseover="this.style.backgroundColor='#dc2626'" 
                            onmouseout="this.style.backgroundColor='#ef4444'">
                        🗑️
                    </button>`;
            } else if (jobId) {
                // Job-related reminder buttons
                html += `
                    <button onclick="jobCalendar.saveJobReminderNotes(${jobId})" 
                            style="flex: 1; padding: 6px 12px; background-color: #3b82f6; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;"
                            onmouseover="this.style.backgroundColor='#2563eb'" 
                            onmouseout="this.style.backgroundColor='#3b82f6'">
                        💾 Save & Close
                    </button>
                    <button onclick="jobCalendar.markCallReminderComplete(${jobId})" 
                            style="flex: 1; padding: 6px 12px; background-color: #10b981; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;"
                            onmouseover="this.style.backgroundColor='#059669'" 
                            onmouseout="this.style.backgroundColor='#10b981'">
                        ✓ Mark Complete
                    </button>
                    <button onclick="jobCalendar.openJobFromReminder(${jobId})" 
                            style="flex: 1; padding: 6px 12px; background-color: #6b7280; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;"
                            onmouseover="this.style.backgroundColor='#4b5563'" 
                            onmouseout="this.style.backgroundColor='#6b7280'">
                        View Job
                    </button>`;
            }

            html += `</div></div>`;

            if (window.JobPanel) {
                window.JobPanel.setTitle('📞 Call Reminder');
                window.JobPanel.showContent(html);
            }
        }

        /**
         * Mark call reminder as complete
         */
        async markCallReminderComplete(jobId) {
            try {
                const response = await fetch(`/api/jobs/${jobId}/mark-call-reminder-complete/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });

                if (response.ok) {
                    // Close the panel
                    if (window.JobPanel) {
                        window.JobPanel.close();
                    }

                    // Refresh calendar to remove the reminder
                    this.calendar.refetchEvents();

                    // Show success message
                    this.showSuccess('Call reminder marked as complete');
                } else {
                    const data = await response.json();
                    this.showError(data.error || 'Failed to mark reminder as complete');
                }
            } catch (error) {
                console.error('Error marking call reminder complete:', error);
                this.showError('Failed to mark reminder as complete');
            }
        }

        /**
         * Save notes for job-related call reminder and close the dialog
         */
        async saveJobReminderNotes(jobId) {
            const notes = document.getElementById('reminder-notes')?.value || '';

            try {
                const response = await fetch(`/jobs/${jobId}/call-reminder/update/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({
                        notes: notes
                    })
                });

                if (response.ok) {
                    // Clear unsaved changes flag before closing
                    if (window.JobPanel && window.JobPanel.clearUnsavedChanges) {
                        window.JobPanel.clearUnsavedChanges();
                    }

                    // Close the panel (skip unsaved check since we just saved)
                    if (window.JobPanel) {
                        window.JobPanel.close(true);
                    }

                    // Refresh calendar to show updated notes
                    this.calendar.refetchEvents();
                } else {
                    const data = await response.json();
                    this.showError(data.error || 'Failed to save notes');
                }
            } catch (error) {
                console.error('Error saving reminder notes:', error);
                this.showError('Failed to save notes. Please try again.');
            }
        }

        /**
         * Open the job detail/edit from a call reminder
         */
        openJobFromReminder(jobId) {
            if (window.JobPanel) {
                window.JobPanel.setTitle('Edit Job');
                window.JobPanel.load(`/jobs/new/partial/?edit=${jobId}`);
            }
        }

        /**
         * Save notes for standalone call reminder
         */
        async saveStandaloneReminderNotes(reminderId) {
            try {
                const notes = document.getElementById('reminder-notes')?.value || '';

                const response = await fetch(`/call-reminders/${reminderId}/update/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({ notes })
                });

                if (response.ok) {
                    // Clear unsaved changes flag and close panel
                    if (window.JobPanel) {
                        window.JobPanel.clearUnsavedChanges();
                        window.JobPanel.close(true);
                    }
                    // Refresh calendar to update the event
                    this.calendar.refetchEvents();
                } else {
                    const data = await response.json();
                    this.showError(data.error || 'Failed to save notes');
                }
            } catch (error) {
                console.error('Error saving reminder notes:', error);
                this.showError('Failed to save notes');
            }
        }

        /**
         * Mark standalone call reminder as complete
         */
        async markStandaloneReminderComplete(reminderId) {
            try {
                const response = await fetch(`/call-reminders/${reminderId}/update/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({ completed: true })
                });

                if (response.ok) {
                    // Close the panel
                    if (window.JobPanel) {
                        window.JobPanel.close();
                    }

                    // Refresh calendar to remove the reminder
                    this.calendar.refetchEvents();

                    // Show success message
                    this.showSuccess('Call reminder marked as complete');
                } else {
                    const data = await response.json();
                    this.showError(data.error || 'Failed to mark reminder as complete');
                }
            } catch (error) {
                console.error('Error marking reminder complete:', error);
                this.showError('Failed to mark reminder as complete');
            }
        }

        /**
         * Delete standalone call reminder
         */
        async deleteStandaloneReminder(reminderId) {
            if (!confirm('Are you sure you want to delete this call reminder?')) {
                return;
            }

            try {
                const response = await fetch(`/call-reminders/${reminderId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });

                if (response.ok) {
                    // Close the panel
                    if (window.JobPanel) {
                        window.JobPanel.close();
                    }

                    // Refresh calendar to remove the reminder
                    this.calendar.refetchEvents();

                    // Show success message
                    this.showSuccess('Call reminder deleted successfully');
                } else {
                    const data = await response.json();
                    this.showError(data.error || 'Failed to delete reminder');
                }
            } catch (error) {
                console.error('Error deleting reminder:', error);
                this.showError('Failed to delete reminder');
            }
        }

        /**
         * Handle date click with proper double-click detection
         */
        handleDateClick(info) {
            try {
                // Check if click is on or near a scrollbar (only if scrollbar is present)
                if (info.jsEvent) {
                    const dayEventsContainer = info.jsEvent.target.closest('.fc-daygrid-day-events');
                    if (dayEventsContainer) {
                        // Only check for scrollbar clicks if there's actually a scrollbar
                        const hasScrollbar = dayEventsContainer.scrollHeight > dayEventsContainer.clientHeight;

                        if (hasScrollbar) {
                            const rect = dayEventsContainer.getBoundingClientRect();
                            const clickX = info.jsEvent.clientX;
                            const rightEdge = rect.right;
                            const isScrollbarClick = (rightEdge - clickX) <= 18;

                            if (isScrollbarClick) {
                                // Click is on scrollbar - ignore it
                                return;
                            }
                        }
                    }
                }

                const currentTime = Date.now();
                const currentDate = info.date.getTime();

                // Check if this is a double-click (same date within threshold)
                if (this.lastClickDate === currentDate &&
                    this.lastClickTime &&
                    (currentTime - this.lastClickTime) < this.doubleClickThreshold) {

                    // Double click detected - clear timer
                    if (this.clickTimer) {
                        clearTimeout(this.clickTimer);
                        this.clickTimer = null;
                    }

                    // Record handled double click to prevent duplicate handling from dblclick listener
                    const dateMs = info.date.getTime();
                    this.lastOpenedDateByDoubleClick = dateMs;
                    this.lastOpenedDateTimestamp = currentTime;

                    // Open the appropriate form
                    this.openCreateFormForDate(info.date);

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
                    this.clickTimer = setTimeout(() => {
                        this.lastClickDate = null;
                        this.lastClickTime = null;
                        this.clickTimer = null;
                    }, this.doubleClickThreshold);
                }

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

            // Force apply calendar colors if they exist
            if (props?.calendar_color) {
                const calendarColor = props.calendar_color;
                const isCompleted = props.status === 'completed';

                // Apply lighter shade for completed events
                let finalColor = calendarColor;
                if (isCompleted) {
                    finalColor = this.lightenColor(calendarColor, 0.3);
                }

                // Force set the colors
                event.setProp('backgroundColor', finalColor);
                event.setProp('borderColor', finalColor);

                // Also set on the DOM element directly
                if (info.el) {
                    info.el.style.backgroundColor = finalColor;
                    info.el.style.borderColor = finalColor;
                }

                // Use setTimeout to ensure colors are applied after FullCalendar finishes
                setTimeout(() => {
                    if (info.el) {
                        info.el.style.backgroundColor = finalColor;
                        info.el.style.borderColor = finalColor;
                    }
                }, 100);
            }

            // Apply completion styling (only to DOM element, not as event property)
            if (props.is_completed || (props.completed && (props.type === 'call_reminder' || props.type === 'standalone_call_reminder'))) {
                if (info.el) {
                    info.el.style.textDecoration = 'line-through';
                    info.el.style.textDecorationColor = 'white';
                    info.el.style.color = 'white';
                    info.el.style.opacity = '0.7';
                }
            }

            // Apply canceled styling (only to DOM element, not as event property)
            if (props.is_canceled) {
                if (info.el) {
                    info.el.style.textDecoration = 'line-through';
                    info.el.style.opacity = '0.5';
                }
            }
        }

        /**
         * Lighten a hex color by a given factor (0-1)
         */
        lightenColor(hexColor, factor) {
            // Remove # if present
            hexColor = hexColor.replace('#', '');

            // Convert to RGB
            const r = parseInt(hexColor.substr(0, 2), 16);
            const g = parseInt(hexColor.substr(2, 2), 16);
            const b = parseInt(hexColor.substr(4, 2), 16);

            // Lighten by mixing with white
            const newR = Math.round(r + (255 - r) * factor);
            const newG = Math.round(g + (255 - g) * factor);
            const newB = Math.round(b + (255 - b) * factor);

            // Convert back to hex
            return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
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

            // Add strikethrough styling for completed jobs
            const isCompleted = props.status === 'completed';
            const titleClass = isCompleted ? 'job-title job-title-completed' : 'job-title';

            // Add recurring event icon
            const recurringIcon = (props.is_recurring_parent || props.is_recurring_instance)
                ? '<svg style="width: 12px; height: 12px; display: inline-block; margin-right: 4px; vertical-align: middle;" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"></path></svg>'
                : '';

            // Add multi-day indicator
            let multiDayIndicator = '';
            if (props.is_multi_day) {
                const dayNumber = props.multi_day_number + 1;  // Convert 0-indexed to 1-indexed
                const totalDays = props.multi_day_total + 1;   // Convert count to 1-indexed total
                multiDayIndicator = ` <span style="font-size: 0.85em; opacity: 0.8;">(Day ${dayNumber}/${totalDays})</span>`;
            }

            return {
                html: `
                    <div class="job-event-content">
                        <div class="${titleClass}">${recurringIcon}${event.title}${multiDayIndicator}</div>
                    </div>
                `
            };
        }

        /**
         * Render custom day cell content with month name for first 7 days
         */
        renderDayCellContent(info) {
            const dayOfMonth = info.date.getDate();

            // Only show month name for first 7 days of the month
            if (dayOfMonth >= 1 && dayOfMonth <= 7) {
                const monthName = info.date.toLocaleDateString('en-US', { month: 'short' });

                return {
                    html: `
                        <div class="fc-daygrid-day-top">
                            <a class="fc-daygrid-day-number">${dayOfMonth}</a>
                        </div>
                        <div class="fc-month-name-wrapper">
                            <span class="fc-month-name">${monthName}</span>
                        </div>
                    `
                };
            }

            // Default rendering for other days
            return {
                html: `
                    <div class="fc-daygrid-day-top">
                        <a class="fc-daygrid-day-number">${dayOfMonth}</a>
                    </div>
                `
            };
        }


        /**
         * Update job status via API
         */
        updateJobStatus(jobId, newStatus) {
            const csrfToken = this.getCSRFToken();

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
            toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white ${type === 'success' ? 'bg-green-600' :
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
            // Use the global toast system if available, otherwise use the local toast method
            if (window.layout && window.layout.showToast) {
                window.layout.showToast(message, 'success');
            } else {
                this.showToast(message, 'success');
            }
        }

        /**
         * Toggle search panel visibility
         */
        toggleSearchPanel() {
            this.searchPanelOpen = !this.searchPanelOpen;
            const searchPanel = document.getElementById('calendar-search-panel');
            const calendarShell = document.getElementById('calendar-shell');
            const searchInput = document.getElementById('calendar-search-input');
            const searchButton = document.querySelector('.fc-searchButton-button');

            if (!searchPanel || !calendarShell) {
                console.error('Search panel or calendar shell not found');
                return;
            }

            if (this.searchPanelOpen) {
                searchPanel.style.height = '50vh';
                calendarShell.style.height = 'calc(50vh - 45px)';

                // Add active class to button
                if (searchButton) {
                    searchButton.classList.add('active');
                }

                // Focus search input after transition
                setTimeout(() => {
                    if (searchInput) {
                        searchInput.focus();
                    }
                }, 350);
            } else {
                searchPanel.style.height = '0';
                calendarShell.style.height = 'calc(100vh - 45px)';

                // Remove active class from button
                if (searchButton) {
                    searchButton.classList.remove('active');
                }
            }

            // Save state to localStorage
            localStorage.setItem('gts-calendar-search-open', this.searchPanelOpen);

            // Update calendar size after transition completes
            setTimeout(() => {
                if (this.calendar) {
                    this.calendar.updateSize();
                    this.forceEqualWeekHeights();
                }
            }, 350);
        }

        /**
         * Toggle Today sidebar visibility
         */
        toggleTodaySidebar() {
            this.todaySidebarOpen = !this.todaySidebarOpen;
            this.applyTodaySidebarState();
            localStorage.setItem('gts-calendar-today-sidebar-open', this.todaySidebarOpen);

            setTimeout(() => {
                if (this.calendar) {
                    this.calendar.updateSize();
                    this.forceEqualWeekHeights();
                }
            }, 200);
        }

        /**
         * Apply Today sidebar state to DOM and button
         * @param {boolean} updateButton - whether to update the toggle button state
         */
        applyTodaySidebarState(updateButton = true) {
            const todaySidebar = document.getElementById('todaySidebar');
            if (todaySidebar) {
                todaySidebar.classList.toggle('hidden', !this.todaySidebarOpen);
            }

            if (!updateButton) return;

            const todayToggleButton = document.querySelector('.fc-todaySidebarButton-button');
            if (todayToggleButton) {
                todayToggleButton.setAttribute('aria-pressed', this.todaySidebarOpen ? 'true' : 'false');
                todayToggleButton.classList.toggle('active', this.todaySidebarOpen);
                todayToggleButton.title = this.todaySidebarOpen ? 'Hide Today column' : 'Show Today column';
            }
        }

        /**
         * Cleanup method for removing event listeners and resetting state
         */
        destroy() {
            if (this.calendar) {
                this.calendar.destroy();
            }
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.jobCalendar = new JobCalendar();
        });
    } else {
        window.jobCalendar = new JobCalendar();
    }

})();


