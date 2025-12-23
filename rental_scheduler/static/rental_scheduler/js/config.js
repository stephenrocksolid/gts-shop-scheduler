/**
 * Centralized configuration for GTS Rental Scheduler
 * Single source of truth for all URLs, field mappings, and settings
 */

// Wrap in IIFE to avoid global conflicts
(function () {
    'use strict';

    // Defensive loading - only declare RentalConfig if it doesn't already exist
    if (typeof window.RentalConfig === 'undefined') {

        class RentalConfig {
            constructor() {
                this.environment = this.detectEnvironment();
                this.baseUrl = this.getBaseUrl();
                this.initializeConfig();
            }

            /**
             * Detect current environment
             * @returns {string} Environment name (development|staging|production)
             */
            detectEnvironment() {
                const hostname = window.location.hostname;
                const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';
                const isDev = hostname.includes('dev') || isLocalhost;
                const isStaging = hostname.includes('staging') || hostname.includes('stage');

                // Check for explicit environment meta tag
                const envMeta = document.querySelector('meta[name="environment"]');
                if (envMeta) {
                    return envMeta.content;
                }

                // Legacy cleanup: remove deprecated localStorage overrides (rental_env, rental_debug)
                // These were hidden debug settings with no UI to clear them.
                try {
                    localStorage.removeItem('rental_env');
                    localStorage.removeItem('rental_debug');
                } catch (e) {
                    // Ignore storage errors
                }

                // Auto-detect based on hostname
                if (isDev) return 'development';
                if (isStaging) return 'staging';
                return 'production';
            }

            /**
             * Get base URL for API calls
             * @returns {string} Base URL
             */
            getBaseUrl() {
                return window.location.origin;
            }

            /**
             * Initialize all configuration objects
             */
            initializeConfig() {
                // API Endpoints
                this.api = {
                    calculateDuration: '/api/calculate-duration/',
                    getAvailableTrailers: '/api/contracts/get-available-trailers/',
                    sendErrorReport: '/api/send-error-report/',
                    searchCustomers: '/api/search_customers/',
                    updateContractStatus: '/api/contracts/{id}/update-status/',
                    calendarData: '/api/calendar-data/',
                    browseFolders: '/api/browse-folders/',
                    validateNetworkPath: '/api/validate-network-path/',
                    testNetworkConnection: '/api/test-network-connection/',
                    networkStatus: '/api/network-status/',
                    contractPdf: '/contracts/{id}/pdf/'
                };

                // Field ID mappings - commonly used form field IDs
                this.fieldIds = {
                    // Date/Time fields
                    startDateTime: 'id_start_datetime',
                    endDateTime: 'id_end_datetime',
                    returnDateTime: 'id_return_datetime',

                    // Trailer fields
                    category: 'id_category',
                    trailer: 'id_trailer',

                    // Rate fields
                    customRate: 'id_custom_rate',
                    extraMileage: 'id_extra_mileage',

                    // Add-on fields
                    includesWinch: 'id_includes_winch',
                    includesHitchBar: 'id_includes_hitch_bar',
                    furnitureBlanketCount: 'id_furniture_blanket_count',
                    strapChainCount: 'id_strap_chain_count',
                    hasEveningPickup: 'id_has_evening_pickup',

                    // Payment fields
                    downPayment: 'id_down_payment',
                    paymentTiming: 'id_payment_timing',

                    // Customer fields
                    customerSearch: 'customer_search',
                    customerId: 'id_customer_id',
                    customerName: 'id_customer_name',
                    customerPhone: 'id_customer_phone',
                    customerStreetAddress: 'id_customer_street_address',
                    customerCity: 'id_customer_city',
                    customerState: 'id_customer_state',
                    customerZipCode: 'id_customer_zip_code',
                    customerPoNumber: 'id_customer_po_number',
                    customerDriversLicenseNumber: 'id_customer_drivers_license_number',
                    customerDriversLicenseScan: 'id_customer_drivers_license_scan',

                    // Status fields
                    isReturned: 'id_is_returned',
                    isPickedUp: 'id_is_picked_up'
                };

                // Display element IDs
                this.displayIds = {
                    durationDisplay: 'duration_display',
                    rateDisplay: 'rate_display',
                    subtotalDisplay: 'subtotal_display',
                    taxDisplay: 'tax_display',
                    balanceDueDisplay: 'balance_due_display',
                    rateTypeLabel: 'rate_type_label',
                    customerSearchResults: 'customer_search_results',
                    calendarLoading: 'calendar-loading',
                    folderList: 'folder-list',
                    returnDateTimeContainer: 'return_datetime_container'
                };

                // Quick Schedule button IDs
                this.quickScheduleIds = {
                    morningHalfDay: 'qs_morning_half_day',
                    afternoonHalfDay: 'qs_afternoon_half_day',
                    fullDay: 'qs_full_day',
                    weekly: 'qs_weekly'
                };

                // Filter IDs (for calendar page)
                this.filterIds = {
                    categoryFilter: 'category-filter',
                    trailerFilter: 'trailer-filter',
                    statusFilter: 'status-filter'
                };

                // Timing and performance settings
                this.timing = {
                    // API timeouts (milliseconds)
                    apiTimeout: this.environment === 'development' ? 10000 : 5000,

                    // UI timeouts
                    errorDisplayTimeout: 3000,
                    loadingMinimumTimeout: 500,
                    debounceDelay: 300,
                    quickScheduleDelay: 100,
                    focusDelay: 200,

                    // Cache settings
                    constantsCacheTimeout: 5 * 60 * 1000, // 5 minutes
                    trailerCacheTimeout: 2 * 60 * 1000,   // 2 minutes
                };

                // UI settings
                this.ui = {
                    // CSS classes for states
                    classes: {
                        error: ['error', 'bg-red-50', 'border-red-300', 'text-red-700'],
                        loading: ['loading', 'bg-gray-50', 'text-gray-500'],
                        success: ['bg-green-50', 'border-green-300', 'text-green-700'],
                        warning: ['bg-yellow-50', 'border-yellow-300', 'text-yellow-700']
                    },

                    // Default messages
                    messages: {
                        selectTrailerAndDates: 'Select trailer and dates to see rate',
                        selectDates: 'Select dates to see rate',
                        selectDatesForDuration: 'Select start and end dates to see duration',
                        noAvailableTrailers: 'No available trailers for selected dates',
                        errorLoadingTrailers: 'Unable to load trailers',
                        errorLoadingRates: 'Unable to load rates',
                        errorCalculatingDuration: 'Unable to calculate duration',
                        errorCalculating: 'Error calculating',
                        loading: 'Loading...',
                        calculating: 'Calculating...',
                        endDateAfterStart: 'End date must be after start date'
                    },

                    // Quick Schedule settings
                    quickSchedule: {
                        maxFullDays: 4,
                        weeklyDays: 7,
                        defaultTimes: {
                            morningStart: '7:00 AM',
                            morningEnd: '12:00 PM',
                            afternoonStart: '1:00 PM',
                            afternoonEnd: '6:00 PM',
                            fullDayStart: '7:00 AM',
                            fullDayEnd: '5:00 PM'
                        }
                    }
                };

                // Status Colors - Single Source of Truth (matches CSS variables)
                this.colors = {
                    status: {
                        pending: '#B45309',    // amber-700
                        pickedUp: '#16A34A',   // green-600 (changed from green-500 for better contrast)
                        returned: '#3B82F6',   // blue-500
                        overdue: '#C026D3',    // fuchsia-600
                        service: '#DC2626'     // red-600
                    }
                };

                // Environment-specific overrides
                this.applyEnvironmentOverrides();
            }

            /**
             * Apply environment-specific configuration overrides
             */
            applyEnvironmentOverrides() {
                switch (this.environment) {
                    case 'development':
                        // Development-specific settings
                        this.timing.debounceDelay = 100; // Faster response in dev
                        this.timing.constantsCacheTimeout = 30 * 1000; // Shorter cache in dev
                        break;

                    case 'staging':
                        // Staging-specific settings
                        this.timing.apiTimeout = 8000; // Longer timeout for staging
                        break;

                    case 'production':
                        // Production-specific settings
                        this.timing.debounceDelay = 500; // More conservative in production
                        this.timing.constantsCacheTimeout = 10 * 60 * 1000; // Longer cache
                        break;
                }
            }

            /**
             * Get API URL with base URL prepended
             * @param {string} endpoint - API endpoint key
             * @param {Object} params - URL parameters to substitute (e.g., {id: 123})
             * @returns {string} Complete API URL
             */
            getApiUrl(endpoint, params = {}) {
                let url = this.api[endpoint];
                if (!url) {
                    throw new Error(`Unknown API endpoint: ${endpoint}`);
                }

                // Substitute parameters in URL (e.g., /api/contracts/{id}/update-status/)
                Object.keys(params).forEach(key => {
                    url = url.replace(`{${key}}`, params[key]);
                });

                return this.baseUrl + url;
            }

            /**
             * Get field element by ID
             * @param {string} fieldKey - Field key from config
             * @returns {HTMLElement|null} Field element
             */
            getField(fieldKey) {
                const fieldId = this.fieldIds[fieldKey];
                return fieldId ? document.getElementById(fieldId) : null;
            }

            /**
             * Get display element by ID
             * @param {string} displayKey - Display key from config
             * @returns {HTMLElement|null} Display element
             */
            getDisplay(displayKey) {
                const displayId = this.displayIds[displayKey];
                return displayId ? document.getElementById(displayId) : null;
            }

            /**
             * Get quick schedule button by ID
             * @param {string} buttonKey - Button key from config
             * @returns {HTMLElement|null} Button element
             */
            getQuickScheduleButton(buttonKey) {
                const buttonId = this.quickScheduleIds[buttonKey];
                return buttonId ? document.getElementById(buttonId) : null;
            }

            /**
             * Get configuration for specific component
             * @param {string} component - Component name (e.g., 'trailerDetails', 'quickSchedule')
             * @returns {Object} Component-specific configuration
             */
            getComponentConfig(component) {
                const configs = {
                    trailerDetails: {
                        fieldIds: this.fieldIds,
                        displayIds: this.displayIds,
                        timing: this.timing,
                        messages: this.ui.messages,
                        classes: this.ui.classes
                    },
                    quickSchedule: {
                        buttonIds: this.quickScheduleIds,
                        fieldIds: this.fieldIds,
                        timing: this.timing,
                        settings: this.ui.quickSchedule
                    },
                    customerSearch: {
                        fieldIds: this.fieldIds,
                        displayIds: this.displayIds,
                        timing: this.timing
                    },
                    calendar: {
                        filterIds: this.filterIds,
                        displayIds: this.displayIds,
                        api: this.api
                    }
                };

                return configs[component] || {};
            }

            /**
             * Check if we're in development mode
             * @returns {boolean} True if in development
             */
            isDevelopment() {
                return this.environment === 'development';
            }

            /**
             * Check if we're in production mode
             * @returns {boolean} True if in production
             */
            isProduction() {
                return this.environment === 'production';
            }

            /**
             * Get debug status
             * @returns {boolean} True if debugging should be enabled
             */
            isDebugEnabled() {
                // Debug mode is now purely based on environment detection (no localStorage override)
                return this.isDevelopment();
            }

            /**
 * Get CSRF token using multiple fallback strategies
 * @returns {string} CSRF token or empty string
 */
            getCSRFToken() {
                // Strategy 1: Meta tag (most reliable)
                const metaToken = document.querySelector('meta[name="csrf-token"]');
                if (metaToken && metaToken.getAttribute('content')) {
                    return metaToken.getAttribute('content');
                }

                // Strategy 2: Cookie (Django default)
                const cookieToken = this.getCookie('csrftoken');
                if (cookieToken) {
                    return cookieToken;
                }

                // Strategy 3: Hidden form input (Django forms)
                const hiddenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
                if (hiddenInput && hiddenInput.value) {
                    return hiddenInput.value;
                }

                // Strategy 4: Check for newer meta tag variations
                const csrfMeta = document.querySelector('meta[name="csrf_token"]') ||
                    document.querySelector('meta[name="X-CSRFToken"]');
                if (csrfMeta && csrfMeta.getAttribute('content')) {
                    return csrfMeta.getAttribute('content');
                }

                // If in development, log the issue for debugging
                if (this.isDevelopment()) {
                    console.warn('CSRF token not found - API calls may fail', {
                        strategies_checked: ['meta[csrf-token]', 'cookie[csrftoken]', 'input[csrfmiddlewaretoken]', 'meta[csrf_token]'],
                        current_url: window.location.href
                    });
                }

                return '';
            }

            /**
             * Get cookie value by name
             * @param {string} name - Cookie name
             * @returns {string|null} Cookie value
             */
            getCookie(name) {
                if (!document.cookie) {
                    return null;
                }

                const value = `; ${document.cookie}`;
                const parts = value.split(`; ${name}=`);

                if (parts.length === 2) {
                    const cookieValue = parts.pop().split(';').shift();
                    return cookieValue ? decodeURIComponent(cookieValue) : null;
                }

                return null;
            }

            /**
             * Create HTTP headers with CSRF token for API requests
             * @param {Object} additionalHeaders - Additional headers to include
             * @returns {Object} Headers object ready for fetch requests
             */
            getApiHeaders(additionalHeaders = {}) {
                const headers = {
                    'Content-Type': 'application/json',
                    ...additionalHeaders
                };

                const csrfToken = this.getCSRFToken();
                if (csrfToken) {
                    headers['X-CSRFToken'] = csrfToken;
                }

                return headers;
            }

            /**
             * Validate CSRF token and refresh if needed
             * @returns {Promise<boolean>} True if valid token is available
             */
            async validateCSRFToken() {
                const token = this.getCSRFToken();

                if (!token) {
                    if (this.isDevelopment()) {
                        console.warn('No CSRF token available for validation');
                    }
                    return false;
                }

                // In a real implementation, you might want to validate against the server
                // For now, we just check if we have a non-empty token
                return token.length > 0;
            }

            /**
             * Get status color by status name
             * @param {string} status - Status name ('pending', 'pickedUp', 'returned')
             * @returns {string} Hex color code
             */
            getStatusColor(status) {
                return this.colors.status[status] || this.colors.status.pending;
            }

            /**
             * Override configuration at runtime (useful for testing)
             * @param {string} path - Dot notation path (e.g., 'timing.debounceDelay')
             * @param {*} value - New value
             */
            override(path, value) {
                const keys = path.split('.');
                let obj = this;

                for (let i = 0; i < keys.length - 1; i++) {
                    obj = obj[keys[i]];
                }

                obj[keys[keys.length - 1]] = value;
            }
        }

        // Create global config instance
        window.RentalConfig = new RentalConfig();

    } else {
        // Config already exists - do nothing
        console.debug('RentalConfig already exists, skipping initialization');
    }

})(); // End of IIFE 