/**
 * Calendar Filters Module
 * 
 * Handles filter state persistence (localStorage + URL params).
 * Registers: loadSavedFilters, initializeSelectedCalendars, saveFilters,
 *            updateURLParams, clearFilters, handleFilterChange, handleDatesSet
 */
(function() {
    'use strict';

    GTS.calendar.register('filters', function(proto) {
        /**
         * Load saved filters from localStorage
         */
        proto.loadSavedFilters = function() {
            try {
                // First, check if there are URL parameters (from direct links or browser back/forward)
                var urlParams = new URLSearchParams(window.location.search);
                var urlCalendar = urlParams.get('calendar') || '';
                var urlStatus = urlParams.get('status') || '';
                var urlSearch = urlParams.get('search') || '';

                // If URL has parameters, use them (they take priority)
                if (urlCalendar || urlStatus || urlSearch) {
                    this.currentFilters.calendar = urlCalendar;
                    this.currentFilters.status = urlStatus;
                    this.currentFilters.search = urlSearch;
                } else {
                    // Otherwise, load from localStorage
                    var savedFilters = localStorage.getItem('gts-calendar-filters');
                    if (savedFilters) {
                        var filters = JSON.parse(savedFilters);
                        this.currentFilters.calendar = filters.calendar || '';
                        this.currentFilters.status = filters.status || '';
                        this.currentFilters.search = filters.search || '';
                    }
                }
            } catch (error) {
                console.warn('JobCalendar: Error loading saved filters', error);
            }
        };

        /**
         * Initialize selected calendars from localStorage
         * This must happen BEFORE the calendar is rendered to ensure
         * the first event fetch includes the proper calendar filter
         */
        proto.initializeSelectedCalendars = function() {
            var selectedCalendars = [];

            // Load selected calendars from storage
            try {
                var saved = localStorage.getItem('gts-selected-calendars');
                if (saved) {
                    selectedCalendars = JSON.parse(saved);
                }
            } catch (error) {
                console.warn('Error loading saved calendar selection:', error);
            }

            // If nothing saved, default to all calendars selected
            var calendars = (window.calendarConfig && window.calendarConfig.calendars) || [];
            if (selectedCalendars.length === 0 && calendars.length > 0) {
                selectedCalendars = calendars.map(function(c) { return c.id; });
            }

            // Store selected calendars
            this.selectedCalendars = new Set(selectedCalendars);

            // Load default calendar from storage
            var defaultCalendar = null;
            try {
                var savedDefault = localStorage.getItem('gts-default-calendar');
                if (savedDefault) {
                    defaultCalendar = parseInt(savedDefault);
                }
            } catch (error) {
                console.warn('Error loading default calendar:', error);
            }

            this.defaultCalendar = defaultCalendar;
        };

        /**
         * Save current filters to localStorage
         */
        proto.saveFilters = function() {
            try {
                var filtersToSave = {
                    calendar: this.currentFilters.calendar,
                    status: this.currentFilters.status,
                    search: this.currentFilters.search
                };
                localStorage.setItem('gts-calendar-filters', JSON.stringify(filtersToSave));
            } catch (error) {
                console.warn('JobCalendar: Error saving filters', error);
            }
        };

        /**
         * Update URL parameters to reflect current filter state
         */
        proto.updateURLParams = function() {
            try {
                var url = new URL(window.location);
                var params = url.searchParams;

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
                var newURL = url.pathname + (params.toString() ? '?' + params.toString() : '');
                window.history.replaceState({}, '', newURL);
            } catch (error) {
                console.warn('JobCalendar: Error updating URL params', error);
            }
        };

        /**
         * Clear all filters
         */
        proto.clearFilters = function() {
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
        };

        /**
         * Handle filter changes
         */
        proto.handleFilterChange = function() {
            this.currentFilters.calendar = this.calendarFilter ? this.calendarFilter.value : '';
            this.currentFilters.status = this.statusFilter ? this.statusFilter.value : '';
            this.currentFilters.search = this.searchFilter ? this.searchFilter.value : '';

            // Save filters and update URL
            this.saveFilters();
            this.updateURLParams();

            this.refreshCalendar();
        };

        /**
         * Handle calendar date changes
         */
        proto.handleDatesSet = function(info) {
            this.currentFilters.month = info.start.getMonth() + 1;
            this.currentFilters.year = info.start.getFullYear();
        };
    });

})();
