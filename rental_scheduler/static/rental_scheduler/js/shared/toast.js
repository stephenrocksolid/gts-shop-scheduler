/**
 * GTS Shared Toast Module
 * 
 * Provides a thin wrapper over window.showToast (defined in base.html).
 * Consolidates duplicate implementations from gts_init.js and job_calendar.js.
 * 
 * Usage:
 *   GTS.toast.show(message, type, duration)
 *   GTS.toast.success(message, duration?)
 *   GTS.toast.error(message, duration?)
 *   GTS.toast.warning(message, duration?)
 *   GTS.toast.info(message, duration?)
 *   GTS.showToast(message, type, duration) // back-compat alias
 */
(function() {
    'use strict';

    // Ensure GTS namespace exists
    window.GTS = window.GTS || {};

    /**
     * Default toast duration in milliseconds.
     */
    var DEFAULT_DURATION = 5000;

    /**
     * Show a toast notification.
     * Delegates to window.showToast when available, otherwise logs to console.
     * 
     * @param {string} message - Message to display
     * @param {string} [type='info'] - Toast type: 'success', 'error', 'warning', 'info'
     * @param {number} [duration=5000] - Duration in milliseconds
     */
    function show(message, type, duration) {
        type = type || 'info';
        duration = duration !== undefined ? duration : DEFAULT_DURATION;

        if (typeof window.showToast === 'function') {
            window.showToast(message, type, duration);
        } else {
            // Fallback: log to console
            var prefix = '[Toast ' + type + ']:';
            if (type === 'error') {
                console.error(prefix, message);
            } else if (type === 'warning') {
                console.warn(prefix, message);
            } else {
                console.log(prefix, message);
            }
        }
    }

    /**
     * Show a success toast.
     * @param {string} message
     * @param {number} [duration]
     */
    function success(message, duration) {
        show(message, 'success', duration);
    }

    /**
     * Show an error toast.
     * @param {string} message
     * @param {number} [duration]
     */
    function error(message, duration) {
        show(message, 'error', duration);
    }

    /**
     * Show a warning toast.
     * @param {string} message
     * @param {number} [duration]
     */
    function warning(message, duration) {
        show(message, 'warning', duration);
    }

    /**
     * Show an info toast.
     * @param {string} message
     * @param {number} [duration]
     */
    function info(message, duration) {
        show(message, 'info', duration);
    }

    // Expose the toast module
    GTS.toast = {
        show: show,
        success: success,
        error: error,
        warning: warning,
        info: info
    };

    // Back-compat alias: GTS.showToast (replaces gts_init.js version)
    GTS.showToast = show;

})();
