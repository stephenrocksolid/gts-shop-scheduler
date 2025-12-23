/**
 * HTMX Configuration Shim
 * 
 * Disables HTMX's localStorage history caching and clears any existing cache.
 * This prevents sensitive HTML content from persisting in browser storage.
 * 
 * Must be loaded immediately after htmx.min.js in base.html.
 */
(function() {
    'use strict';

    // Disable HTMX history cache to prevent sensitive data persistence
    // Setting to 0 stops htmx-history-cache from being written
    if (typeof htmx !== 'undefined' && htmx.config) {
        htmx.config.historyCacheSize = 0;
    }

    // Clear any existing htmx-history-cache from localStorage (best-effort)
    try {
        localStorage.removeItem('htmx-history-cache');
    } catch (e) {
        // Ignore storage errors (private browsing, quota, etc.)
    }
})();

