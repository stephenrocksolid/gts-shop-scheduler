/**
 * RentalCalculator - JavaScript module for rental calculations via API
 * Provides consistent calculations by calling Django RentalCalculator service endpoints
 */
// Prevent redeclaration errors during browser cache transitions
if (typeof RentalCalculator === 'undefined') {
    window.RentalCalculator = class RentalCalculator {
        constructor() {
            this.constants = null;
            this.constantsLoaded = false;
            this.constantsLoadedAt = null;
            this.cache = new Map(); // General cache for API responses
        }

        /**
 * Load calculation constants from the API with intelligent caching
 * @returns {Promise<Object>} Calculation constants
 */
        async getCalculationConstants() {
            const now = Date.now();
            const cacheTimeout = window.RentalConfig?.timing?.constantsCacheTimeout || 5 * 60 * 1000; // 5 min default

            // Check if we have valid cached constants
            if (this.constantsLoaded && this.constants && this.constantsLoadedAt) {
                const isExpired = (now - this.constantsLoadedAt) > cacheTimeout;

                if (!isExpired) {
                    window.Logger?.debug('Using cached calculation constants');
                    return this.constants;
                } else {
                    window.Logger?.debug('Calculation constants cache expired, refetching');
                }
            }

            try {
                window.Logger?.debug('Fetching calculation constants from API');

                const response = await fetch(window.RentalConfig.getApiUrl('calculationConstants'), {
                    method: 'GET',
                    headers: window.RentalConfig.getApiHeaders()
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                this.constants = await response.json();
                this.constantsLoaded = true;
                this.constantsLoadedAt = now;

                window.Logger?.debug('Calculation constants loaded and cached');
                return this.constants;
            } catch (error) {
                window.Logger.error('Error loading calculation constants:', error);

                // If we have expired constants, return them as fallback
                if (this.constants) {
                    window.Logger?.warn('Using expired constants as fallback');
                    return this.constants;
                }

                throw new Error('Failed to load calculation constants');
            }
        }

        /**
         * Calculate a complete rental quote
         * @param {Object} quoteData - Quote parameters
         * @returns {Promise<Object>} Complete calculation results
         */
        async calculateQuote(quoteData) {
            try {
                // Format datetime fields for API if they exist
                const formattedData = { ...quoteData };
                if (formattedData.start_datetime) {
                    formattedData.start_datetime = this.formatDateTimeForAPI(formattedData.start_datetime);
                }
                if (formattedData.end_datetime) {
                    formattedData.end_datetime = this.formatDateTimeForAPI(formattedData.end_datetime);
                }
                window.Logger.debug('calculateQuote payload:', formattedData);

                const response = await fetch(window.RentalConfig.getApiUrl('calculateRentalQuote'), {
                    method: 'POST',
                    headers: window.RentalConfig.getApiHeaders(),
                    body: JSON.stringify(formattedData)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
                }

                const json = await response.json();
                window.Logger.debug('calculateQuote response:', json);
                return json;
            } catch (error) {
                window.Logger.error('Error calculating quote:', error);
                throw error;
            }
        }

        /**
         * Calculate duration information
         * @param {string} startDateTime - Start date/time string
         * @param {string} endDateTime - End date/time string
         * @returns {Promise<Object>} Duration information
         */
        async calculateDurationInfo(startDateTime, endDateTime) {
            try {
                const response = await fetch(window.RentalConfig.getApiUrl('calculateDuration'), {
                    method: 'POST',
                    headers: window.RentalConfig.getApiHeaders(),
                    body: JSON.stringify({
                        start_datetime: this.formatDateTimeForAPI(startDateTime),
                        end_datetime: this.formatDateTimeForAPI(endDateTime)
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();
            } catch (error) {
                window.Logger.error('Error calculating duration:', error);
                throw error;
            }
        }

        /**
         * Format duration information for display - matches Python RentalCalculator.format_duration_display
         * @param {Object} durationInfo - Duration info from API
         * @returns {string} Formatted duration string
         */
        formatDuration(durationInfo) {
            if (!durationInfo) {
                return 'Invalid duration';
            }

            const { rate_category, full_days, has_half_day, days, remainder } = durationInfo;

            if (rate_category === 'half_day') {
                return 'Half Day';
            }

            if (rate_category === 'weekly') {
                return '1 week';
            }

            if (rate_category === 'daily') {
                // Follow the same logic as calculate_base_rate for billing consistency
                if (remainder <= 0) {
                    // No remainder, just show full days
                    const displayDays = Math.max(full_days, 1); // Minimum 1 day for daily rate
                    return `${displayDays} day${displayDays !== 1 ? 's' : ''}`;
                } else if (has_half_day) {
                    // Remainder qualifies as half-day increment
                    return `${full_days}½ days`;
                } else {
                    // Remainder is more than half-day, so we charge (and display) another full day
                    const billedDays = full_days + 1;
                    return `${billedDays} day${billedDays !== 1 ? 's' : ''}`;
                }
            }

            if (rate_category === 'extended') {
                const roundedDays = Math.ceil(days);
                return `${roundedDays} day${roundedDays !== 1 ? 's' : ''}`;
            }

            // Fallback for unknown categories - matches Python logic
            const intDays = Math.floor(days);
            return `${intDays} day${intDays !== 1 ? 's' : ''}`;
        }

        /**
         * Format rate information for display
         * @param {Object} rateInfo - Rate info from API
         * @returns {string} Formatted rate string
         */
        formatRate(rateInfo) {
            if (!rateInfo) {
                return '$0.00';
            }

            const amount = rateInfo.unit_rate !== undefined ? rateInfo.unit_rate : rateInfo.base_rate;

            if (amount === undefined) {
                return '$0.00';
            }

            const { duration_info } = rateInfo;
            const formattedRate = this.formatCurrency(amount);

            if (duration_info) {
                const { rate_category } = duration_info;
                if (rate_category) {
                    const displayCategory = rate_category.charAt(0).toUpperCase() + rate_category.slice(1).replace('_', ' ');
                    return `${formattedRate} (${displayCategory})`;
                }
            }

            return formattedRate;
        }

        /**
         * Format currency values
         * @param {number|string} amount - Amount to format
         * @returns {string} Formatted currency string
         */
        formatCurrency(amount) {
            const value = parseFloat(amount) || 0;
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(value);
        }

        /**
         * Format datetime string for API consumption
         * Converts from form input format to Django-expected format
         * @param {string} dateTimeString - DateTime string from form input
         * @returns {string} Formatted datetime string (YYYY-MM-DD HH:MM:SS)
         */
        formatDateTimeForAPI(dateTimeString) {
            if (!dateTimeString || typeof dateTimeString !== 'string') {
                return '';
            }

            try {
                const pattern = /^(\d{1,2})\/(\d{1,2})\/(\d{4})\s+(\d{1,2}):(\d{2})\s*(AM|PM)$/i;
                const match = dateTimeString.match(pattern);
                if (match) {
                    let [, month, day, year, hour, minute, ampm] = match;
                    hour = parseInt(hour, 10);
                    if (ampm.toUpperCase() === 'PM' && hour !== 12) {
                        hour += 12;
                    }
                    if (ampm.toUpperCase() === 'AM' && hour === 12) {
                        hour = 0;
                    }
                    const hours24 = String(hour).padStart(2, '0');
                    const formatted = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')} ${hours24}:${minute}:00`;
                    return formatted;
                }

                let date = new Date(dateTimeString);
                if (isNaN(date.getTime())) {
                    window.Logger.error('Unable to parse datetime:', dateTimeString);
                    return dateTimeString;
                }
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                const seconds = String(date.getSeconds()).padStart(2, '0');
                return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
            } catch (error) {
                window.Logger.error('Error formatting datetime for API:', error, 'Input:', dateTimeString);
                return dateTimeString;
            }
        }

        // CSRF token handling is now centralized in RentalConfig

        /**
         * Show loading state for an element
         * @param {HTMLElement} element - Element to show loading state
         * @param {string} originalText - Original text to restore later
         */
        showLoading(element, originalText = 'Loading...') {
            return window.Logger.showLoading(element, originalText);
        }

        /**
         * Hide loading state for an element
         * @param {HTMLElement} element - Element to hide loading state
         * @param {string} newValue - New value to set
         */
        hideLoading(element, newValue = null) {
            return window.Logger.hideLoading(element, newValue);
        }

        /**
         * Show error state for an element
         * @param {HTMLElement} element - Element to show error state
         * @param {string} errorMessage - Error message to display
         */
        showError(element, errorMessage = 'Error calculating') {
            return window.Logger.showUserError(element, errorMessage, true);
        }

        /**
         * Validate form data before sending to API
         * @param {Object} formData - Form data to validate
         * @returns {Object} Validation result
         */
        validateFormData(formData) {
            const errors = [];

            // Required fields
            if (!formData.trailer_id) {
                errors.push('Trailer is required');
            }

            if (!formData.start_datetime) {
                errors.push('Start date/time is required');
            }

            if (!formData.end_datetime) {
                errors.push('End date/time is required');
            }

            // Date validation
            if (formData.start_datetime && formData.end_datetime) {
                const startDate = new Date(formData.start_datetime);
                const endDate = new Date(formData.end_datetime);

                if (isNaN(startDate.getTime())) {
                    errors.push('Invalid start date');
                }

                if (isNaN(endDate.getTime())) {
                    errors.push('Invalid end date');
                }

                if (startDate >= endDate) {
                    errors.push('End date must be after start date');
                }
            }

            // Numeric validations
            const numericFields = ['custom_rate', 'extra_mileage', 'down_payment', 'furniture_blanket_count', 'strap_chain_count'];
            numericFields.forEach(field => {
                if (formData[field] !== undefined && formData[field] !== '' && formData[field] !== null) {
                    const value = parseFloat(formData[field]);
                    if (isNaN(value) || value < 0) {
                        errors.push(`${field.replace('_', ' ')} must be a valid positive number`);
                    }
                }
            });

            return {
                isValid: errors.length === 0,
                errors: errors
            };
        }

        /**
 * Clear calculation constants cache (useful for testing or forced refresh)
 */
        clearConstantsCache() {
            this.constants = null;
            this.constantsLoaded = false;
            this.constantsLoadedAt = null;
            window.Logger?.debug('Calculation constants cache cleared');
        }

        /**
         * Clear all caches
         */
        clearAllCaches() {
            this.clearConstantsCache();
            this.cache.clear();
            window.Logger?.debug('All RentalCalculator caches cleared');
        }

        /**
         * Create a debounced version of a function
         * @param {Function} func - Function to debounce
         * @param {number} delay - Delay in milliseconds (uses config default if not provided)
         * @returns {Function} Debounced function
         */
        debounce(func, delay = null) {
            const debounceDelay = delay || window.RentalConfig?.timing?.debounceDelay || 300;
            let timeoutId;
            return function (...args) {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => func.apply(this, args), debounceDelay);
            };
        }
    };

    // Create a global instance
    window.RentalCalculator = new window.RentalCalculator();
}