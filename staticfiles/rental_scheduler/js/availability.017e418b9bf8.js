/**
 * Availability.js - Manages availability search functionality
 * Handles form interactions, API calls, and real-time results updates
 */

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // Check for required dependencies
    if (!window.RentalConfig) {
        console.error('Availability: RentalConfig is required but not available');
        return;
    }

    // Initialize the availability search manager
    window.AvailabilityManager = class AvailabilityManager {
        constructor() {
            this.debounceTimer = null;
            this.debounceDelay = 500; // Wait 500ms after user stops typing

            // Initialize status popover properties
            this.statusPopover = null;
            this.boundCloseStatusPopover = null;
            this.boundEscapeHandler = null;

            // Initialize DOM elements
            this.initializeElements();

            // Validate required elements
            if (!this.validateElements()) {
                return;
            }

            // Initialize event listeners
            this.initializeEventListeners();

            // Initialize quick schedule functionality
            this.initializeQuickSchedule();

            // Check if we're returning from contract creation and clear if needed
            this.handleReturnFromContractCreation();

            // Restore search from URL parameters on page load
            this.restoreSearchFromURL();

            window.Logger?.info('AvailabilityManager: Initialized successfully');
        }

        /**
         * Initialize all DOM element references
         */
        initializeElements() {
            this.categorySelect = document.getElementById('category-filter');
            this.searchInput = document.getElementById('search-input');
            this.startDateInput = document.getElementById('id_start_datetime');
            this.endDateInput = document.getElementById('id_end_datetime');
            this.searchButton = document.getElementById('search-availability');
            this.clearButton = document.getElementById('clear-search');

            // Results containers
            this.availabilityResults = document.getElementById('availability-results');
            this.unavailabilityResults = document.getElementById('unavailability-results');

            // Loading indicators
            this.availabilityLoading = document.getElementById('availability-loading');
            this.unavailabilityLoading = document.getElementById('unavailability-loading');

            // Error display
            this.errorContainer = document.getElementById('availability-error');
            this.errorMessage = document.getElementById('availability-error-message');
        }

        /**
         * Validate that all required elements exist
         */
        validateElements() {
            const requiredElements = [
                'categorySelect', 'searchInput', 'startDateInput', 'endDateInput', 'searchButton',
                'availabilityResults', 'unavailabilityResults'
            ];

            for (const elementName of requiredElements) {
                if (!this[elementName]) {
                    window.Logger?.error(`AvailabilityManager: Required element ${elementName} not found`);
                    return false;
                }
            }

            return true;
        }

        /**
         * Initialize event listeners
         */
        initializeEventListeners() {
            // Search button click
            this.searchButton.addEventListener('click', () => {
                this.performSearch();
            });

            // Clear button click
            if (this.clearButton) {
                this.clearButton.addEventListener('click', () => {
                    this.clearSearch();
                });
            }

            // Auto-search on form changes (debounced)
            const autoSearchElements = [this.categorySelect, this.startDateInput, this.endDateInput];
            autoSearchElements.forEach(element => {
                element.addEventListener('change', () => {
                    this.debouncedSearch();
                });
            });

            // Search input with keyup debounced search (similar to trailer list)
            if (this.searchInput) {
                this.searchInput.addEventListener('keyup', () => {
                    this.debouncedSearch();
                });
                this.searchInput.addEventListener('change', () => {
                    this.debouncedSearch();
                });
            }

            // Enable/disable search button based on form validity
            autoSearchElements.forEach(element => {
                element.addEventListener('input', () => {
                    this.updateSearchButtonState();
                });
                element.addEventListener('change', () => {
                    this.updateSearchButtonState();
                });
            });

            // Initial button state
            this.updateSearchButtonState();
        }

        /**
         * Debounced search to avoid excessive API calls
         */
        debouncedSearch() {
            // Skip debounced search if we're applying a quick schedule
            if (this.isApplyingQuickSchedule) {
                return;
            }

            // Clear existing timer
            if (this.debounceTimer) {
                clearTimeout(this.debounceTimer);
            }

            // Set new timer
            this.debounceTimer = setTimeout(() => {
                if (this.isFormValid()) {
                    this.performSearch();
                }
            }, this.debounceDelay);
        }

        /**
         * Check if the form has all required fields
         */
        isFormValid() {
            return this.categorySelect.value &&
                this.startDateInput.value &&
                this.endDateInput.value;
        }

        /**
         * Update search button state based on form validity
         */
        updateSearchButtonState() {
            const isValid = this.isFormValid();
            this.searchButton.disabled = !isValid;

            if (isValid) {
                this.searchButton.classList.remove('opacity-50', 'cursor-not-allowed');
            } else {
                this.searchButton.classList.add('opacity-50', 'cursor-not-allowed');
            }
        }

        /**
         * Show loading state
         */
        showLoading() {
            if (this.availabilityLoading) {
                this.availabilityLoading.classList.remove('hidden');
            }
            if (this.unavailabilityLoading) {
                this.unavailabilityLoading.classList.remove('hidden');
            }
            this.searchButton.disabled = true;
            this.searchButton.innerHTML = `
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Searching...
            `;
        }

        /**
         * Hide loading state
         */
        hideLoading() {
            if (this.availabilityLoading) {
                this.availabilityLoading.classList.add('hidden');
            }
            if (this.unavailabilityLoading) {
                this.unavailabilityLoading.classList.add('hidden');
            }
            this.searchButton.disabled = false;
            this.searchButton.innerHTML = `
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"></path>
                </svg>
                Search Availability
            `;
        }

        /**
         * Show error message
         */
        showError(message) {
            if (this.errorContainer && this.errorMessage) {
                this.errorMessage.textContent = message;
                this.errorContainer.classList.remove('hidden');
            }
        }

        /**
         * Hide error message
         */
        hideError() {
            if (this.errorContainer) {
                this.errorContainer.classList.add('hidden');
            }
        }

        /**
         * Convert datetime input value to API format
         */
        formatDateForAPI(dateString) {
            if (!dateString) return '';

            try {
                // Parse the date string from flatpickr format
                const date = new Date(dateString);
                if (isNaN(date.getTime())) {
                    throw new Error('Invalid date');
                }

                // Format as YYYY-MM-DD HH:MM:SS
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                const seconds = String(date.getSeconds()).padStart(2, '0');

                return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
            } catch (error) {
                window.Logger?.error('AvailabilityManager: Error formatting date', error);
                return '';
            }
        }

        /**
         * Validate date range
         */
        validateDateRange(startDate, endDate) {
            if (!startDate || !endDate) {
                return { valid: false, message: 'Please select both start and end dates' };
            }

            const start = new Date(startDate);
            const end = new Date(endDate);

            if (isNaN(start.getTime()) || isNaN(end.getTime())) {
                return { valid: false, message: 'Invalid date format' };
            }

            if (end <= start) {
                return { valid: false, message: 'End date must be after start date' };
            }

            return { valid: true };
        }

        /**
         * Perform the availability search
         */
        async performSearch() {
            window.Logger?.debug('AvailabilityManager: Starting availability search');

            // Hide error
            this.hideError();

            // Get form values
            const category = this.categorySelect.value;
            const startDate = this.formatDateForAPI(this.startDateInput.value);
            const endDate = this.formatDateForAPI(this.endDateInput.value);

            // Validate inputs
            if (!category) {
                this.showError('Please select a category');
                return;
            }

            const dateValidation = this.validateDateRange(this.startDateInput.value, this.endDateInput.value);
            if (!dateValidation.valid) {
                this.showError(dateValidation.message);
                return;
            }

            // Save search parameters to URL before starting search
            this.saveSearchToURL({
                category: category,
                search: this.searchInput?.value?.trim() || '',
                start_date: this.startDateInput.value,
                end_date: this.endDateInput.value
            });

            // Show loading state
            this.showLoading();

            try {
                // Build API URL
                const apiUrl = new URL('/api/availability/search/', window.location.origin);
                apiUrl.searchParams.append('category', category);
                apiUrl.searchParams.append('start_date', startDate);
                apiUrl.searchParams.append('end_date', endDate);

                // Add search parameter if provided
                const searchTerm = this.searchInput?.value?.trim();
                if (searchTerm) {
                    apiUrl.searchParams.append('search', searchTerm);
                }

                window.Logger?.debug('AvailabilityManager: Calling API', { url: apiUrl.toString() });

                // Make API call
                const response = await fetch(apiUrl, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                    }
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || `HTTP ${response.status}`);
                }

                if (!data.success) {
                    throw new Error(data.error || 'Search failed');
                }

                // Update results
                this.updateResults(data);

                window.Logger?.info('AvailabilityManager: Search completed successfully', {
                    availableCount: data.available_count,
                    unavailableCount: data.unavailable_count
                });

            } catch (error) {
                window.Logger?.error('AvailabilityManager: Search error', error);
                this.showError(error.message || 'An error occurred while searching for availability');

                // Show empty state on error
                this.showEmptyState();
            } finally {
                this.hideLoading();
            }
        }

        /**
         * Update results containers with API response
         */
        updateResults(data) {
            // Update available results
            if (this.availabilityResults) {
                this.availabilityResults.innerHTML = data.available_html || '';
            }

            // Update unavailable results
            if (this.unavailabilityResults) {
                this.unavailabilityResults.innerHTML = data.unavailable_html || '';
            }

            // Update duration info section
            this.updateDurationInfo(data);

            // Wire up status popovers for any newly inserted buttons
            this.attachStatusButtons();

            // Attach click handlers to trailer links to clear search on navigation
            this.attachTrailerLinkHandlers();
        }

        /**
         * Update the duration info display
         */
        updateDurationInfo(data) {
            const durationField = document.getElementById('duration-field');

            if (durationField) {
                // Update duration field with just the duration (rate category shown in trailer rows)
                if (data.duration_display) {
                    durationField.value = data.duration_display;
                } else {
                    // Clear field if no data
                    durationField.value = '';
                }
            }
        }

        /**
         * Attach click handlers to "Update Status" buttons in unavailable list
         */
        attachStatusButtons() {
            const buttons = this.unavailabilityResults?.querySelectorAll('button[data-contract-id]') || [];
            buttons.forEach(btn => {
                // Remove any existing listener first to avoid duplicates
                btn.removeEventListener('click', btn._statusHandler);

                // Create and store the handler for future removal
                btn._statusHandler = (e) => {
                    e.stopPropagation();
                    this.openStatusPopover(btn);
                };

                btn.addEventListener('click', btn._statusHandler);
            });
        }

        /**
         * Open a lightweight status popover similar to calendar's, and send updates via the same API
         */
        openStatusPopover(triggerEl) {
            // Close any existing popover first
            this.closeStatusPopover();

            const contractId = triggerEl.getAttribute('data-contract-id');
            const current = {
                is_invoiced: triggerEl.getAttribute('data-is-invoiced') === 'true',
                is_picked_up: triggerEl.getAttribute('data-is-picked-up') === 'true',
                is_returned: triggerEl.getAttribute('data-is-returned') === 'true',
                return_iso: triggerEl.getAttribute('data-return-iso') || ''
            };

            const pop = document.createElement('div');
            pop.className = 'z-50 absolute bg-white border border-gray-200 rounded shadow p-3 text-sm';
            pop.style.minWidth = '220px';
            pop.innerHTML = `
                <div class="mb-2 font-medium text-gray-800">Update Status</div>
                <label class="flex items-center gap-2 mb-1">
                    <input type="checkbox" name="is_invoiced" ${current.is_invoiced ? 'checked' : ''}>
                    <span>Send Invoice</span>
                </label>
                <label class="flex items-center gap-2 mb-1">
                    <input type="checkbox" name="is_picked_up" ${current.is_picked_up ? 'checked' : ''}>
                    <span>Picked Up</span>
                </label>
                <label class="flex items-center gap-2 mb-2">
                    <input type="checkbox" name="is_returned" ${current.is_returned ? 'checked' : ''}>
                    <span>Returned</span>
                </label>
                <div class="mb-2" id="return_datetime_container" style="display: none;">
                    <input type="datetime-local" class="border rounded px-2 py-1 w-full" id="return_datetime_field">
                </div>
                <div class="flex justify-end gap-2">
                    <button class="px-2 py-1 text-xs rounded border border-gray-300 bg-white hover:bg-gray-50 text-gray-700" data-action="cancel">Cancel</button>
                    <button class="px-2 py-1 text-xs rounded bg-indigo-600 text-white hover:bg-indigo-700" data-action="save">Save</button>
                </div>
            `;

            document.body.appendChild(pop);
            this.statusPopover = pop;

            // Position near trigger
            const rect = triggerEl.getBoundingClientRect();
            pop.style.top = `${window.scrollY + rect.bottom + 6}px`;
            pop.style.left = `${window.scrollX + rect.left}px`;

            // Prevent popover clicks from closing it
            pop.addEventListener('click', e => e.stopPropagation());

            // Setup outside click handler with a delay to prevent immediate closure
            setTimeout(() => {
                this.boundCloseStatusPopover = () => this.closeStatusPopover();
                document.addEventListener('click', this.boundCloseStatusPopover, { once: true });
            }, 0);

            // Setup escape key handler
            this.boundEscapeHandler = (e) => {
                if (e.key === 'Escape') {
                    this.closeStatusPopover();
                }
            };
            document.addEventListener('keydown', this.boundEscapeHandler);

            const returnedCheckbox = pop.querySelector('input[name="is_returned"]');
            const returnContainer = pop.querySelector('#return_datetime_container');
            const returnField = pop.querySelector('#return_datetime_field');

            const applyDefaultReturnTime = () => {
                if (!returnField.value) {
                    const d = new Date();
                    d.setHours(6, 59, 0, 0); // 6:59 AM today
                    const year = d.getFullYear();
                    const month = String(d.getMonth() + 1).padStart(2, '0');
                    const day = String(d.getDate()).padStart(2, '0');
                    const hours = String(d.getHours()).padStart(2, '0');
                    const minutes = String(d.getMinutes()).padStart(2, '0');
                    returnField.value = `${year}-${month}-${day}T${hours}:${minutes}`;
                }
            };

            const updateReturnVisibility = () => {
                if (returnedCheckbox.checked) {
                    returnContainer.style.display = 'block';
                    applyDefaultReturnTime();
                } else {
                    returnContainer.style.display = 'none';
                }
            };
            returnedCheckbox.addEventListener('change', updateReturnVisibility);
            updateReturnVisibility();

            // Pre-populate return datetime if we have one
            if (current.return_iso) {
                try {
                    const dt = new Date(current.return_iso);
                    if (!isNaN(dt.getTime())) {
                        const year = dt.getFullYear();
                        const month = String(dt.getMonth() + 1).padStart(2, '0');
                        const day = String(dt.getDate()).padStart(2, '0');
                        const hours = String(dt.getHours()).padStart(2, '0');
                        const minutes = String(dt.getMinutes()).padStart(2, '0');
                        returnField.value = `${year}-${month}-${day}T${hours}:${minutes}`;
                        returnedCheckbox.checked = true;
                        updateReturnVisibility();
                    }
                } catch (_) { /* ignore */ }
            } else {
                // No existing return time – set default 6:59 AM today
                applyDefaultReturnTime();
            }

            pop.addEventListener('click', async (e) => {
                const action = e.target.getAttribute('data-action');
                if (!action) return;
                if (action === 'cancel') {
                    this.closeStatusPopover();
                    return;
                }

                // Build payload similar to calendar's toggle API
                const payload = new URLSearchParams();
                if (pop.querySelector('input[name="is_invoiced"]').checked) payload.append('is_invoiced', 'on');
                if (pop.querySelector('input[name="is_picked_up"]').checked) payload.append('is_picked_up', 'on');
                if (returnedCheckbox.checked) {
                    payload.append('is_returned', 'on');
                    if (returnField.value) payload.append('return_datetime', returnField.value);
                }

                try {
                    const res = await fetch(`/contracts/${contractId}/status/`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': this.getCSRFToken(),
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: payload.toString()
                    });
                    if (!res.ok) {
                        throw new Error(`HTTP ${res.status}`);
                    }
                    const data = await res.json();
                    if (!res.ok || data.status !== 'success') throw new Error(data.error || 'Update failed');
                    this.closeStatusPopover();
                    // Refresh results to reflect changes
                    this.performSearch();
                } catch (err) {
                    window.Logger?.error('AvailabilityManager: status update failed', err);
                }
            });
        }

        /**
         * Close the status popover and clean up event listeners
         */
        closeStatusPopover() {
            if (this.statusPopover) {
                // Remove the popover from DOM
                if (this.statusPopover.parentNode) {
                    this.statusPopover.parentNode.removeChild(this.statusPopover);
                }
                this.statusPopover = null;
            }

            // Clean up event listeners
            if (this.boundCloseStatusPopover) {
                document.removeEventListener('click', this.boundCloseStatusPopover);
                this.boundCloseStatusPopover = null;
            }

            if (this.boundEscapeHandler) {
                document.removeEventListener('keydown', this.boundEscapeHandler);
                this.boundEscapeHandler = null;
            }
        }

        getCSRFToken() {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') return value;
            }
            const meta = document.querySelector('meta[name="csrf-token"]');
            return meta ? meta.getAttribute('content') : '';
        }

        /**
         * Show empty state when no results or error
         */
        showEmptyState() {
            if (this.availabilityResults) {
                this.availabilityResults.innerHTML = `
                    <div class="text-center py-8 text-gray-500">
                        <p>Select a category and dates to see available trailers</p>
                    </div>
                `;
            }

            if (this.unavailabilityResults) {
                this.unavailabilityResults.innerHTML = `
                    <div class="text-center py-8 text-gray-500">
                        <p>Select a category and dates to see unavailable trailers</p>
                    </div>
                `;
            }

            // Clear duration field
            const durationField = document.getElementById('duration-field');
            if (durationField) {
                durationField.value = '';
            }
        }

        /**
         * Save search parameters to URL and localStorage
         */
        saveSearchToURL(params) {
            try {
                const url = new URL(window.location);
                url.searchParams.set('category', params.category || '');
                url.searchParams.set('search', params.search || '');
                url.searchParams.set('start_date', params.start_date || '');
                url.searchParams.set('end_date', params.end_date || '');

                // Update URL without page reload
                window.history.replaceState({}, '', url);

                // Also save to localStorage for persistence across navigation
                this.saveSearchToLocalStorage(params);

                window.Logger?.debug('AvailabilityManager: Search parameters saved to URL and localStorage', params);
            } catch (error) {
                window.Logger?.error('AvailabilityManager: Error saving search to URL', error);
            }
        }

        /**
         * Restore search from URL parameters or localStorage and perform search if data is complete
         */
        async restoreSearchFromURL() {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                let category = urlParams.get('category');
                let search = urlParams.get('search');
                let startDate = urlParams.get('start_date');
                let endDate = urlParams.get('end_date');

                // If no URL parameters, try localStorage
                if (!category && !search && !startDate && !endDate) {
                    const savedSearch = this.loadSearchFromLocalStorage();
                    if (savedSearch) {
                        category = savedSearch.category;
                        search = savedSearch.search;
                        startDate = savedSearch.start_date;
                        endDate = savedSearch.end_date;
                        window.Logger?.debug('AvailabilityManager: Restoring search from localStorage', savedSearch);
                    }
                } else {
                    window.Logger?.debug('AvailabilityManager: Restoring search from URL', {
                        category, search, startDate, endDate
                    });
                }

                // Only restore if we have parameters from either source
                if (!category && !startDate && !endDate) {
                    return;
                }

                // Restore form values
                if (category) {
                    this.categorySelect.value = category;
                }
                if (search && this.searchInput) {
                    this.searchInput.value = search;
                }
                if (startDate) {
                    this.startDateInput.value = startDate;
                    // Trigger flatpickr update if it exists
                    if (this.startDateInput._flatpickr) {
                        this.startDateInput._flatpickr.setDate(startDate, false);
                    }
                }
                if (endDate) {
                    this.endDateInput.value = endDate;
                    // Trigger flatpickr update if it exists
                    if (this.endDateInput._flatpickr) {
                        this.endDateInput._flatpickr.setDate(endDate, false);
                    }
                }

                // Update button state
                this.updateSearchButtonState();

                // Perform search if form is complete
                if (this.isFormValid()) {
                    // Small delay to ensure flatpickr has updated
                    setTimeout(() => {
                        this.performSearch();
                    }, 100);
                }
            } catch (error) {
                window.Logger?.error('AvailabilityManager: Error restoring search from URL/localStorage', error);
            }
        }

        /**
         * Clear the search form and results
         */
        clearSearch() {
            window.Logger?.debug('AvailabilityManager: Clearing search');

            // Clear form fields
            this.categorySelect.value = '';
            if (this.searchInput) {
                this.searchInput.value = '';
            }
            this.startDateInput.value = '';
            this.endDateInput.value = '';

            // Clear flatpickr if it exists
            if (this.startDateInput._flatpickr) {
                this.startDateInput._flatpickr.clear();
            }
            if (this.endDateInput._flatpickr) {
                this.endDateInput._flatpickr.clear();
            }

            // Clear URL parameters
            const url = new URL(window.location);
            url.searchParams.delete('category');
            url.searchParams.delete('start_date');
            url.searchParams.delete('end_date');
            window.history.replaceState({}, '', url);

            // Clear localStorage
            this.clearSearchFromLocalStorage();

            // Hide error
            this.hideError();

            // Show empty state
            this.showEmptyState();

            // Update button state
            this.updateSearchButtonState();

            window.Logger?.info('AvailabilityManager: Search cleared');
        }

        /**
         * Initialize quick schedule functionality
         */
        initializeQuickSchedule() {
            this.fullDayDays = 1; // For cycling through 1-4 days
            this.isApplyingQuickSchedule = false; // Flag to prevent double renders
            this.setupQuickScheduleButtons();
        }

        /**
         * Setup all quick schedule buttons
         */
        setupQuickScheduleButtons() {
            this.setupMorningHalfDay();
            this.setupAfternoonHalfDay();
            this.setupFullDay();
            this.setupWeekly();
        }

        /**
         * Setup morning half day button (7:00 AM - 12:00 PM)
         */
        setupMorningHalfDay() {
            const button = document.getElementById('qs_morning_half_day');
            if (!button) return;

            button.addEventListener('click', () => {
                this.applyQuickSchedule('7:00 AM', '12:00 PM', 0);
            });
        }

        /**
         * Setup afternoon half day button (1:00 PM - 6:00 PM)
         */
        setupAfternoonHalfDay() {
            const button = document.getElementById('qs_afternoon_half_day');
            if (!button) return;

            button.addEventListener('click', () => {
                this.applyQuickSchedule('1:00 PM', '6:00 PM', 0);
            });
        }

        /**
         * Setup full day button with cycling functionality (1-4 days)
         */
        setupFullDay() {
            const button = document.getElementById('qs_full_day');
            const label = document.getElementById('qs_full_day_label');
            if (!button || !label) return;

            // Set initial label
            this.updateFullDayLabel(label);

            button.addEventListener('click', () => {
                const currentDays = this.fullDayDays;

                // Apply the schedule for current days
                this.applyQuickSchedule('7:00 AM', '5:00 PM', currentDays - 1);

                // Cycle to next number of days (1-4)
                this.fullDayDays = (this.fullDayDays % 4) + 1;
                this.updateFullDayLabel(label);
            });
        }

        /**
         * Setup weekly button (7 days)
         */
        setupWeekly() {
            const button = document.getElementById('qs_weekly');
            if (!button) return;

            button.addEventListener('click', () => {
                this.applyQuickSchedule('7:00 AM', '5:00 PM', 6); // 7 days = start + 6 additional days
            });
        }

        /**
         * Update full day button label to show current cycle
         */
        updateFullDayLabel(label) {
            const dayTexts = ['Full Day', '2 Days', '3 Days', '4 Days'];
            label.textContent = dayTexts[this.fullDayDays - 1];
        }

        /**
 * Apply quick schedule with specified times and duration
 */
        applyQuickSchedule(startTime, endTime, additionalDays) {
            // Set flag to prevent auto-search from triggering during value updates
            this.isApplyingQuickSchedule = true;

            // Determine base date: use existing start date if present, otherwise use today
            let baseDate;
            if (this.startDateInput.value) {
                // Parse existing start date
                baseDate = new Date(this.startDateInput.value);
                if (isNaN(baseDate.getTime())) {
                    // Fallback to today if parsing fails
                    baseDate = new Date();
                }
            } else {
                // No start date selected, use today
                baseDate = new Date();
            }

            // Create start and end dates based on the base date
            const startDate = new Date(baseDate);
            const endDate = new Date(baseDate);

            // Parse start time and apply to start date
            const startTimeParts = this.parseTimeString(startTime);
            startDate.setHours(startTimeParts.hours, startTimeParts.minutes, 0, 0);

            // Parse end time and add additional days if needed
            const endTimeParts = this.parseTimeString(endTime);
            endDate.setDate(endDate.getDate() + additionalDays);
            endDate.setHours(endTimeParts.hours, endTimeParts.minutes, 0, 0);

            // Format dates for flatpickr (MM/DD/YYYY HH:MM AM/PM)
            const startFormatted = this.formatDateForInput(startDate);
            const endFormatted = this.formatDateForInput(endDate);

            // Set input values
            this.startDateInput.value = startFormatted;
            this.endDateInput.value = endFormatted;

            // Update flatpickr instances if they exist
            if (this.startDateInput._flatpickr) {
                this.startDateInput._flatpickr.setDate(startDate, true);
            }
            if (this.endDateInput._flatpickr) {
                this.endDateInput._flatpickr.setDate(endDate, true);
            }

            // Update button state
            this.updateSearchButtonState();

            // Clear the flag and trigger search once
            this.isApplyingQuickSchedule = false;

            // Trigger single search after a brief delay
            setTimeout(() => {
                if (this.isFormValid()) {
                    this.performSearch();
                }
            }, 150); // Slightly longer delay to ensure all updates are complete

            window.Logger?.debug('AvailabilityManager: Applied quick schedule', {
                baseDate: baseDate.toISOString(),
                startTime, endTime, additionalDays,
                startFormatted, endFormatted
            });
        }

        /**
         * Parse time string like "7:00 AM" or "1:00 PM"
         */
        parseTimeString(timeStr) {
            const match = timeStr.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
            if (!match) return { hours: 0, minutes: 0 };

            let hours = parseInt(match[1]);
            const minutes = parseInt(match[2]);
            const meridiem = match[3].toUpperCase();

            if (meridiem === 'PM' && hours !== 12) {
                hours += 12;
            } else if (meridiem === 'AM' && hours === 12) {
                hours = 0;
            }

            return { hours, minutes };
        }

        /**
         * Format date for input field (MM/DD/YYYY HH:MM AM/PM)
         */
        formatDateForInput(date) {
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const year = date.getFullYear();

            let hours = date.getHours();
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const meridiem = hours >= 12 ? 'PM' : 'AM';

            if (hours === 0) {
                hours = 12;
            } else if (hours > 12) {
                hours -= 12;
            }

            return `${month}/${day}/${year} ${hours}:${minutes} ${meridiem}`;
        }

        /**
         * Save search parameters to localStorage for persistence across navigation
         */
        saveSearchToLocalStorage(params) {
            try {
                const searchData = {
                    category: params.category || '',
                    search: params.search || '',
                    start_date: params.start_date || '',
                    end_date: params.end_date || '',
                    timestamp: Date.now() // For potential expiration in the future
                };
                localStorage.setItem('availabilitySearch', JSON.stringify(searchData));
                window.Logger?.debug('AvailabilityManager: Search saved to localStorage', searchData);
            } catch (error) {
                window.Logger?.error('AvailabilityManager: Error saving to localStorage', error);
            }
        }

        /**
         * Load search parameters from localStorage
         */
        loadSearchFromLocalStorage() {
            try {
                const stored = localStorage.getItem('availabilitySearch');
                if (stored) {
                    const searchData = JSON.parse(stored);
                    // Optional: Check if data is too old (e.g., older than 24 hours)
                    // const isStale = searchData.timestamp && (Date.now() - searchData.timestamp) > (24 * 60 * 60 * 1000);
                    // if (isStale) {
                    //     this.clearSearchFromLocalStorage();
                    //     return null;
                    // }
                    return searchData;
                }
            } catch (error) {
                window.Logger?.error('AvailabilityManager: Error loading from localStorage', error);
                // Clear corrupted data
                this.clearSearchFromLocalStorage();
            }
            return null;
        }

        /**
         * Clear search parameters from localStorage
         */
        clearSearchFromLocalStorage() {
            try {
                localStorage.removeItem('availabilitySearch');
                window.Logger?.debug('AvailabilityManager: localStorage cleared');
            } catch (error) {
                window.Logger?.error('AvailabilityManager: Error clearing localStorage', error);
            }
        }

        /**
         * Completely clear all search terms (URL and localStorage) without updating the form
         */
        clearSearchTermsCompletely() {
            try {
                // Clear URL parameters
                const url = new URL(window.location);
                url.searchParams.delete('category');
                url.searchParams.delete('search');
                url.searchParams.delete('start_date');
                url.searchParams.delete('end_date');
                window.history.replaceState({}, '', url);

                // Clear localStorage
                this.clearSearchFromLocalStorage();

                window.Logger?.debug('AvailabilityManager: All search terms cleared completely');
            } catch (error) {
                window.Logger?.error('AvailabilityManager: Error clearing search terms completely', error);
            }
        }

        /**
         * Attach click handlers to trailer links to clear search terms before navigation
         */
        attachTrailerLinkHandlers() {
            // Find all trailer links in both available and unavailable results
            const trailerLinks = [
                ...(this.availabilityResults?.querySelectorAll('a[href*="contract_create"]') || []),
                ...(this.unavailabilityResults?.querySelectorAll('a[href*="contract_create"]') || [])
            ];

            trailerLinks.forEach(link => {
                // Remove any existing event listener to avoid duplicates
                if (link._clearSearchHandler) {
                    link.removeEventListener('click', link._clearSearchHandler);
                }

                // Create and store a bound handler for this specific link
                link._clearSearchHandler = this.handleTrailerLinkClick.bind(this);

                // Add new event listener
                link.addEventListener('click', link._clearSearchHandler);
            });

            window.Logger?.debug('AvailabilityManager: Attached click handlers to trailer links', {
                linkCount: trailerLinks.length
            });
        }

        /**
         * Handle trailer link click - clear search terms before navigation
         */
        handleTrailerLinkClick(event) {
            window.Logger?.debug('AvailabilityManager: Trailer link clicked, clearing search terms');

            // Set a flag to indicate we're navigating to contract creation
            try {
                localStorage.setItem('availabilityNavigatingToContract', 'true');
            } catch (error) {
                window.Logger?.warn('AvailabilityManager: Could not set navigation flag', error);
            }

            // Clear search terms immediately and synchronously
            this.clearSearchTermsCompletely();

            // Add a small delay to ensure localStorage/URL clearing completes
            // before navigation (shouldn't be needed but being extra safe)
            setTimeout(() => {
                window.Logger?.debug('AvailabilityManager: Search terms cleared, allowing navigation');
            }, 10);

            // Allow normal link navigation to proceed
        }

        /**
         * Check if we're returning from contract creation and ensure search is cleared
         */
        handleReturnFromContractCreation() {
            try {
                const wasNavigatingToContract = localStorage.getItem('availabilityNavigatingToContract');
                if (wasNavigatingToContract === 'true') {
                    window.Logger?.debug('AvailabilityManager: Returning from contract creation, ensuring search is cleared');

                    // Clear the flag
                    localStorage.removeItem('availabilityNavigatingToContract');

                    // Ensure search terms are completely cleared
                    this.clearSearchTermsCompletely();

                    window.Logger?.info('AvailabilityManager: Search cleared on return from contract creation');
                }
            } catch (error) {
                window.Logger?.error('AvailabilityManager: Error handling return from contract creation', error);
            }
        }
    };

    // Initialize the availability manager
    try {
        new window.AvailabilityManager();
    } catch (error) {
        window.Logger?.error('AvailabilityManager: Initialization failed', error);
    }
});
