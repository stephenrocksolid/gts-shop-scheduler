/**
 * CustomerSearch - Manages customer search functionality and form population
 * Handles search input, API calls, and customer data population
 */

// Wrap in IIFE to avoid global conflicts
(function () {
    'use strict';

    // Defensive loading - only declare CustomerSearch if it doesn't already exist
    if (typeof window.CustomerSearch === 'undefined') {

        class CustomerSearch {
            constructor(options) {
                // Check for required dependencies
                if (!window.RentalConfig) {
                    window.Logger?.error('CustomerSearch: RentalConfig is required but not available');
                    return;
                }

                if (!window.Logger) {
                    console.warn('CustomerSearch: Logger not available, falling back to console logging');
                }

                // Initialize DOM elements
                this.searchInput = document.getElementById(options.searchInputId);
                this.searchResults = document.getElementById(options.searchResultsId);
                this.customerIdInput = document.getElementById(options.customerIdInputId);
                this.formFieldIds = options.formFieldIds;
                this.searchTimeout = null;

                // Validate required elements
                if (!this.validateElements()) {
                    window.Logger?.error('CustomerSearch: Required elements not found');
                    return;
                }

                // Initialize functionality
                this.init();

                window.Logger?.debug('CustomerSearch initialized successfully', {
                    searchInputId: options.searchInputId,
                    searchResultsId: options.searchResultsId,
                    customerIdInputId: options.customerIdInputId,
                    formFieldCount: Object.keys(this.formFieldIds).length
                });
            }

            /**
             * Validate that required DOM elements exist
             * @returns {boolean} True if all required elements are present
             */
            validateElements() {
                const required = {
                    searchInput: this.searchInput,
                    searchResults: this.searchResults,
                    customerIdInput: this.customerIdInput
                };

                const missing = Object.entries(required)
                    .filter(([name, element]) => !element)
                    .map(([name]) => name);

                if (missing.length > 0) {
                    window.Logger?.error('CustomerSearch: Missing required elements', { missing });
                    return false;
                }

                return true;
            }

            init() {
                this.setupSearchHandler();
                this.setupClickOutside();
            }

            /**
 * Populate form fields with selected customer data
 * @param {Object} customer - Customer data object
 */
            populateCustomerFields(customer) {
                try {
                    window.Logger?.debug('CustomerSearch: Populating customer fields', {
                        customerId: customer.id,
                        customerName: customer.name
                    });

                    this.customerIdInput.value = customer.id;

                    // Populate each form field
                    let populatedFields = 0;
                    Object.entries(this.formFieldIds).forEach(([field, id]) => {
                        const element = document.getElementById(id);
                        if (element) {
                            element.value = customer[field] || '';
                            populatedFields++;
                        } else {
                            window.Logger?.warn(`CustomerSearch: Form field element not found`, { field, id });
                        }
                    });

                    // Clear search interface
                    this.clearSearch();

                    window.Logger?.info('CustomerSearch: Customer fields populated successfully', {
                        customerId: customer.id,
                        customerName: customer.name,
                        populatedFields
                    });

                } catch (error) {
                    window.Logger?.error('CustomerSearch: Error populating customer fields', error);
                    this.showError('Failed to populate customer information');
                }
            }

            /**
             * Clear search input and results
             */
            clearSearch() {
                this.searchInput.value = '';
                this.searchResults.innerHTML = '';
                this.searchResults.classList.add('hidden');
            }

            setupSearchHandler() {
                this.searchInput.addEventListener('input', () => {
                    clearTimeout(this.searchTimeout);
                    const query = this.searchInput.value.trim();

                    if (query.length < 2) {
                        this.searchResults.innerHTML = '';
                        this.searchResults.classList.add('hidden');
                        return;
                    }

                    const debounceDelay = window.RentalConfig?.timing?.debounceDelay || 300;
                    this.searchTimeout = setTimeout(async () => {
                        await this.performSearch(query);
                    }, debounceDelay);
                });
            }

            /**
             * Perform customer search via API
             * @param {string} query - Search query string
             */
            async performSearch(query) {
                try {
                    window.Logger?.debug('CustomerSearch: Performing search', { query, queryLength: query.length });

                    const response = await fetch(
                        `${window.RentalConfig.getApiUrl('searchCustomers')}?query=${encodeURIComponent(query)}`,
                        {
                            headers: window.RentalConfig.getApiHeaders()
                        }
                    );

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const data = await response.json();
                    this.displaySearchResults(data.customers, query);

                    window.Logger?.debug('CustomerSearch: Search completed successfully', {
                        query,
                        resultCount: data.customers.length
                    });

                } catch (error) {
                    window.Logger?.error('CustomerSearch: Search failed', error);
                    this.showError('Unable to search customers. Please try again.');
                }
            }

            /**
             * Display search results in the dropdown
             * @param {Array} customers - Array of customer objects
             * @param {string} query - Original search query
             */
            displaySearchResults(customers, query) {
                this.searchResults.innerHTML = '';

                if (customers.length === 0) {
                    this.searchResults.innerHTML = '<div class="p-2 text-sm text-gray-500">No customers found</div>';
                    this.searchResults.classList.remove('hidden');
                    window.Logger?.debug('CustomerSearch: No customers found', { query });
                    return;
                }

                customers.forEach(customer => {
                    const div = document.createElement('div');
                    div.className = 'p-2 hover:bg-gray-100 cursor-pointer text-sm';
                    div.innerHTML = `
                    <div class="font-medium">${this.escapeHtml(customer.name)}</div>
                    <div class="text-gray-600">${this.escapeHtml(customer.phone || '')}</div>
                `;
                    div.addEventListener('click', () => this.populateCustomerFields(customer));
                    this.searchResults.appendChild(div);
                });

                this.searchResults.classList.remove('hidden');
                window.Logger?.debug('CustomerSearch: Results displayed', {
                    query,
                    customerCount: customers.length
                });
            }

            /**
             * Show error message in search results
             * @param {string} message - Error message to display
             */
            showError(message) {
                this.searchResults.innerHTML = `<div class="p-2 text-sm text-red-600">${this.escapeHtml(message)}</div>`;
                this.searchResults.classList.remove('hidden');
            }

            /**
             * Escape HTML to prevent XSS
             * @param {string} text - Text to escape
             * @returns {string} Escaped text
             */
            escapeHtml(text) {
                if (!text) return '';
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            /**
 * Setup click outside handler to hide search results
 */
            setupClickOutside() {
                document.addEventListener('click', (event) => {
                    if (!this.searchInput.contains(event.target) && !this.searchResults.contains(event.target)) {
                        this.searchResults.classList.add('hidden');
                        window.Logger?.debug('CustomerSearch: Search results hidden due to outside click');
                    }
                });
            }

            /**
             * Cleanup method for removing event listeners and resetting state
             */
            destroy() {
                if (this.searchTimeout) {
                    clearTimeout(this.searchTimeout);
                }
                this.clearSearch();
                window.Logger?.debug('CustomerSearch: Destroyed');
            }
        }

        // Export CustomerSearch class to global scope
        window.CustomerSearch = CustomerSearch;

    } else {
        window.Logger?.debug('CustomerSearch already exists, skipping initialization');
    }

})(); // End of IIFE 