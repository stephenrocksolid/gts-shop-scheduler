/**
 * Calendar Utils Module
 * 
 * Shared utilities used across calendar modules.
 * Registers: showToast, getCSRFToken, debounce, showError, showSuccess
 */
(function() {
    'use strict';

    GTS.calendar.register('utils', function(proto) {
        /**
         * Show toast notification.
         * Delegates to GTS.toast (shared/toast.js).
         */
        proto.showToast = function(message, type) {
            if (type === undefined) type = 'info';
            if (window.GTS && window.GTS.toast) {
                GTS.toast.show(message, type);
            } else if (window.showToast) {
                window.showToast(message, type);
            } else {
                console.log('[Toast ' + type + ']:', message);
            }
        };

        /**
         * Get CSRF token for API requests.
         * Delegates to GTS.csrf.getToken() (shared/csrf.js).
         * @returns {string} CSRF token
         */
        proto.getCSRFToken = function() {
            return window.GTS && window.GTS.csrf
                ? GTS.csrf.getToken()
                : (window.getCookie ? window.getCookie('csrftoken') : '');
        };

        /**
         * Debounce function for search input
         */
        proto.debounce = function(func, wait) {
            var timeout;
            return function executedFunction() {
                var args = arguments;
                var context = this;
                var later = function() {
                    clearTimeout(timeout);
                    func.apply(context, args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        };

        /**
         * Show error message
         * @param {string} message - Error message to display
         */
        proto.showError = function(message) {
            console.error('JobCalendar Error:', message);
            // Use the shared toast system
            if (window.GTS && window.GTS.toast) {
                GTS.toast.error(message);
            } else {
                this.showToast(message, 'error');
            }
        };

        /**
         * Show success message
         * @param {string} message - Success message
         */
        proto.showSuccess = function(message) {
            // Use the shared toast system
            if (window.GTS && window.GTS.toast) {
                GTS.toast.success(message);
            } else {
                this.showToast(message, 'success');
            }
        };
    });

})();
