/**
 * Calendar Layout Module
 * 
 * Handles layout, sizing, scroll wheel navigation, and search panel toggle.
 * Registers: ensureCalendarVisible, adjustHeaderColumnWidths, scheduleUIUpdate,
 *            forceEqualWeekHeights, _applyWeekHeights, setupResizeObserver,
 *            enableDayCellScrolling, saveCurrentDate, getSavedDate, toggleSearchPanel
 */
(function() {
    'use strict';

    GTS.calendar.register('layout', function(proto) {
        /**
         * Ensure calendar content is visible
         */
        proto.ensureCalendarVisible = function() {
            // Ensure all day numbers are visible
            var dayNumbers = document.querySelectorAll('.fc-daygrid-day-number');
            dayNumbers.forEach(function(dayNumber) {
                dayNumber.style.display = 'block';
                dayNumber.style.visibility = 'visible';
                dayNumber.style.opacity = '1';
            });

            // Adjust header column widths to match content
            this.adjustHeaderColumnWidths();
        };

        /**
         * Adjust header column widths to match content columns
         */
        proto.adjustHeaderColumnWidths = function() {
            // Find the header row
            var headerRow = document.querySelector('.fc-col-header');
            if (!headerRow) return;

            // Find all header cells and make them all equal width
            var headerCells = headerRow.querySelectorAll('th');
            headerCells.forEach(function(cell) {
                // All days equal width (100% / 7 days = 14.29%)
                cell.style.width = '14.29%';
                cell.style.minWidth = '14.29%';
                cell.style.maxWidth = '14.29%';
            });
        };

        /**
         * Save current calendar date to localStorage
         */
        proto.saveCurrentDate = function() {
            if (this.calendar) {
                var currentDate = this.calendar.getDate();
                localStorage.setItem('gts-calendar-current-date', currentDate.toISOString());
            }
        };

        /**
         * Debounced UI update - consolidates repeated renderTodayPanel + forceEqualWeekHeights calls
         * into a single execution per animation frame
         */
        proto.scheduleUIUpdate = function() {
            var self = this;
            if (this.uiUpdateTimer) {
                clearTimeout(this.uiUpdateTimer);
            }
            this.uiUpdateTimer = setTimeout(function() {
                self.uiUpdateTimer = null;
                self.renderTodayPanel();
                self.forceEqualWeekHeights();
            }, this.uiUpdateDebounceMs);
        };

        /**
         * Force all week rows to have equal height (25% each)
         * OPTIMIZED: Uses single rAF instead of multiple timeouts to reduce layout thrash.
         * Called at explicit call sites: after render, toggles, and windowResize.
         */
        proto.forceEqualWeekHeights = function() {
            var self = this;
            // Skip if already scheduled
            if (this._weekHeightRafPending) return;
            this._weekHeightRafPending = true;

            requestAnimationFrame(function() {
                self._weekHeightRafPending = false;
                self._applyWeekHeights();
            });
        };

        /**
         * Internal: Apply equal heights to week rows
         * OPTIMIZED: Only writes to 4 row elements, not individual cells.
         * Uses CSS inherit on cells via stylesheet rather than inline styles.
         */
        proto._applyWeekHeights = function() {
            // Find the daygrid body
            var daygridBody = document.querySelector('.fc-daygrid-body');
            if (!daygridBody) return;

            // Get the total available height
            var totalHeight = daygridBody.offsetHeight;

            // Skip if height hasn't changed (avoid redundant style writes)
            if (this._lastDaygridHeight === totalHeight) return;
            this._lastDaygridHeight = totalHeight;

            var weekHeight = Math.floor(totalHeight / 4); // Exact pixel height for each week
            if (weekHeight <= 0) return;

            // Find all week rows
            var weekRows = document.querySelectorAll('.fc-daygrid-body table tbody tr');
            if (weekRows.length !== 4) return;

            // OPTIMIZED: Only write to rows, not cells
            // CSS handles cell heights via inherit/100% (see job_calendar.css)
            weekRows.forEach(function(row) {
                // Set explicit pixel heights on rows only
                row.style.setProperty('height', weekHeight + 'px', 'important');
                row.style.setProperty('max-height', weekHeight + 'px', 'important');
                row.style.setProperty('overflow', 'hidden', 'important');
            });
        };

        /**
         * Set up ResizeObserver to handle container resize
         * DISABLED: ResizeObserver was causing forced reflows during initial render.
         * Height adjustments are now handled at explicit call sites:
         * - after calendar.render()
         * - after toggleSearchPanel() / toggleTodaySidebar() transitions
         * - in windowResize FullCalendar callback
         */
        proto.setupResizeObserver = function() {
            // DISABLED - see comment above
            return;
        };

        /**
         * Get saved calendar date from localStorage
         */
        proto.getSavedDate = function() {
            try {
                var savedDate = localStorage.getItem('gts-calendar-current-date');
                return savedDate ? new Date(savedDate) : null;
            } catch (error) {
                console.warn('Error loading saved calendar date:', error);
                return null;
            }
        };

        /**
         * Enable scrolling within day event containers
         */
        proto.enableDayCellScrolling = function() {
            var self = this;
            var calendarEl = this.calendarEl;
            if (!calendarEl) return;

            // Wheel/scroll navigation for weeks
            var wheelTimeout = null;
            calendarEl.addEventListener('wheel', function(e) {
                // Check if we're scrolling inside a day events container
                var dayEventsContainer = e.target.closest('.fc-daygrid-day-events');

                if (dayEventsContainer) {
                    // Check if the container can actually scroll
                    var canScroll = dayEventsContainer.scrollHeight > dayEventsContainer.clientHeight;

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

                wheelTimeout = setTimeout(function() {
                    wheelTimeout = null;
                }, 150);

                // Get current date from calendar
                var currentDate = self.calendar.getDate();

                // Calculate new date (scroll down = next week, scroll up = prev week)
                var newDate = new Date(currentDate);
                if (e.deltaY > 0) {
                    // Scroll down - next week
                    newDate.setDate(newDate.getDate() + 7);
                } else {
                    // Scroll up - previous week
                    newDate.setDate(newDate.getDate() - 7);
                }

                // Navigate to new date
                self.calendar.gotoDate(newDate);
                self.saveCurrentDate();
            }, { passive: false });
        };

        /**
         * Toggle search panel visibility
         */
        proto.toggleSearchPanel = function() {
            var self = this;
            this.searchPanelOpen = !this.searchPanelOpen;
            var searchPanel = document.getElementById('calendar-search-panel');
            var calendarShell = document.getElementById('calendar-shell');
            var searchInput = document.getElementById('calendar-search-input');
            var searchButton = document.querySelector('.fc-searchButton-button');

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
                setTimeout(function() {
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
            setTimeout(function() {
                if (self.calendar) {
                    self.calendar.updateSize();
                    self.forceEqualWeekHeights();
                }
            }, 350);
        };
    });

})();
