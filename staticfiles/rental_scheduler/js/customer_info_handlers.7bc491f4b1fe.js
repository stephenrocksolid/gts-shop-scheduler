/**
 * CustomerInfoHandlers - Manages customer information form interactions
 * Handles customer search initialization and file input management
 */

// Wrap in IIFE to avoid global conflicts
(function () {
    'use strict';

    // Defensive loading - only declare CustomerInfoHandlers if it doesn't already exist
    if (typeof window.CustomerInfoHandlers === 'undefined') {

        class CustomerInfoHandlers {
            constructor(config = {}) {
                // Configuration and dependencies
                this.config = config;
                this.customerSearch = null;
                this.fileInput = null;
                this.fileNameDisplay = null;
                this.currentPath = '';

                // State management
                this.isInitialized = false;

                // Initialize if dependencies are available
                this.initialize();
            }

            /**
             * Initialize the customer info handlers module
             */
            initialize() {
                // Check for required dependencies
                if (!window.RentalConfig) {
                    window.Logger?.error('CustomerInfoHandlers: RentalConfig is required but not available');
                    return;
                }

                if (!window.CustomerSearch) {
                    window.Logger?.error('CustomerInfoHandlers: CustomerSearch is required but not available');
                    return;
                }

                if (!window.Logger) {
                    console.warn('CustomerInfoHandlers: Logger not available, falling back to console logging');
                }

                // Get configuration from DOM or config parameter
                const contextConfig = this.extractDjangoContext();
                if (!contextConfig) {
                    window.Logger?.error('CustomerInfoHandlers: Could not extract Django context configuration');
                    return;
                }

                // Initialize customer search
                this.initializeCustomerSearch(contextConfig);

                // Initialize file input handling
                this.initializeFileInputHandling(contextConfig);

                this.isInitialized = true;
                window.Logger?.debug('CustomerInfoHandlers initialized successfully');
            }

            /**
             * Extract Django context from DOM data attributes or JSON script tag
             * @returns {Object|null} Configuration object with form field IDs
             */
            extractDjangoContext() {
                // Method 1: Try to get from JSON script tag
                const contextScript = document.getElementById('customer-info-context');
                if (contextScript) {
                    try {
                        const context = JSON.parse(contextScript.textContent);
                        window.Logger?.debug('CustomerInfoHandlers: Using JSON context', context);
                        return context;
                    } catch (error) {
                        window.Logger?.warn('CustomerInfoHandlers: Failed to parse JSON context', error);
                    }
                }

                // Method 2: Try to get from data attributes on customer info container
                const customerInfoContainer = document.querySelector('[data-customer-info-config]');
                if (customerInfoContainer) {
                    try {
                        const context = JSON.parse(customerInfoContainer.dataset.customerInfoConfig);
                        window.Logger?.debug('CustomerInfoHandlers: Using data attribute context', context);
                        return context;
                    } catch (error) {
                        window.Logger?.warn('CustomerInfoHandlers: Failed to parse data attribute context', error);
                    }
                }

                // Method 3: Fallback to hardcoded element IDs (less flexible)
                const fallbackContext = this.buildFallbackContext();
                if (fallbackContext) {
                    window.Logger?.debug('CustomerInfoHandlers: Using fallback context', fallbackContext);
                    return fallbackContext;
                }

                return null;
            }

            /**
             * Build fallback context by finding elements in DOM
             * @returns {Object|null} Fallback configuration object
             */
            buildFallbackContext() {
                // Try to find common form field patterns
                const customerIdInput = document.querySelector('input[name*="customer_id"]');
                const customerNameInput = document.querySelector('input[name*="customer_name"]');
                const fileInput = document.querySelector('input[type="file"][name*="license"]');

                if (!customerIdInput || !customerNameInput) {
                    return null;
                }

                return {
                    customerIdInputId: customerIdInput.id,
                    formFieldIds: {
                        name: customerNameInput.id,
                        phone: document.querySelector('input[name*="customer_phone"]')?.id || '',
                        street_address: document.querySelector('input[name*="street_address"]')?.id || '',
                        city: document.querySelector('input[name*="city"]')?.id || '',
                        state: document.querySelector('input[name*="state"]')?.id || '',
                        zip_code: document.querySelector('input[name*="zip_code"]')?.id || '',
                        po_number: document.querySelector('input[name*="po_number"]')?.id || '',
                        drivers_license_number: document.querySelector('input[name*="drivers_license_number"]')?.id || ''
                    },
                    fileInputId: fileInput?.id || '',
                    currentLicensePath: ''
                };
            }

            /**
             * Initialize customer search functionality
             * @param {Object} contextConfig - Configuration from Django context
             */
            initializeCustomerSearch(contextConfig) {
                try {
                    this.customerSearch = new window.CustomerSearch({
                        searchInputId: 'customer_search',
                        searchResultsId: 'customer_search_results',
                        customerIdInputId: contextConfig.customerIdInputId,
                        formFieldIds: contextConfig.formFieldIds
                    });

                    window.Logger?.debug('CustomerInfoHandlers: Customer search initialized', {
                        searchInputId: 'customer_search',
                        customerIdInputId: contextConfig.customerIdInputId,
                        fieldCount: Object.keys(contextConfig.formFieldIds).length
                    });

                } catch (error) {
                    window.Logger?.error('CustomerInfoHandlers: Failed to initialize customer search', error);
                }
            }

            /**
             * Initialize file input handling for license scan uploads
             * @param {Object} contextConfig - Configuration from Django context
             */
            initializeFileInputHandling(contextConfig) {
                if (!contextConfig.fileInputId) {
                    window.Logger?.debug('CustomerInfoHandlers: No file input configuration found, skipping file handling');
                    return;
                }

                this.fileInput = document.getElementById(contextConfig.fileInputId);
                this.fileNameDisplay = document.getElementById('file-name-display');
                this.currentPath = contextConfig.currentLicensePath || '';

                if (!this.fileInput) {
                    window.Logger?.warn('CustomerInfoHandlers: File input element not found', {
                        fileInputId: contextConfig.fileInputId
                    });
                    return;
                }

                if (!this.fileNameDisplay) {
                    window.Logger?.warn('CustomerInfoHandlers: File name display element not found');
                    return;
                }

                // Setup file input change handler
                this.setupFileInputHandler();

                window.Logger?.debug('CustomerInfoHandlers: File input handling initialized', {
                    fileInputId: contextConfig.fileInputId,
                    hasCurrentPath: !!this.currentPath
                });
            }

            /**
             * Setup file input change event handler
             */
            setupFileInputHandler() {
                if (!this.fileInput || !this.fileNameDisplay) return;

                this.fileInput.addEventListener('change', (e) => {
                    this.handleFileInputChange(e);
                });
            }

            /**
             * Handle file input change event
             * @param {Event} e - File input change event
             */
            handleFileInputChange(e) {
                const fileInput = e.target;

                try {
                    if (fileInput.files.length > 0) {
                        const fileName = fileInput.files[0].name;
                        this.fileNameDisplay.textContent = fileName;

                        window.Logger?.debug('CustomerInfoHandlers: File selected', {
                            fileName,
                            fileSize: fileInput.files[0].size,
                            fileType: fileInput.files[0].type
                        });

                    } else if (this.currentPath) {
                        this.fileNameDisplay.textContent = this.currentPath;
                        window.Logger?.debug('CustomerInfoHandlers: File cleared, showing current path');

                    } else {
                        this.fileNameDisplay.textContent = '';
                        window.Logger?.debug('CustomerInfoHandlers: File cleared, no current path');
                    }

                } catch (error) {
                    window.Logger?.error('CustomerInfoHandlers: Error handling file input change', error);
                    this.fileNameDisplay.textContent = 'Error reading file';
                }
            }

            /**
             * Update current license path (called when form is updated)
             * @param {string} path - New current path
             */
            updateCurrentPath(path) {
                this.currentPath = path || '';

                // Update display if no file is currently selected
                if (this.fileInput && this.fileNameDisplay && this.fileInput.files.length === 0) {
                    this.fileNameDisplay.textContent = this.currentPath;
                }

                window.Logger?.debug('CustomerInfoHandlers: Current path updated', { path: this.currentPath });
            }

            /**
             * Get current customer search instance
             * @returns {CustomerSearch|null} Customer search instance
             */
            getCustomerSearch() {
                return this.customerSearch;
            }

            /**
             * Refresh customer search functionality (useful after form updates)
             */
            refreshCustomerSearch() {
                if (this.customerSearch && typeof this.customerSearch.refresh === 'function') {
                    this.customerSearch.refresh();
                    window.Logger?.debug('CustomerInfoHandlers: Customer search refreshed');
                }
            }

            /**
             * Cleanup method for removing event listeners and resetting state
             */
            destroy() {
                if (this.customerSearch && typeof this.customerSearch.destroy === 'function') {
                    this.customerSearch.destroy();
                }

                this.isInitialized = false;
                window.Logger?.debug('CustomerInfoHandlers: Destroyed');
            }
        }

        // Export CustomerInfoHandlers class to global scope
        window.CustomerInfoHandlers = CustomerInfoHandlers;

        // Auto-initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', function () {
            // Wait for dependencies to be available
            if (window.RentalConfig && window.CustomerSearch) {
                window.customerInfoHandlers = new CustomerInfoHandlers();
            } else {
                // Wait a bit for dependencies to load
                setTimeout(() => {
                    if (window.RentalConfig && window.CustomerSearch) {
                        window.customerInfoHandlers = new CustomerInfoHandlers();
                    } else {
                        console.error('CustomerInfoHandlers: Required dependencies not available (RentalConfig, CustomerSearch)');
                    }
                }, 100);
            }
        });

    } else {
        window.Logger?.debug('CustomerInfoHandlers already exists, skipping initialization');
    }

})(); // End of IIFE 