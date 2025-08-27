/**
 * Production-safe logging utility for the GTS Rental Scheduler
 * Provides environment-aware logging with proper error handling
 */

// Wrap in IIFE to avoid global conflicts
(function () {
    'use strict';

    // Defensive loading - only declare Logger if it doesn't already exist
    if (typeof window.Logger === 'undefined') {

        class Logger {
            constructor() {
                this.isDevelopment = this.detectEnvironment();
                this.logLevel = this.isDevelopment ? 'debug' : 'error';
                // Will be set after RentalConfig is available
                this.errorEndpoint = null;
            }

            /**
             * Detect if we're in development environment
             * @returns {boolean} True if in development
             */
            detectEnvironment() {
                // Check for development indicators
                return (
                    window.location.hostname === 'localhost' ||
                    window.location.hostname === '127.0.0.1' ||
                    window.location.hostname.includes('dev') ||
                    document.querySelector('meta[name="environment"]')?.content === 'development' ||
                    localStorage.getItem('debug') === 'true'
                );
            }

            /**
             * Log debug information (development only)
             * @param {string} message - Debug message
             * @param {*} data - Optional data to log
             */
            debug(message, data = null) {
                if (this.isDevelopment && this.shouldLog('debug')) {
                    console.log(`[DEBUG] ${message}`, data || '');
                }
            }

            /**
             * Log informational message
             * @param {string} message - Info message
             * @param {*} data - Optional data to log
             */
            info(message, data = null) {
                if (this.shouldLog('info')) {
                    if (this.isDevelopment) {
                        console.info(`[INFO] ${message}`, data || '');
                    }
                }
            }

            /**
             * Log warning message
             * @param {string} message - Warning message
             * @param {*} data - Optional data to log
             */
            warn(message, data = null) {
                if (this.shouldLog('warn')) {
                    if (this.isDevelopment) {
                        console.warn(`[WARN] ${message}`, data || '');
                    }
                    // In production, could send to monitoring service
                    this.reportToMonitoring('warning', message, data);
                }
            }

            /**
             * Log error message
             * @param {string} message - Error message
             * @param {Error|*} error - Error object or additional data
             */
            error(message, error = null) {
                if (this.shouldLog('error')) {
                    if (this.isDevelopment) {
                        console.error(`[ERROR] ${message}`, error || '');
                    }

                    // Always report errors in production for monitoring
                    this.reportError(message, error);
                }
            }

            /**
             * Check if we should log at the given level
             * @param {string} level - Log level to check
             * @returns {boolean} True if should log
             */
            shouldLog(level) {
                const levels = ['debug', 'info', 'warn', 'error'];
                const currentLevelIndex = levels.indexOf(this.logLevel);
                const requestedLevelIndex = levels.indexOf(level);
                return requestedLevelIndex >= currentLevelIndex;
            }

            /**
             * Report error to backend monitoring system
             * @param {string} message - Error message
             * @param {Error|*} error - Error details
             */
            async reportError(message, error = null) {
                // Get error endpoint from config if available
                const errorEndpoint = window.RentalConfig?.getApiUrl('sendErrorReport') || this.errorEndpoint;

                if (!this.isDevelopment && errorEndpoint) {
                    try {
                        const errorData = {
                            message: message,
                            error: error ? error.toString() : null,
                            stack: error && error.stack ? error.stack : null,
                            url: window.location.href,
                            userAgent: navigator.userAgent,
                            timestamp: new Date().toISOString(),
                            component: 'rental_calculator'
                        };

                        const response = await fetch(errorEndpoint, {
                            method: 'POST',
                            headers: window.RentalConfig?.getApiHeaders() || {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': this.getCSRFToken()
                            },
                            body: JSON.stringify(errorData)
                        });

                        if (!response.ok) {
                            // Fallback: log to console if error reporting fails
                            if (this.isDevelopment) {
                                console.error('Failed to report error to backend:', errorData);
                            }
                        }
                    } catch (reportingError) {
                        // Silent fail - don't create error loops
                        if (this.isDevelopment) {
                            console.error('Error reporting failed:', reportingError);
                        }
                    }
                }
            }

            /**
             * Report non-error events to monitoring (warnings, info)
             * @param {string} level - Log level
             * @param {string} message - Message
             * @param {*} data - Additional data
             */
            reportToMonitoring(level, message, data = null) {
                // Placeholder for future monitoring integration
                // Could integrate with services like Sentry, LogRocket, etc.
                if (this.isDevelopment) {
                    console.log(`[MONITORING] ${level.toUpperCase()}: ${message}`, data);
                }
            }

            /**
             * Get CSRF token for API requests
             * @returns {string} CSRF token
             */
            getCSRFToken() {
                // Try meta tag first
                const metaToken = document.querySelector('meta[name="csrf-token"]');
                if (metaToken) {
                    return metaToken.getAttribute('content');
                }

                // Try cookie
                const cookieToken = this.getCookie('csrftoken');
                if (cookieToken) {
                    return cookieToken;
                }

                // Try hidden input
                const hiddenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
                if (hiddenInput) {
                    return hiddenInput.value;
                }

                return '';
            }

            /**
             * Get cookie value by name
             * @param {string} name - Cookie name
             * @returns {string|null} Cookie value
             */
            getCookie(name) {
                const value = `; ${document.cookie}`;
                const parts = value.split(`; ${name}=`);
                if (parts.length === 2) {
                    return parts.pop().split(';').shift();
                }
                return null;
            }

            /**
             * Create user-friendly error display
             * @param {HTMLElement} element - Element to show error in
             * @param {string} userMessage - User-friendly message
             * @param {boolean} temporary - Whether to auto-clear the error
             */
            showUserError(element, userMessage, temporary = true) {
                if (!element) return;

                // Store original value
                const originalValue = element.value || element.textContent;
                const originalClass = element.className;

                // Apply error styling
                element.value = userMessage;
                element.classList.add('error', 'bg-red-50', 'border-red-300', 'text-red-700');

                // Auto-clear if temporary
                if (temporary) {
                    const errorTimeout = window.RentalConfig?.timing?.errorDisplayTimeout || 3000;
                    setTimeout(() => {
                        element.value = originalValue;
                        element.className = originalClass;
                    }, errorTimeout);
                }
            }

            /**
             * Create loading state for element
             * @param {HTMLElement} element - Element to show loading state
             * @param {string} loadingMessage - Loading message
             */
            showLoading(element, loadingMessage = 'Loading...') {
                if (!element) return;

                element.dataset.originalValue = element.value || element.textContent;
                element.dataset.originalDisabled = element.disabled || 'false';

                element.value = loadingMessage;
                element.disabled = true;
                element.classList.add('loading', 'bg-gray-50', 'text-gray-500');
            }

            /**
             * Hide loading state for element
             * @param {HTMLElement} element - Element to restore
             * @param {string} newValue - New value to set (optional)
             */
            hideLoading(element, newValue = null) {
                if (!element) return;

                const originalValue = element.dataset.originalValue;
                const originalDisabled = element.dataset.originalDisabled === 'true';

                element.value = newValue || originalValue || '';
                element.disabled = originalDisabled;
                element.classList.remove('loading', 'bg-gray-50', 'text-gray-500');

                // Clean up data attributes
                delete element.dataset.originalValue;
                delete element.dataset.originalDisabled;
            }
        }

        // Create global logger instance only if it doesn't exist
        window.Logger = new Logger();

        // Export for module systems if needed
        if (typeof module !== 'undefined' && module.exports) {
            module.exports = Logger;
        }

    } else {
        // Logger already exists - do nothing
        console.log('[INFO] Logger already exists, skipping initialization');
    }

})(); // End of IIFE 