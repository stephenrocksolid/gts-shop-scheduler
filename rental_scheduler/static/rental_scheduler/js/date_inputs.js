// rental_scheduler/static/rental_scheduler/js/date_inputs.js
// ==========================================================================
// SHARED DATE INPUT UTILITIES
// Provides user-friendly date formatting (e.g., "Dec 22, 2026") while
// keeping ISO values (YYYY-MM-DD, YYYY-MM-DDTHH:MM) for form submission.
// Supports flexible typed input in various common formats.
// ==========================================================================

(function () {
  'use strict';

  // Month name map for parsing
  const MONTHS = {
    jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5,
    jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11
  };

  /**
   * Parse a user-entered date string into a Date object.
   * Supports many common formats:
   *   - MM/DD/YY, MM/DD/YYYY (also with - or . separators)
   *   - YYYY-MM-DD, YYYY/MM/DD
   *   - Mon D, YYYY or Mon D YYYY (e.g. Dec 22, 2026)
   *   - ISO datetime: YYYY-MM-DDTHH:MM
   * Returns null if parsing fails.
   */
  function parseFlexibleDate(str) {
    if (!str || typeof str !== 'string') return null;
    str = str.trim();
    if (!str) return null;

    let year, month, day, hours = 0, minutes = 0;

    // Try ISO datetime first: YYYY-MM-DDTHH:MM
    let m = str.match(/^(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})T(\d{1,2}):(\d{2})$/);
    if (m) {
      year = parseInt(m[1], 10);
      month = parseInt(m[2], 10) - 1;
      day = parseInt(m[3], 10);
      hours = parseInt(m[4], 10);
      minutes = parseInt(m[5], 10);
      return new Date(year, month, day, hours, minutes);
    }

    // Try ISO date: YYYY-MM-DD or YYYY/MM/DD
    m = str.match(/^(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})$/);
    if (m) {
      year = parseInt(m[1], 10);
      month = parseInt(m[2], 10) - 1;
      day = parseInt(m[3], 10);
      return new Date(year, month, day);
    }

    // Try MM/DD/YY or MM/DD/YYYY (also - or . separators)
    m = str.match(/^(\d{1,2})[-\/.]\s*(\d{1,2})[-\/.]\s*(\d{2,4})$/);
    if (m) {
      month = parseInt(m[1], 10) - 1;
      day = parseInt(m[2], 10);
      year = parseInt(m[3], 10);
      // Handle 2-digit year
      if (year < 100) {
        year = 2000 + year;
      }
      return new Date(year, month, day);
    }

    // Try "Mon D, YYYY" or "Mon D YYYY" (e.g. Dec 22, 2026)
    m = str.match(/^([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})$/);
    if (m) {
      const monthKey = m[1].toLowerCase().slice(0, 3);
      if (MONTHS.hasOwnProperty(monthKey)) {
        month = MONTHS[monthKey];
        day = parseInt(m[2], 10);
        year = parseInt(m[3], 10);
        return new Date(year, month, day);
      }
    }

    // Try "Mon D, YYYY h:mm AM/PM" or similar with time
    m = str.match(/^([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})\s+(\d{1,2}):(\d{2})\s*(AM|PM)?$/i);
    if (m) {
      const monthKey = m[1].toLowerCase().slice(0, 3);
      if (MONTHS.hasOwnProperty(monthKey)) {
        month = MONTHS[monthKey];
        day = parseInt(m[2], 10);
        year = parseInt(m[3], 10);
        hours = parseInt(m[4], 10);
        minutes = parseInt(m[5], 10);
        const ampm = (m[6] || '').toUpperCase();
        if (ampm === 'PM' && hours < 12) hours += 12;
        if (ampm === 'AM' && hours === 12) hours = 0;
        return new Date(year, month, day, hours, minutes);
      }
    }

    return null;
  }

  /**
   * Parse an ISO date/datetime-local string to a Date object using local time.
   * Avoids timezone issues that occur with `new Date(isoString)`.
   */
  function parseISOLocal(str) {
    if (!str) return null;
    str = str.trim();

    // YYYY-MM-DDTHH:MM
    let m = str.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/);
    if (m) {
      return new Date(
        parseInt(m[1], 10),
        parseInt(m[2], 10) - 1,
        parseInt(m[3], 10),
        parseInt(m[4], 10),
        parseInt(m[5], 10)
      );
    }

    // YYYY-MM-DD
    m = str.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (m) {
      return new Date(
        parseInt(m[1], 10),
        parseInt(m[2], 10) - 1,
        parseInt(m[3], 10)
      );
    }

    return null;
  }

  /**
   * Format a Date object to YYYY-MM-DD (ISO date only).
   */
  function formatISODate(date) {
    if (!date || !(date instanceof Date) || isNaN(date.getTime())) return '';
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }

  /**
   * Format a Date object to YYYY-MM-DDTHH:MM (datetime-local).
   */
  function formatISODateTimeLocal(date) {
    if (!date || !(date instanceof Date) || isNaN(date.getTime())) return '';
    const y = date.getFullYear();
    const mo = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    const h = String(date.getHours()).padStart(2, '0');
    const mi = String(date.getMinutes()).padStart(2, '0');
    return `${y}-${mo}-${d}T${h}:${mi}`;
  }

  /**
   * Build flatpickr configuration with friendly display format.
   * 
   * @param {HTMLElement} inputEl - The input element being initialized
   * @param {Object} baseConfig - Original config to merge with (optional)
   * @param {Object} opts - Additional options
   * @param {boolean} opts.enableTime - Whether to enable time selection
   * @param {Function} opts.onChange - Custom onChange callback
   * @param {Function} opts.onReady - Custom onReady callback
   * @returns {Object} - Flatpickr configuration object
   */
  function buildFriendlyFlatpickrConfig(inputEl, baseConfig, opts) {
    baseConfig = baseConfig || {};
    opts = opts || {};

    const enableTime = opts.enableTime === true || baseConfig.enableTime === true;
    const inputName = inputEl.name || '';

    // Determine altFormat based on whether time is enabled
    const altFormat = enableTime ? 'M j, Y h:i K' : 'M j, Y';

    // Build parseDate that tries flexible formats first, then falls back
    const customParseDate = function (dateStr, format) {
      // Try our flexible parser first
      const parsed = parseFlexibleDate(dateStr);
      if (parsed && !isNaN(parsed.getTime())) {
        // If time is enabled but user typed date-only, add default time
        if (enableTime && !dateStr.includes(':') && !dateStr.includes('T')) {
          // Default: 9:00 AM for start, 5:00 PM for end
          if (inputName === 'start_dt') {
            parsed.setHours(9, 0, 0, 0);
          } else if (inputName === 'end_dt') {
            parsed.setHours(17, 0, 0, 0);
          }
        }
        return parsed;
      }
      // Let flatpickr try its default parsing
      return undefined;
    };

    // Merge with base config
    // Force 12-hour time picker (AM/PM) when time is enabled
    const timeConfig = enableTime ? { time_24hr: false } : {};

    const config = Object.assign({}, baseConfig, timeConfig, {
      altInput: true,
      altFormat: altFormat,
      allowInput: true,
      disableMobile: true,
      enableTime: enableTime,
      dateFormat: enableTime ? 'Y-m-d\\TH:i' : 'Y-m-d',
      parseDate: customParseDate,
      onReady: function (selectedDates, dateStr, instance) {
        // Mark the original input so CSS can hide it
        if (instance.input) {
          instance.input.setAttribute('data-fp-original', 'true');
        }
        // Call original onReady if present
        if (opts.onReady) {
          opts.onReady(selectedDates, dateStr, instance);
        }
        if (baseConfig.onReady) {
          if (Array.isArray(baseConfig.onReady)) {
            baseConfig.onReady.forEach(fn => fn(selectedDates, dateStr, instance));
          } else {
            baseConfig.onReady(selectedDates, dateStr, instance);
          }
        }
      },
      onChange: function (selectedDates, dateStr, instance) {
        // Call custom onChange if provided
        if (opts.onChange) {
          opts.onChange(selectedDates, dateStr, instance);
        }
        // Call original onChange if present
        if (baseConfig.onChange) {
          if (Array.isArray(baseConfig.onChange)) {
            baseConfig.onChange.forEach(fn => fn(selectedDates, dateStr, instance));
          } else {
            baseConfig.onChange(selectedDates, dateStr, instance);
          }
        }
      },
      onClose: function (selectedDates, dateStr, instance) {
        // Trigger change event for validation/listeners
        instance.input.dispatchEvent(new Event('change', { bubbles: true }));
        // Call original onClose if present
        if (baseConfig.onClose) {
          if (Array.isArray(baseConfig.onClose)) {
            baseConfig.onClose.forEach(fn => fn(selectedDates, dateStr, instance));
          } else {
            baseConfig.onClose(selectedDates, dateStr, instance);
          }
        }
      }
    });

    // Preserve minuteIncrement if provided
    if (baseConfig.minuteIncrement) {
      config.minuteIncrement = baseConfig.minuteIncrement;
    }

    return config;
  }

  /**
   * Initialize a single input with friendly date picker behavior.
   * 
   * @param {HTMLElement} inputEl - The input element to enhance
   * @param {Object} opts - Options
   * @param {boolean} opts.enableTime - Whether to enable time selection
   * @param {Function} opts.onChange - Custom onChange callback
   * @param {Function} opts.onReady - Custom onReady callback
   * @param {Date|string} opts.defaultDate - Default date value
   * @returns {Object|null} - The flatpickr instance, or null if skipped
   */
  function initFriendlyDateInput(inputEl, opts) {
    if (!inputEl) return null;
    opts = opts || {};

    // Guard against double-init
    if (inputEl._flatpickr || inputEl.classList.contains('flatpickr-input')) {
      return inputEl._flatpickr || null;
    }

    // Check if flatpickr is available
    if (typeof window.flatpickr !== 'function') {
      console.warn('GtsDateInputs: flatpickr not available');
      return null;
    }

    // Store original value before converting type
    const originalValue = inputEl.value;

    // For native date inputs, change type to text so flatpickr can work with it
    if (inputEl.type === 'date' || inputEl.type === 'datetime-local') {
      const wasDatetimeLocal = inputEl.type === 'datetime-local';
      inputEl.type = 'text';
      // If this was a datetime-local, enable time
      if (wasDatetimeLocal && opts.enableTime === undefined) {
        opts.enableTime = true;
      }
    }

    // Build config
    const baseConfig = {};
    if (opts.defaultDate) {
      baseConfig.defaultDate = opts.defaultDate;
    } else if (originalValue) {
      baseConfig.defaultDate = originalValue;
    }

    const config = buildFriendlyFlatpickrConfig(inputEl, baseConfig, opts);

    // Initialize flatpickr
    const fp = window.flatpickr(inputEl, config);
    return fp;
  }

  /**
   * Initialize all date inputs within a root element.
   * Skips inputs that are already initialized or explicitly excluded.
   * 
   * @param {HTMLElement} rootEl - The root element to scan (defaults to document)
   * @param {Object} opts - Options passed to each input
   */
  function initFriendlyDateInputs(rootEl, opts) {
    rootEl = rootEl || document;
    opts = opts || {};

    // Skip initialization inside #job-panel - panel.js handles its own date inputs
    // to preserve special behaviors like the wrapFlatpickr() integration
    const isInsidePanel = rootEl.id === 'job-panel' ||
      (rootEl.closest && rootEl.closest('#job-panel'));
    if (isInsidePanel) {
      return;
    }

    // Find date inputs that need initialization
    const selector = [
      'input[type="date"]',
      'input[type="datetime-local"]'
    ].join(', ');

    const inputs = rootEl.querySelectorAll ?
      rootEl.querySelectorAll(selector) :
      document.querySelectorAll(selector);

    inputs.forEach(function (input) {
      // Skip inputs inside #job-panel (they're handled by panel.js)
      if (input.closest && input.closest('#job-panel')) {
        return;
      }

      // Skip inputs that are explicitly excluded
      if (input.dataset.noFriendlyDate === 'true') {
        return;
      }

      // Determine if time should be enabled based on input type
      const enableTime = input.type === 'datetime-local' || opts.enableTime === true;

      initFriendlyDateInput(input, {
        enableTime: enableTime,
        onChange: opts.onChange,
        onReady: opts.onReady
      });
    });
  }

  // Expose the API globally
  window.GtsDateInputs = {
    parseFlexibleDate: parseFlexibleDate,
    parseISOLocal: parseISOLocal,
    formatISODate: formatISODate,
    formatISODateTimeLocal: formatISODateTimeLocal,
    buildFriendlyFlatpickrConfig: buildFriendlyFlatpickrConfig,
    initFriendlyDateInput: initFriendlyDateInput,
    initFriendlyDateInputs: initFriendlyDateInputs
  };

})();
