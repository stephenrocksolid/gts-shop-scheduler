/**
 * GTS Shared CSRF Module
 * 
 * Provides a single, consistent CSRF token getter and header helper.
 * Consolidates duplicate implementations from base.html, gts_init.js, config.js,
 * panel.js, and job_calendar.js.
 * 
 * Precedence for getToken():
 *   1) meta[name="csrf-token"] (set by Django template)
 *   2) options.root?.querySelector('input[name="csrfmiddlewaretoken"]') (form-scoped)
 *   3) cookie 'csrftoken' (fallback)
 * 
 * Usage:
 *   GTS.csrf.getToken() -> string
 *   GTS.csrf.getToken({ root: formElement }) -> string (checks form hidden input)
 *   GTS.csrf.headers() -> { 'X-CSRFToken': token }
 *   GTS.csrf.headers({ 'Content-Type': 'application/json' }) -> merged headers
 *   GTS.getCookie('csrftoken') -> string (back-compat alias)
 */
(function() {
    'use strict';

    // Ensure GTS namespace exists
    window.GTS = window.GTS || {};

    /**
     * Get a cookie value by name.
     * @param {string} name - Cookie name
     * @returns {string|undefined}
     */
    function getCookie(name) {
        if (!name) return undefined;
        const value = '; ' + document.cookie;
        const parts = value.split('; ' + name + '=');
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return undefined;
    }

    /**
     * Get the CSRF token using a consistent precedence chain.
     * @param {Object} [options]
     * @param {HTMLElement} [options.root] - Root element to search for hidden input
     * @returns {string} - CSRF token or empty string
     */
    function getToken(options) {
        options = options || {};

        // 1) Try meta tag first (most reliable, set by Django in base.html)
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag && metaTag.content) {
            return metaTag.content;
        }

        // 2) Try form hidden input if root is provided
        if (options.root) {
            const hiddenInput = options.root.querySelector('input[name="csrfmiddlewaretoken"]');
            if (hiddenInput && hiddenInput.value) {
                return hiddenInput.value;
            }
        }

        // 3) Fallback to cookie
        const cookieToken = getCookie('csrftoken');
        if (cookieToken) {
            return cookieToken;
        }

        // 4) Last resort: check for any hidden input in the document
        const anyHiddenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (anyHiddenInput && anyHiddenInput.value) {
            return anyHiddenInput.value;
        }

        return '';
    }

    /**
     * Build request headers including the CSRF token.
     * @param {Object} [extraHeaders] - Additional headers to merge
     * @param {Object} [options] - Options passed to getToken()
     * @returns {Object} - Headers object with X-CSRFToken
     */
    function headers(extraHeaders, options) {
        const token = getToken(options);
        const result = {};

        // Add CSRF token if we have one
        if (token) {
            result['X-CSRFToken'] = token;
        }

        // Merge extra headers
        if (extraHeaders && typeof extraHeaders === 'object') {
            Object.assign(result, extraHeaders);
        }

        return result;
    }

    // Expose the CSRF module
    GTS.csrf = {
        getToken: getToken,
        headers: headers
    };

    // Back-compat alias: GTS.getCookie (replaces gts_init.js version)
    GTS.getCookie = getCookie;

})();
