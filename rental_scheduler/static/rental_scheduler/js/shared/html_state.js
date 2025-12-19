/**
 * GTS Shared HTML State Module
 * 
 * Provides serialize/sanitize functions for draft HTML restoration.
 * Consolidates duplicate implementations from panel.js and workspace.js.
 * 
 * These functions are critical for the draft persistence feature:
 * - serializeDraftHtml: Captures form state (checkboxes, selects, textareas) into HTML attributes
 * - sanitizeDraftHtml: Cleans up HTML before insertion (trims whitespace in strict input values)
 * 
 * Usage:
 *   GTS.htmlState.sanitizeDraftHtml(html) -> string
 *   GTS.htmlState.serializeDraftHtml(rootEl) -> string|null
 */
(function() {
    'use strict';

    // Ensure GTS namespace exists
    window.GTS = window.GTS || {};

    /**
     * Input types that cannot have whitespace in their value attribute.
     * Browsers will reject values with leading/trailing whitespace for these types.
     */
    var STRICT_VALUE_TYPES = ['number', 'date', 'datetime-local', 'time', 'month', 'week'];

    /**
     * Sanitize cached HTML before inserting into the DOM.
     * Trims value attributes for input types that don't accept whitespace.
     * 
     * @param {string} html - Raw HTML string (e.g., from localStorage draft)
     * @returns {string} - Sanitized HTML string
     */
    function sanitizeDraftHtml(html) {
        if (!html || typeof html !== 'string') return html;

        try {
            var parser = new DOMParser();
            var doc = parser.parseFromString(html, 'text/html');

            // Build selector for strict input types
            var selector = STRICT_VALUE_TYPES.map(function(t) {
                return 'input[type="' + t + '"]';
            }).join(', ');

            var inputs = doc.querySelectorAll(selector);
            inputs.forEach(function(input) {
                if (input.hasAttribute('value')) {
                    var rawValue = input.getAttribute('value');
                    var trimmed = rawValue.trim();
                    input.setAttribute('value', trimmed);
                }
            });

            // Return the sanitized body innerHTML
            return doc.body.innerHTML;
        } catch (e) {
            console.warn('GTS.htmlState.sanitizeDraftHtml: Error parsing HTML, returning original', e);
            return html;
        }
    }

    /**
     * Serialize panel/form body HTML for draft storage, preserving form state.
     * 
     * Unlike innerHTML alone, this persists:
     * - Checkbox and radio checked state (as 'checked' attribute)
     * - Select element selected options (as 'selected' attribute)
     * - Textarea content (as textContent)
     * - Text/number/date input values (as 'value' attribute)
     * 
     * Uses parallel NodeList iteration (by index) to avoid invalid selectors
     * when elements have empty IDs or names.
     * 
     * @param {HTMLElement} rootEl - The root element to serialize (e.g., panel body)
     * @returns {string|null} - HTML string with form state preserved, or null if rootEl is falsy
     */
    function serializeDraftHtml(rootEl) {
        if (!rootEl) return null;

        try {
            // Clone the root element so we don't modify the live DOM
            var clone = rootEl.cloneNode(true);

            // Persist checkbox and radio checked state using parallel iteration
            var origCheckboxes = rootEl.querySelectorAll('input[type="checkbox"], input[type="radio"]');
            var cloneCheckboxes = clone.querySelectorAll('input[type="checkbox"], input[type="radio"]');
            for (var i = 0; i < origCheckboxes.length && i < cloneCheckboxes.length; i++) {
                if (origCheckboxes[i].checked) {
                    cloneCheckboxes[i].setAttribute('checked', 'checked');
                } else {
                    cloneCheckboxes[i].removeAttribute('checked');
                }
            }

            // Persist select element selected state using parallel iteration
            var origSelects = rootEl.querySelectorAll('select');
            var cloneSelects = clone.querySelectorAll('select');
            for (var j = 0; j < origSelects.length && j < cloneSelects.length; j++) {
                var origSelect = origSelects[j];
                var cloneSelect = cloneSelects[j];

                // Clear all selected attributes first
                var cloneOptions = cloneSelect.querySelectorAll('option');
                cloneOptions.forEach(function(opt) {
                    opt.removeAttribute('selected');
                });

                // Set selected on the currently selected option(s) by matching value
                Array.from(origSelect.selectedOptions).forEach(function(origOpt) {
                    for (var k = 0; k < cloneOptions.length; k++) {
                        if (cloneOptions[k].value === origOpt.value) {
                            cloneOptions[k].setAttribute('selected', 'selected');
                            break;
                        }
                    }
                });
            }

            // Persist textarea values using parallel iteration
            // (innerHTML doesn't capture typed content)
            var origTextareas = rootEl.querySelectorAll('textarea');
            var cloneTextareas = clone.querySelectorAll('textarea');
            for (var m = 0; m < origTextareas.length && m < cloneTextareas.length; m++) {
                cloneTextareas[m].textContent = origTextareas[m].value;
            }

            // Persist text/number/date input values using parallel iteration
            var inputSelector = 'input[type="text"], input[type="number"], input[type="date"], ' +
                'input[type="datetime-local"], input[type="email"], input[type="tel"], input[type="hidden"]';
            var origInputs = rootEl.querySelectorAll(inputSelector);
            var cloneInputs = clone.querySelectorAll(inputSelector);
            for (var n = 0; n < origInputs.length && n < cloneInputs.length; n++) {
                cloneInputs[n].setAttribute('value', origInputs[n].value);
            }

            return clone.innerHTML;
        } catch (e) {
            console.warn('GTS.htmlState.serializeDraftHtml: Error serializing, falling back to innerHTML', e);
            return rootEl.innerHTML;
        }
    }

    // Expose the HTML state module
    GTS.htmlState = {
        sanitizeDraftHtml: sanitizeDraftHtml,
        serializeDraftHtml: serializeDraftHtml
    };

})();
