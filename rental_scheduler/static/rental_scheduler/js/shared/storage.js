/**
 * GTS Shared Storage Module
 * 
 * Provides safe localStorage helpers with JSON parsing/stringify and boolean support.
 * Uses try/catch to handle quota exceeded errors and private browsing mode.
 * 
 * Note: Phase 2 keeps existing localStorage keys unchanged. Key consolidation
 * is deferred to Phase 4.
 * 
 * Usage:
 *   GTS.storage.getRaw(key) -> string|null
 *   GTS.storage.setRaw(key, value) -> void
 *   GTS.storage.remove(key) -> void
 *   GTS.storage.getJson(key, fallback?) -> parsed value or fallback
 *   GTS.storage.setJson(key, value) -> boolean (true if stored)
 *   GTS.storage.getBool(key, fallback?) -> boolean
 *   GTS.storage.setBool(key, value) -> void
 */
(function() {
    'use strict';

    // Ensure GTS namespace exists
    window.GTS = window.GTS || {};

    /**
     * Get a raw string value from localStorage.
     * @param {string} key
     * @returns {string|null}
     */
    function getRaw(key) {
        try {
            return localStorage.getItem(key);
        } catch (e) {
            console.warn('GTS.storage.getRaw: Error reading localStorage', e);
            return null;
        }
    }

    /**
     * Set a raw string value in localStorage.
     * @param {string} key
     * @param {string} value
     */
    function setRaw(key, value) {
        try {
            localStorage.setItem(key, value);
        } catch (e) {
            console.warn('GTS.storage.setRaw: Error writing localStorage', e);
        }
    }

    /**
     * Remove a key from localStorage.
     * @param {string} key
     */
    function remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('GTS.storage.remove: Error removing from localStorage', e);
        }
    }

    /**
     * Get a JSON-parsed value from localStorage.
     * Returns fallback if key doesn't exist or parsing fails.
     * @param {string} key
     * @param {*} [fallback=null]
     * @returns {*}
     */
    function getJson(key, fallback) {
        fallback = fallback !== undefined ? fallback : null;
        try {
            var raw = localStorage.getItem(key);
            if (raw === null) {
                return fallback;
            }
            return JSON.parse(raw);
        } catch (e) {
            console.warn('GTS.storage.getJson: Error parsing JSON for key "' + key + '"', e);
            return fallback;
        }
    }

    /**
     * Set a JSON-stringified value in localStorage.
     * @param {string} key
     * @param {*} value
     * @returns {boolean} - true if stored, false if storage failed
     */
    function setJson(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.warn('GTS.storage.setJson: Error writing JSON to localStorage', e);
            // If quota exceeded, log additional info
            if (e.name === 'QuotaExceededError' || e.code === 22) {
                console.error('GTS.storage.setJson: localStorage quota exceeded for key "' + key + '"');
            }
            return false;
        }
    }

    /**
     * Get a boolean value from localStorage.
     * Treats 'true', '1', and truthy JSON values as true.
     * @param {string} key
     * @param {boolean} [fallback=false]
     * @returns {boolean}
     */
    function getBool(key, fallback) {
        fallback = fallback !== undefined ? fallback : false;
        try {
            var raw = localStorage.getItem(key);
            if (raw === null) {
                return fallback;
            }
            // Handle common boolean string representations
            if (raw === 'true' || raw === '1') {
                return true;
            }
            if (raw === 'false' || raw === '0' || raw === '') {
                return false;
            }
            // Try JSON parse for other values
            return !!JSON.parse(raw);
        } catch (e) {
            return fallback;
        }
    }

    /**
     * Set a boolean value in localStorage.
     * Stores as 'true' or 'false' string.
     * @param {string} key
     * @param {boolean} value
     */
    function setBool(key, value) {
        try {
            localStorage.setItem(key, value ? 'true' : 'false');
        } catch (e) {
            console.warn('GTS.storage.setBool: Error writing to localStorage', e);
        }
    }

    // Expose the storage module
    GTS.storage = {
        getRaw: getRaw,
        setRaw: setRaw,
        remove: remove,
        getJson: getJson,
        setJson: setJson,
        getBool: getBool,
        setBool: setBool
    };

})();
