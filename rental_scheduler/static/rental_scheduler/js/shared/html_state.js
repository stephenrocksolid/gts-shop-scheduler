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
     * 
     * This function:
     * - Trims value attributes for input types that don't accept whitespace
     * - Strips flatpickr artifacts from OLD drafts that were saved before the fix
     *   (so restoring old drafts won't create duplicate inputs)
     * 
     * @param {string} html - Raw HTML string (e.g., from localStorage draft)
     * @returns {string} - Sanitized HTML string
     */
    function sanitizeDraftHtml(html) {
        if (!html || typeof html !== 'string') return html;

        try {
            var parser = new DOMParser();
            var doc = parser.parseFromString(html, 'text/html');

            // ================================================================
            // STRIP FLATPICKR ARTIFACTS FROM OLD DRAFTS
            // This handles drafts saved before the fix was in place.
            // Uses the shared helper from GtsDateInputs when available.
            // ================================================================
            if (window.GtsDateInputs && window.GtsDateInputs.stripFlatpickrArtifacts) {
                window.GtsDateInputs.stripFlatpickrArtifacts(doc.body);
            } else {
                // Fallback: inline cleanup for old drafts (before GtsDateInputs is loaded)
                stripFlatpickrArtifactsInline(doc.body);
            }

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

            // Remove HTMX processed markers so restored drafts rebind correctly
            doc.querySelectorAll('[data-hx-processed]').forEach(function(el) {
                el.removeAttribute('data-hx-processed');
            });

            // Return the sanitized body innerHTML
            return doc.body.innerHTML;
        } catch (e) {
            console.warn('GTS.htmlState.sanitizeDraftHtml: Error parsing HTML, returning original', e);
            return html;
        }
    }

    /**
     * Inline fallback for stripping flatpickr artifacts.
     * Used when GtsDateInputs is not yet loaded.
     * @param {HTMLElement} rootEl - The root element to clean
     */
    function stripFlatpickrArtifactsInline(rootEl) {
        if (!rootEl) return;

        // Remove alt inputs by marker class
        rootEl.querySelectorAll('.gts-flatpickr-alt').forEach(function(el) {
            el.remove();
        });

        // Remove alt inputs by structural detection (fallback)
        rootEl.querySelectorAll('input[data-fp-original="true"], input.flatpickr-input[name]').forEach(function(originalInput) {
            var sibling = originalInput.nextElementSibling;
            while (sibling && sibling.tagName === 'INPUT' && !sibling.name) {
                var toRemove = sibling;
                sibling = sibling.nextElementSibling;
                toRemove.remove();
            }
        });

        // Remove nameless inputs with flatpickr-input class
        rootEl.querySelectorAll('input.flatpickr-input:not([name])').forEach(function(el) {
            el.remove();
        });

        // Remove schedule picker init marker
        var scheduleContainer = rootEl.querySelector('#schedule-picker-container');
        if (scheduleContainer) {
            delete scheduleContainer.dataset.schedulePickerInit;
            scheduleContainer.removeAttribute('data-schedule-picker-init');
        }

        // Clean up flatpickr classes from original inputs
        rootEl.querySelectorAll('input[data-fp-original="true"], input.flatpickr-input').forEach(function(input) {
            if (input.name) {
                input.classList.remove('flatpickr-input');
                input.removeAttribute('data-fp-original');
                input.removeAttribute('readonly');
                if (input.type === 'hidden') {
                    input.type = 'text';
                }
            }
        });

        // Remove any flatpickr calendar dropdowns
        rootEl.querySelectorAll('.flatpickr-calendar').forEach(function(cal) {
            cal.remove();
        });
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
     * Also STRIPS client-only artifacts that would prevent re-initialization on restore:
     * - Flatpickr-generated alt inputs (input.flatpickr-input:not([name]))
     * - Schedule picker init markers (data-schedule-picker-init)
     * - Panel date picker markers and flatpickr classes on original inputs
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

            // ================================================================
            // STRIP CLIENT-ONLY FLATPICKR ARTIFACTS (prevents re-init issues)
            // Uses the shared helper from GtsDateInputs when available.
            // ================================================================
            if (window.GtsDateInputs && window.GtsDateInputs.stripFlatpickrArtifacts) {
                window.GtsDateInputs.stripFlatpickrArtifacts(clone);
            } else {
                // Fallback: inline cleanup (before GtsDateInputs is loaded)
                stripFlatpickrArtifactsInline(clone);
            }

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

            // Persist text/number/date input values using NAME-BASED matching
            // We must use name matching (not index iteration) because stripping flatpickr artifacts
            // from the clone removes alt inputs, causing index misalignment between orig and clone.
            var inputSelector = 'input[type="text"], input[type="number"], input[type="date"], ' +
                'input[type="datetime-local"], input[type="email"], input[type="tel"], input[type="hidden"]';
            var origInputs = rootEl.querySelectorAll(inputSelector);
            origInputs.forEach(function(origInput) {
                // Only process named inputs (skip flatpickr alt inputs which have no name)
                var inputName = origInput.name;
                if (!inputName) return;

                // Find matching input in clone by name
                var cloneInput = clone.querySelector('input[name="' + inputName + '"]');
                if (cloneInput) {
                    // Get the value from the original - but prefer the _flatpickr instance's selectedDates
                    // if available (the input.value for hidden inputs may be the ISO string, which is correct)
                    var valueToSave = origInput.value;
                    
                    // If this is a flatpickr-managed input, get the proper value from the instance
                    // This ensures we save the ISO format, not the friendly display format
                    if (origInput._flatpickr && origInput._flatpickr.selectedDates && origInput._flatpickr.selectedDates.length > 0) {
                        // Use the formatDate method to get proper ISO string
                        var fp = origInput._flatpickr;
                        var dateFormat = fp.config.dateFormat || 'Y-m-d';
                        valueToSave = fp.formatDate(fp.selectedDates[0], dateFormat);
                    }
                    
                    cloneInput.setAttribute('value', valueToSave);
                }
            });

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
