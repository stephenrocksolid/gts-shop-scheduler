// rental_scheduler/static/rental_scheduler/js/schedule_picker.js
// Per-input flatpickr date/time pickers for job scheduling (Start & End)
(function () {
    'use strict';

    /**
     * Clean up stale flatpickr artifacts from restored draft HTML.
     * 
     * When a panel is restored from cached draft HTML (via innerHTML), the DOM may contain:
     * - flatpickr-generated "alt input" elements (with gts-flatpickr-alt class or no name)
     * - Stale init markers (data-schedule-picker-init="true")
     * - Classes that prevent re-initialization
     * 
     * This function cleans up these artifacts so initSchedulePicker() can run correctly.
     * Uses the shared GtsDateInputs helper when available.
     * 
     * @param {HTMLElement} container - The schedule-picker-container element
     */
    function cleanupRestoredFlatpickrArtifacts(container) {
        if (!container) return;

        // Use the shared helper from GtsDateInputs if available
        if (window.GtsDateInputs && window.GtsDateInputs.stripFlatpickrArtifacts) {
            window.GtsDateInputs.stripFlatpickrArtifacts(container, { destroyLiveInstances: true });
            return;
        }

        // Fallback: inline cleanup (before GtsDateInputs is loaded)

        // Remove stale init marker
        delete container.dataset.schedulePickerInit;

        // Find and process the original Start/End inputs
        const startInput = container.querySelector('input[name="start_dt"]');
        const endInput = container.querySelector('input[name="end_dt"]');

        [startInput, endInput].forEach(input => {
            if (!input) return;

            // Destroy any live flatpickr instance (shouldn't exist after innerHTML restore, but just in case)
            if (input._flatpickr) {
                input._flatpickr.destroy();
            }

            // Remove flatpickr-added class that prevents re-init detection
            input.classList.remove('flatpickr-input');
            input.removeAttribute('data-fp-original');

            // Restore input type to text (flatpickr requires text type)
            if (input.type === 'hidden') {
                input.type = 'text';
            }
        });

        // Remove alt inputs by marker class (our stable marker)
        container.querySelectorAll('.gts-flatpickr-alt').forEach(altInput => {
            altInput.remove();
        });

        // Remove alt inputs by structural detection (fallback for old drafts)
        container.querySelectorAll('input[data-fp-original="true"]').forEach(originalInput => {
            let sibling = originalInput.nextElementSibling;
            while (sibling && sibling.tagName === 'INPUT' && !sibling.name) {
                const toRemove = sibling;
                sibling = sibling.nextElementSibling;
                toRemove.remove();
            }
        });

        // Remove flatpickr-generated alt inputs (they have class flatpickr-input but no name attribute)
        // These are visible display inputs that flatpickr creates alongside the original input
        container.querySelectorAll('input.flatpickr-input:not([name])').forEach(altInput => {
            altInput.remove();
        });

        // Also remove any stray flatpickr calendar dropdowns that might have been cached
        // (unlikely, but defensive)
        container.querySelectorAll('.flatpickr-calendar').forEach(cal => {
            cal.remove();
        });
    }

    /**
     * Check if the schedule picker has live JS bindings (not just a stale DOM marker).
     * Returns true if flatpickr is actually initialized and functional.
     * 
     * @param {HTMLElement} container - The schedule-picker-container element
     * @returns {boolean} - True if live flatpickr instances exist
     */
    function hasLiveFlatpickrInstances(container) {
        if (!container) return false;

        const startInput = container.querySelector('input[name="start_dt"]');
        const endInput = container.querySelector('input[name="end_dt"]');

        // Check if either input has a live flatpickr instance
        const startHasLive = startInput && startInput._flatpickr && typeof startInput._flatpickr.open === 'function';
        const endHasLive = endInput && endInput._flatpickr && typeof endInput._flatpickr.open === 'function';

        return startHasLive && endHasLive;
    }

    /**
     * Initialize the schedule picker for the job form.
     * Guards against duplicate initialization by checking for LIVE flatpickr instances.
     * 
     * The previous approach used a data attribute (data-schedule-picker-init) which
     * persisted in cached draft HTML, preventing re-initialization after restore.
     * Now we check for actual JS bindings instead of just DOM markers.
     */
    function initSchedulePicker() {
        const container = document.getElementById('schedule-picker-container');
        if (!container) {
            return; // Container not found
        }

        // Check for live flatpickr instances (JS-based idempotency)
        // This correctly handles the case where:
        // - DOM has stale init markers from cached draft HTML, but no live JS bindings
        // - DOM has both markers AND live bindings (truly initialized)
        if (hasLiveFlatpickrInstances(container)) {
            return; // Already initialized with live instances
        }

        // If we get here, we need to (re)initialize.
        // First, clean up any stale artifacts from restored draft HTML.
        cleanupRestoredFlatpickrArtifacts(container);

        // Mark as initialized (still useful for debugging, but not the sole idempotency check)
        container.dataset.schedulePickerInit = 'true';

        // DOM elements
        const startInput = document.querySelector('input[name="start_dt"]');
        const endInput = document.querySelector('input[name="end_dt"]');
        const allDayCheckbox = document.querySelector('input[name="all_day"]');

        if (!startInput || !endInput) {
            console.warn('Schedule picker: Start/End inputs not found');
            return;
        }

        // flatpickr instances
        let startPicker = null;
        let endPicker = null;

        /**
         * Determine if All Day mode is currently on.
         */
        function isAllDay() {
            return allDayCheckbox && allDayCheckbox.checked;
        }

        /**
         * Format a Date object to YYYY-MM-DD.
         */
        function formatDate(date) {
            if (!date) return '';
            const y = date.getFullYear();
            const m = String(date.getMonth() + 1).padStart(2, '0');
            const d = String(date.getDate()).padStart(2, '0');
            return `${y}-${m}-${d}`;
        }

        /**
         * Format a Date object to YYYY-MM-DDTHH:MM.
         */
        function formatDateTime(date) {
            if (!date) return '';
            const y = date.getFullYear();
            const mo = String(date.getMonth() + 1).padStart(2, '0');
            const d = String(date.getDate()).padStart(2, '0');
            const h = String(date.getHours()).padStart(2, '0');
            const mi = String(date.getMinutes()).padStart(2, '0');
            return `${y}-${mo}-${d}T${h}:${mi}`;
        }

        /**
         * Parse an input value to a Date object.
         * Handles YYYY-MM-DD and YYYY-MM-DDTHH:MM formats.
         */
        function parseInputValue(val) {
            if (!val) return null;
            // Remove any extra whitespace
            val = val.trim();
            if (val.includes('T')) {
                // datetime-local format
                const parts = val.split('T');
                const dateParts = parts[0].split('-');
                const timeParts = parts[1].split(':');
                if (dateParts.length === 3 && timeParts.length >= 2) {
                    return new Date(
                        parseInt(dateParts[0]),
                        parseInt(dateParts[1]) - 1,
                        parseInt(dateParts[2]),
                        parseInt(timeParts[0]),
                        parseInt(timeParts[1])
                    );
                }
            } else {
                // date-only format
                const parts = val.split('-');
                if (parts.length === 3) {
                    return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
                }
            }
            return null;
        }

        /**
         * Get flatpickr config based on current All Day mode.
         */
        function getPickerConfig(isStart) {
            const allDay = isAllDay();
            const config = {
                allowInput: true,
                disableMobile: true, // Use flatpickr on mobile too for consistency
                dateFormat: allDay ? 'Y-m-d' : 'Y-m-d\\TH:i',
                enableTime: !allDay,
                time_24hr: false,
                minuteIncrement: 15,
                onClose: function (selectedDates, dateStr, instance) {
                    // Trigger change event for validation/listeners
                    instance.input.dispatchEvent(new Event('change', { bubbles: true }));
                }
            };

            if (!isStart) {
                // End picker: onChange enforces that end >= start
                config.onChange = function (selectedDates) {
                    if (selectedDates.length > 0) {
                        enforceEndAfterStart();
                    }
                };
                // End picker: onOpen jumps to minDate if no date selected yet
                // This prevents the calendar opening on an invalid month when Start is far in the future
                config.onOpen = function (selectedDates, dateStr, instance) {
                    if (selectedDates.length === 0 && instance.config.minDate) {
                        instance.jumpToDate(instance.config.minDate);
                    }
                };
            } else {
                // Start picker: onChange updates end's minDate and enforces constraint
                config.onChange = function (selectedDates) {
                    if (selectedDates.length > 0 && endPicker) {
                        const startDate = selectedDates[0];
                        // Update minDate on end picker
                        endPicker.set('minDate', startDate);
                        // Enforce end >= start
                        enforceEndAfterStart();
                    }
                };
            }

            return config;
        }

        /**
         * Enforce that end date/time is not before start date/time.
         * If invalid, auto-correct end to a valid value.
         */
        function enforceEndAfterStart() {
            const startDate = startPicker ? startPicker.selectedDates[0] : null;
            const endDate = endPicker ? endPicker.selectedDates[0] : null;

            if (!startDate || !endDate) return;

            const allDay = isAllDay();

            if (allDay) {
                // For all-day: end must be >= start (same day is OK)
                if (endDate < startDate) {
                    endPicker.setDate(startDate, true);
                }
            } else {
                // For timed: end must be > start
                if (endDate <= startDate) {
                    // Set end to start + 60 minutes
                    const newEnd = new Date(startDate.getTime() + 60 * 60 * 1000);
                    endPicker.setDate(newEnd, true);
                }
            }
        }

        /**
         * Initialize or reinitialize both flatpickr instances.
         */
        function initPickers() {
            // Destroy existing pickers if any
            if (startPicker) {
                startPicker.destroy();
                startPicker = null;
            }
            if (endPicker) {
                endPicker.destroy();
                endPicker = null;
            }

            // Parse current values
            const startVal = parseInputValue(startInput.value);
            const endVal = parseInputValue(endInput.value);

            // Initialize start picker
            const startConfig = getPickerConfig(true);
            if (startVal) {
                startConfig.defaultDate = startVal;
            }
            startPicker = flatpickr(startInput, startConfig);

            // Initialize end picker
            const endConfig = getPickerConfig(false);
            if (endVal) {
                endConfig.defaultDate = endVal;
            }
            // Set minDate to start value if available
            if (startVal) {
                endConfig.minDate = startVal;
            }
            endPicker = flatpickr(endInput, endConfig);
        }

        /**
         * Handle All Day checkbox toggle.
         * Converts values between date-only and datetime formats and reinitializes pickers.
         */
        function handleAllDayToggle() {
            const allDay = isAllDay();
            const startDate = startPicker ? startPicker.selectedDates[0] : parseInputValue(startInput.value);
            const endDate = endPicker ? endPicker.selectedDates[0] : parseInputValue(endInput.value);

            if (allDay) {
                // Convert to date-only format
                if (startDate) {
                    startInput.value = formatDate(startDate);
                }
                if (endDate) {
                    endInput.value = formatDate(endDate);
                }
            } else {
                // Convert to datetime format with default times
                if (startDate) {
                    // Set to 09:00 if no time was set
                    const newStart = new Date(startDate);
                    if (newStart.getHours() === 0 && newStart.getMinutes() === 0) {
                        newStart.setHours(9, 0, 0, 0);
                    }
                    startInput.value = formatDateTime(newStart);
                }
                if (endDate) {
                    // Set to 17:00 if no time was set
                    const newEnd = new Date(endDate);
                    if (newEnd.getHours() === 0 && newEnd.getMinutes() === 0) {
                        newEnd.setHours(17, 0, 0, 0);
                    }
                    endInput.value = formatDateTime(newEnd);
                }
            }

            // Reinitialize pickers with new config
            initPickers();

            // Trigger change events
            startInput.dispatchEvent(new Event('change', { bubbles: true }));
            endInput.dispatchEvent(new Event('change', { bubbles: true }));
        }

        // Listen for all-day checkbox changes
        if (allDayCheckbox) {
            allDayCheckbox.addEventListener('change', handleAllDayToggle);
        }

        // Initialize pickers on load
        initPickers();
    }

    /**
     * Initialize schedule picker on DOM ready.
     */
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initSchedulePicker);
        } else {
            initSchedulePicker();
        }
    }

    // Run initialization
    init();

    // Re-initialize after HTMX swaps
    document.body.addEventListener('htmx:afterSwap', function () {
        setTimeout(initSchedulePicker, 100);
    });

    document.body.addEventListener('htmx:load', function () {
        setTimeout(initSchedulePicker, 100);
    });

    // Expose for manual use if needed
    window.SchedulePicker = {
        init: initSchedulePicker,
        cleanup: cleanupRestoredFlatpickrArtifacts,
        hasLiveInstances: hasLiveFlatpickrInstances
    };
})();
