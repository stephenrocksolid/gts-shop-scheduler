/**
 * Job Calendar - Manages job calendar display with HTMX integration
 * Handles calendar rendering, filtering, and job status updates
 * VERSION: 3.0 - Modular Architecture (Phase 3)
 * 
 * This file is the thin "glue" that:
 * 1. Defines the JobCalendar class with state initialization
 * 2. Applies mixins from calendar/* modules via GTS.calendar.applyMixins()
 * 3. Creates the instance on DOM ready
 * 
 * All feature implementations are in calendar/*.js modules:
 * - registry.js: Mixin registration system
 * - utils.js: Shared utilities (toast, CSRF, debounce)
 * - layout.js: Layout, sizing, scroll wheel navigation
 * - events.js: Event fetching and caching
 * - today_sidebar.js: Today sidebar panel
 * - tooltips.js: Event hover tooltips
 * - rendering.js: Event rendering and styling
 * - day_interactions.js: Day click behaviors
 * - toolbar.js: Toolbar UI controls
 * - filters.js: Filter state persistence
 * - job_actions.js: Event click → panel/workspace
 * - recurrence_virtual.js: Virtual occurrence materialization
 * - call_reminders.js: Call reminder actions
 * - core.js: Lifecycle and FullCalendar wiring
 */

(function() {
    'use strict';

    /**
     * JobCalendar class - constructor only initializes state.
     * All methods are added via mixins from calendar/*.js modules.
     */
    class JobCalendar {
        constructor() {
            // FullCalendar instance and DOM references
            this.calendar = null;
            this.calendarEl = null;
            this.calendarFilter = null;
            this.statusFilter = null;
            this.searchFilter = null;
            this.loadingEl = null;
            this.noCalendarsOverlay = null;

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
            this.refetchDebounceMs = 150;

            // AbortController for cancelling in-flight fetch requests
            this.fetchAbortController = null;

            // Debounced UI update tracking
            this.uiUpdateTimer = null;
            this.uiUpdateDebounceMs = 50;

            // Search panel state - load from localStorage
            var savedSearchPanelState = localStorage.getItem('gts-calendar-search-open');
            this.searchPanelOpen = savedSearchPanelState === 'true';

            // Today sidebar state - default to open if not stored
            var savedTodaySidebarState = localStorage.getItem('gts-calendar-today-sidebar-open');
            this.todaySidebarOpen = savedTodaySidebarState === null ? true : savedTodaySidebarState === 'true';
            
            // Apply sidebar state early (before calendar renders)
            this.applyTodaySidebarState(false);

            // Initialize search panel state on page load
            if (this.searchPanelOpen) {
                this._initSearchPanelState();
            }

            // State management for filters
            this.currentFilters = {
                calendar: '',
                status: '',
                search: '',
                month: new Date().getMonth() + 1,
                year: new Date().getFullYear()
            };

            // Selected calendars and default calendar
            this.selectedCalendars = new Set();
            this.defaultCalendar = null;

            // Load saved filters from localStorage
            this.loadSavedFilters();

            // Initialize selected calendars BEFORE calendar is set up
            this.initializeSelectedCalendars();

            // Initialize the calendar (implemented in core.js mixin)
            this.initialize();
        }

        /**
         * Initialize search panel state on page load (called from constructor)
         * @private
         */
        _initSearchPanelState() {
            var self = this;
            setTimeout(function() {
                var searchPanel = document.getElementById('calendar-search-panel');
                var calendarShell = document.getElementById('calendar-shell');
                var searchInput = document.getElementById('calendar-search-input');
                var searchButton = document.querySelector('.fc-searchButton-button');

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
    }

    // Apply all registered mixins to the prototype
    // This adds all methods from calendar/*.js modules
    if (window.GTS && window.GTS.calendar && window.GTS.calendar.applyMixins) {
        GTS.calendar.applyMixins(JobCalendar);
    } else {
        console.error('GTS.calendar.applyMixins not available. Ensure calendar/registry.js is loaded first.');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            window.jobCalendar = new JobCalendar();
        });
    } else {
        window.jobCalendar = new JobCalendar();
    }

})();
