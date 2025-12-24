/**
 * GTS Init Helpers - Idempotent initialization utilities for HTMX-driven pages
 * 
 * This module provides utilities to prevent duplicate event bindings when:
 * - Page loads initially
 * - HTMX swaps content
 * - Partials are loaded multiple times
 * 
 * Usage:
 *   - GTS.initOnce('my_feature', () => { ... }) - Run once globally
 *   - GTS.markElInitialized(el, 'my_feature') - Mark an element as initialized
 *   - GTS.isElInitialized(el, 'my_feature') - Check if element was initialized
 *   - GTS.onDomReady(fn) - Run when DOM is ready (or immediately if already ready)
 *   - GTS.onHtmxLoad(fn) - Run on htmx:load events
 *   - GTS.onHtmxAfterSwap(fn) - Run on htmx:afterSwap events
 */
(function() {
    'use strict';

    // Global namespace
    window.GTS = window.GTS || {};

    // Track which global initializers have run
    const initOnceFlags = {};

    /**
     * Run an initializer function only once globally.
     * Subsequent calls with the same key are no-ops.
     * 
     * @param {string} key - Unique identifier for this initializer
     * @param {Function} fn - Function to run (only on first call)
     * @returns {boolean} - true if fn was executed, false if already initialized
     */
    GTS.initOnce = function(key, fn) {
        if (initOnceFlags[key]) {
            return false;
        }
        initOnceFlags[key] = true;
        fn();
        return true;
    };

    /**
     * Check if a global initializer has already run.
     * 
     * @param {string} key - Unique identifier to check
     * @returns {boolean}
     */
    GTS.hasInitialized = function(key) {
        return !!initOnceFlags[key];
    };

    /**
     * Reset an initializer flag (useful for testing).
     * 
     * @param {string} key - Unique identifier to reset
     */
    GTS.resetInit = function(key) {
        delete initOnceFlags[key];
    };

    /**
     * Mark an element as initialized for a specific feature.
     * Uses a data attribute to track initialization state.
     * 
     * @param {HTMLElement} el - Element to mark
     * @param {string} key - Feature identifier
     * @returns {boolean} - true if newly marked, false if already marked
     */
    GTS.markElInitialized = function(el, key) {
        if (!el || !el.setAttribute) return false;
        
        const attrName = 'data-gts-init-' + key;
        if (el.getAttribute(attrName) === '1') {
            return false;
        }
        el.setAttribute(attrName, '1');
        return true;
    };

    /**
     * Check if an element has been initialized for a specific feature.
     * 
     * @param {HTMLElement} el - Element to check
     * @param {string} key - Feature identifier
     * @returns {boolean}
     */
    GTS.isElInitialized = function(el, key) {
        if (!el || !el.getAttribute) return false;
        return el.getAttribute('data-gts-init-' + key) === '1';
    };

    /**
     * Clear initialization mark from an element.
     * 
     * @param {HTMLElement} el - Element to clear
     * @param {string} key - Feature identifier
     */
    GTS.clearElInitialized = function(el, key) {
        if (!el || !el.removeAttribute) return;
        el.removeAttribute('data-gts-init-' + key);
    };

    /**
     * Run a function when the DOM is ready.
     * If DOM is already ready, runs immediately.
     * 
     * @param {Function} fn - Function to run
     */
    GTS.onDomReady = function(fn) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fn);
        } else {
            fn();
        }
    };

    /**
     * Register a handler for htmx:load events.
     * The handler receives the event and the loaded element.
     * 
     * @param {Function} fn - Handler function(event)
     * @param {Object} options - Optional: { once: true } to only run once
     */
    GTS.onHtmxLoad = function(fn, options) {
        options = options || {};
        const handler = function(evt) {
            fn(evt);
            if (options.once) {
                document.body.removeEventListener('htmx:load', handler);
            }
        };
        document.body.addEventListener('htmx:load', handler);
    };

    /**
     * Register a handler for htmx:afterSwap events.
     * 
     * @param {Function} fn - Handler function(event)
     * @param {Object} options - Optional: { once: true } to only run once
     */
    GTS.onHtmxAfterSwap = function(fn, options) {
        options = options || {};
        const handler = function(evt) {
            fn(evt);
            if (options.once) {
                document.body.removeEventListener('htmx:afterSwap', handler);
            }
        };
        document.body.addEventListener('htmx:afterSwap', handler);
    };

    /**
     * Register a handler for htmx:afterRequest events (successful or not).
     * 
     * @param {Function} fn - Handler function(event)
     * @param {Object} options - Optional: { once: true } to only run once
     */
    GTS.onHtmxAfterRequest = function(fn, options) {
        options = options || {};
        const handler = function(evt) {
            fn(evt);
            if (options.once) {
                document.body.removeEventListener('htmx:afterRequest', handler);
            }
        };
        document.body.addEventListener('htmx:afterRequest', handler);
    };

    // =========================================================================
    // CSRF and Toast helpers are now provided by shared/csrf.js and shared/toast.js
    // They define GTS.getCookie, GTS.csrf.*, GTS.showToast, and GTS.toast.*
    // =========================================================================

})();
