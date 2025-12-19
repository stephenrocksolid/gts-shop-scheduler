/**
 * Calendar Module Registry
 * 
 * Provides a mixin registration system for decomposing JobCalendar into modules
 * without requiring a bundler.
 * 
 * Usage:
 *   // In a module file (e.g., calendar/utils.js):
 *   GTS.calendar.register('utils', function(proto) {
 *       proto.showToast = function(message, type, duration) { ... };
 *       proto.debounce = function(func, wait) { ... };
 *   });
 * 
 *   // In job_calendar.js (after all modules are loaded):
 *   GTS.calendar.applyMixins(JobCalendar);
 */
(function() {
    'use strict';

    // Ensure GTS namespace exists
    window.GTS = window.GTS || {};

    // Calendar module registry
    const registry = {
        _mixins: {},
        _appliedTo: null,

        /**
         * Register a mixin to be applied to JobCalendar.prototype
         * @param {string} name - Unique name for this mixin (for debugging)
         * @param {function} mixinFn - Function that receives prototype and adds methods
         */
        register: function(name, mixinFn) {
            if (typeof mixinFn !== 'function') {
                console.error(`[GTS.calendar.register] Mixin "${name}" must be a function`);
                return;
            }
            if (this._mixins[name]) {
                console.warn(`[GTS.calendar.register] Mixin "${name}" already registered, overwriting`);
            }
            this._mixins[name] = mixinFn;

            // If we've already applied mixins to a class, apply this one immediately
            // (supports dynamic loading during development)
            if (this._appliedTo) {
                try {
                    mixinFn(this._appliedTo.prototype);
                } catch (e) {
                    console.error(`[GTS.calendar.register] Error applying late mixin "${name}":`, e);
                }
            }
        },

        /**
         * Apply all registered mixins to a class's prototype
         * @param {Function} JobCalendarClass - The JobCalendar class constructor
         */
        applyMixins: function(JobCalendarClass) {
            if (typeof JobCalendarClass !== 'function') {
                console.error('[GTS.calendar.applyMixins] Expected a class/function');
                return;
            }

            this._appliedTo = JobCalendarClass;
            const proto = JobCalendarClass.prototype;
            const mixinNames = Object.keys(this._mixins);

            // Apply each mixin
            for (const name of mixinNames) {
                try {
                    this._mixins[name](proto);
                } catch (e) {
                    console.error(`[GTS.calendar.applyMixins] Error applying mixin "${name}":`, e);
                }
            }

            // Dev-mode assertion: check for expected critical methods
            if (typeof console !== 'undefined' && console.warn) {
                const criticalMethods = [
                    'initialize',
                    'setupCalendar',
                    'fetchEvents',
                    'showEventTooltip',
                    'hideEventTooltip',
                    'toggleSearchPanel',
                    'forceEqualWeekHeights',
                    'selectAllCalendars'
                ];
                const missing = criticalMethods.filter(m => typeof proto[m] !== 'function');
                if (missing.length > 0) {
                    console.warn(
                        '[GTS.calendar] Missing critical methods after mixin apply:',
                        missing.join(', '),
                        '\nEnsure all calendar/*.js modules are loaded before job_calendar.js'
                    );
                }
            }
        },

        /**
         * Get list of registered mixin names (for debugging)
         * @returns {string[]}
         */
        getRegisteredMixins: function() {
            return Object.keys(this._mixins);
        },

        /**
         * Check if a mixin is registered
         * @param {string} name
         * @returns {boolean}
         */
        hasMixin: function(name) {
            return !!this._mixins[name];
        }
    };

    // Expose the registry
    GTS.calendar = registry;

})();
