/**
 * GTS Series Occurrences UI Module
 * 
 * Shared logic for expanding/collapsing grouped-search series occurrence rows.
 * Used by both calendar_page.js and jobs_list_page.js.
 * 
 * This module exposes functions that do NOT auto-bind event handlers.
 * The calling entrypoint is responsible for event delegation and idempotency.
 * 
 * Requires: GTS.urls.seriesOccurrences
 */
(function() {
    'use strict';

    // Ensure GTS namespace exists
    window.GTS = window.GTS || {};

    /**
     * Default count of occurrence rows to fetch on initial expand.
     */
    var DEFAULT_COUNT = 5;

    /**
     * Expand a series header row to show its occurrence rows.
     * 
     * @param {HTMLElement} headerRow - The .series-header-row element
     * @param {Object} options
     * @param {number} [options.count=5] - Number of rows to fetch
     * @param {Function} [options.getSearchQuery] - Function returning current search query string
     * @param {HTMLElement} [options.rootEl=document] - Root element for DOM queries
     * @returns {Promise<void>}
     */
    function expand(headerRow, options) {
        options = options || {};
        var count = options.count || DEFAULT_COUNT;
        var getSearchQuery = options.getSearchQuery || function() { return ''; };
        var rootEl = options.rootEl || document;

        var seriesId = headerRow.getAttribute('data-series-id');
        var scope = headerRow.getAttribute('data-scope');

        var icon = headerRow.querySelector('.expand-icon');
        var spinner = headerRow.querySelector('.loading-spinner');
        var label = headerRow.querySelector('.expand-label');

        // Show loading state
        headerRow.style.opacity = '0.7';
        if (icon) icon.classList.add('hidden');
        if (spinner) spinner.classList.remove('hidden');
        if (label) label.textContent = 'Loading...';

        var searchQuery = getSearchQuery();
        var url = GTS.urls.seriesOccurrences +
            '?parent_id=' + encodeURIComponent(seriesId || '') +
            '&scope=' + encodeURIComponent(scope || '') +
            '&search=' + encodeURIComponent(searchQuery) +
            '&count=' + encodeURIComponent(String(count)) +
            '&offset=0';

        return fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(function(response) {
                if (!response.ok) {
                    return response.text().then(function(text) {
                        throw new Error('Failed to fetch occurrences: ' + text);
                    });
                }
                return response.text();
            })
            .then(function(html) {
                // Remove any existing occurrence rows for this series/scope
                removeOccurrenceRows(seriesId, scope, rootEl);

                // Insert new rows after header
                headerRow.insertAdjacentHTML('afterend', html);

                // Update header state
                headerRow.setAttribute('data-expanded', 'true');
                headerRow.setAttribute('aria-expanded', 'true');
                if (icon) icon.style.transform = 'rotate(90deg)';
                if (label) label.textContent = 'Click to collapse';
            })
            .catch(function(error) {
                console.error('Error fetching series occurrences:', error);
                if (window.showToast) {
                    window.showToast('Failed to load occurrences: ' + error.message, 'error');
                }
                if (label) label.textContent = 'Click to expand';
            })
            .finally(function() {
                headerRow.style.opacity = '1';
                if (icon) icon.classList.remove('hidden');
                if (spinner) spinner.classList.add('hidden');
            });
    }

    /**
     * Collapse a series header row (remove its occurrence rows).
     * 
     * @param {HTMLElement} headerRow - The .series-header-row element
     * @param {Object} options
     * @param {HTMLElement} [options.rootEl=document] - Root element for DOM queries
     */
    function collapse(headerRow, options) {
        options = options || {};
        var rootEl = options.rootEl || document;

        var seriesId = headerRow.getAttribute('data-series-id');
        var scope = headerRow.getAttribute('data-scope');

        removeOccurrenceRows(seriesId, scope, rootEl);

        var icon = headerRow.querySelector('.expand-icon');
        var label = headerRow.querySelector('.expand-label');

        headerRow.setAttribute('data-expanded', 'false');
        headerRow.setAttribute('aria-expanded', 'false');
        if (icon) icon.style.transform = 'rotate(0deg)';
        if (label) label.textContent = 'Click to expand';
    }

    /**
     * Toggle expansion state of a series header row.
     * 
     * @param {HTMLElement} headerRow - The .series-header-row element
     * @param {Object} options - Same as expand() options
     * @returns {Promise<void>|undefined}
     */
    function toggle(headerRow, options) {
        var isExpanded = headerRow.getAttribute('data-expanded') === 'true';
        if (isExpanded) {
            collapse(headerRow, options);
        } else {
            return expand(headerRow, options);
        }
    }

    /**
     * Handle "Show more occurrences" button click.
     * Fetches the next page of occurrences and appends them.
     * 
     * @param {HTMLElement} btn - The .show-more-series-btn element
     * @param {Object} options
     * @param {number} [options.count=5] - Number of additional rows to fetch
     * @param {HTMLElement} [options.rootEl=document] - Root element for DOM queries
     * @returns {Promise<void>}
     */
    function showMore(btn, options) {
        options = options || {};
        var count = options.count || DEFAULT_COUNT;
        var rootEl = options.rootEl || document;

        var parentId = btn.getAttribute('data-parent-id');
        var scope = btn.getAttribute('data-scope');
        var currentOffset = parseInt(btn.getAttribute('data-current-offset'), 10) || 0;
        var searchQuery = decodeURIComponent(btn.getAttribute('data-search') || '');

        // Show loading state
        var originalText = btn.textContent;
        btn.textContent = 'Loading...';
        btn.disabled = true;

        var url = GTS.urls.seriesOccurrences +
            '?parent_id=' + encodeURIComponent(parentId || '') +
            '&scope=' + encodeURIComponent(scope || '') +
            '&search=' + encodeURIComponent(searchQuery) +
            '&count=' + encodeURIComponent(String(count)) +
            '&offset=' + encodeURIComponent(String(currentOffset));

        return fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('Failed to fetch more occurrences');
                }
                return response.text();
            })
            .then(function(html) {
                // The "show more" row should be replaced by the new rows + potentially a new show-more row
                var showMoreRow = btn.closest('tr');
                if (showMoreRow) {
                    showMoreRow.insertAdjacentHTML('beforebegin', html);
                    showMoreRow.remove();
                }
            })
            .catch(function(error) {
                console.error('Error fetching more occurrences:', error);
                if (window.showToast) {
                    window.showToast('Failed to load more occurrences', 'error');
                }
                btn.textContent = originalText;
                btn.disabled = false;
            });
    }

    /**
     * Remove all occurrence rows for a given series/scope combination.
     * 
     * @param {string} seriesId
     * @param {string} scope
     * @param {HTMLElement|Document} rootEl
     */
    function removeOccurrenceRows(seriesId, scope, rootEl) {
        var selector = '.series-occurrence-row[data-series-id="' + seriesId + '"][data-series-scope="' + scope + '"]';
        var rows = rootEl.querySelectorAll(selector);
        rows.forEach(function(row) {
            row.remove();
        });
    }

    // Expose public API
    GTS.seriesOccurrencesUI = {
        expand: expand,
        collapse: collapse,
        toggle: toggle,
        showMore: showMore,
        DEFAULT_COUNT: DEFAULT_COUNT
    };

})();

