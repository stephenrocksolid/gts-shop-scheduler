// rental_scheduler/static/rental_scheduler/js/panel.js
(function () {
  function clamp(n, min, max) { return Math.max(min, Math.min(max, n)); }
  const STORAGE_KEY = 'jobPanelState';

  /**
   * Normalize job ID to string for consistent usage with JobWorkspace
   */
  function normalizeJobId(jobId) {
    return jobId != null ? String(jobId) : null;
  }

  // Initialize global API immediately
  let panelInstance = null;
  let isAlpineMode = false;

  // Queue for operations before panel is ready
  let operationQueue = [];

  function executeOperation(op) {
    if (panelInstance) {
      op();
    } else {
      operationQueue.push(op);
    }
  }

  function flushQueue() {
    while (operationQueue.length > 0) {
      const op = operationQueue.shift();
      op();
    }
  }

  // ==========================================================================
  // HTML SANITIZATION FOR DRAFT RESTORE
  // Trims whitespace from value attributes of numeric/date inputs to prevent
  // browser parsing errors when restoring cached HTML from localStorage.
  // ==========================================================================

  /**
   * Sanitize cached HTML before inserting into the DOM.
   * Trims value attributes for input types that don't accept whitespace.
   * @param {string} html - Raw HTML string (e.g., from localStorage draft)
   * @returns {string} - Sanitized HTML string
   */
  function sanitizeDraftHtml(html) {
    if (!html || typeof html !== 'string') return html;

    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');

      // Input types that cannot have whitespace in their value attribute
      const strictValueTypes = ['number', 'date', 'datetime-local', 'time', 'month', 'week'];
      const selector = strictValueTypes.map(t => `input[type="${t}"]`).join(', ');

      const inputs = doc.querySelectorAll(selector);
      inputs.forEach(input => {
        if (input.hasAttribute('value')) {
          const rawValue = input.getAttribute('value');
          const trimmed = rawValue.trim();
          input.setAttribute('value', trimmed);
        }
      });

      // Return the sanitized body innerHTML
      return doc.body.innerHTML;
    } catch (e) {
      console.warn('sanitizeDraftHtml: Error parsing HTML, returning original', e);
      return html;
    }
  }

  /**
   * Serialize panel body HTML for draft storage, preserving form state.
   * Unlike innerHTML alone, this persists checkbox/radio checked state and select values
   * by setting the corresponding HTML attributes to match runtime properties.
   * @param {HTMLElement} panelBody - The panel body element to serialize
   * @returns {string} - HTML string with form state preserved
   */
  function serializeDraftHtml(panelBody) {
    if (!panelBody) return null;

    try {
      // Clone the panel body so we don't modify the live DOM
      const clone = panelBody.cloneNode(true);

      // Persist checkbox and radio checked state as attributes
      clone.querySelectorAll('input[type="checkbox"], input[type="radio"]').forEach(input => {
        const original = panelBody.querySelector(`#${CSS.escape(input.id)}`) ||
          panelBody.querySelector(`input[name="${CSS.escape(input.name)}"][type="${input.type}"]`);
        if (original) {
          if (original.checked) {
            input.setAttribute('checked', 'checked');
          } else {
            input.removeAttribute('checked');
          }
        }
      });

      // Persist select element selected state
      clone.querySelectorAll('select').forEach(select => {
        const original = panelBody.querySelector(`#${CSS.escape(select.id)}`) ||
          panelBody.querySelector(`select[name="${CSS.escape(select.name)}"]`);
        if (original) {
          // Clear all selected attributes first
          select.querySelectorAll('option').forEach(opt => opt.removeAttribute('selected'));
          // Set selected on the currently selected option(s)
          Array.from(original.selectedOptions).forEach(origOpt => {
            const cloneOpt = select.querySelector(`option[value="${CSS.escape(origOpt.value)}"]`);
            if (cloneOpt) {
              cloneOpt.setAttribute('selected', 'selected');
            }
          });
        }
      });

      // Persist textarea values (innerHTML doesn't capture typed content)
      clone.querySelectorAll('textarea').forEach(textarea => {
        const original = panelBody.querySelector(`#${CSS.escape(textarea.id)}`) ||
          panelBody.querySelector(`textarea[name="${CSS.escape(textarea.name)}"]`);
        if (original) {
          textarea.textContent = original.value;
        }
      });

      // Persist text/number/date input values
      clone.querySelectorAll('input[type="text"], input[type="number"], input[type="date"], input[type="datetime-local"], input[type="email"], input[type="tel"]').forEach(input => {
        const original = panelBody.querySelector(`#${CSS.escape(input.id)}`) ||
          panelBody.querySelector(`input[name="${CSS.escape(input.name)}"]`);
        if (original) {
          input.setAttribute('value', original.value);
        }
      });

      return clone.innerHTML;
    } catch (e) {
      console.warn('serializeDraftHtml: Error serializing, falling back to innerHTML', e);
      return panelBody.innerHTML;
    }
  }

  // ==========================================================================
  // JOB FORM TOGGLE UI (Call Reminder + Recurrence)
  // Centralized, idempotent handler for checkbox-driven expand/collapse sections.
  // ==========================================================================

  /**
   * Sync visibility of toggle-controlled sections based on checkbox state.
   * @param {HTMLElement} rootEl - The root element to scope queries to (e.g., panel body)
   */
  function syncJobFormToggles(rootEl) {
    if (!rootEl) return;

    // Call reminder toggle
    const callReminderCheckbox = rootEl.querySelector('#call-reminder-enabled');
    const callReminderOptions = rootEl.querySelector('#call-reminder-options');
    if (callReminderCheckbox && callReminderOptions) {
      if (callReminderCheckbox.checked) {
        callReminderOptions.classList.remove('call-reminder-hidden');
        callReminderOptions.classList.add('call-reminder-visible');
      } else {
        callReminderOptions.classList.remove('call-reminder-visible');
        callReminderOptions.classList.add('call-reminder-hidden');
      }
    }

    // Recurrence toggle
    const recurrenceCheckbox = rootEl.querySelector('#recurrence-enabled');
    const recurrenceOptions = rootEl.querySelector('#recurrence-options');
    if (recurrenceCheckbox && recurrenceOptions) {
      if (recurrenceCheckbox.checked) {
        recurrenceOptions.classList.remove('recurrence-hidden');
        recurrenceOptions.classList.add('recurrence-visible');
      } else {
        recurrenceOptions.classList.remove('recurrence-visible');
        recurrenceOptions.classList.add('recurrence-hidden');
      }
    }
  }

  /**
   * Initialize job form toggle UI with a single delegated change listener.
   * Idempotent - safe to call multiple times on the same element.
   * @param {HTMLElement} rootEl - The root element to scope to (e.g., panel body or form)
   */
  function initJobFormToggleUI(rootEl) {
    if (!rootEl) return;

    // Guard against double-binding using a data attribute
    if (rootEl.dataset.toggleUiInit === '1') {
      // Already initialized, just sync visibility in case checkbox state changed
      syncJobFormToggles(rootEl);
      return;
    }
    rootEl.dataset.toggleUiInit = '1';

    // Attach a single delegated change listener for toggle checkboxes
    rootEl.addEventListener('change', function (e) {
      const target = e.target;
      if (!target) return;

      // Handle call reminder toggle
      if (target.id === 'call-reminder-enabled' || target.name === 'has_call_reminder') {
        const options = rootEl.querySelector('#call-reminder-options');
        if (options) {
          if (target.checked) {
            options.classList.remove('call-reminder-hidden');
            options.classList.add('call-reminder-visible');
          } else {
            options.classList.remove('call-reminder-visible');
            options.classList.add('call-reminder-hidden');
          }
        }
      }

      // Handle recurrence toggle
      if (target.id === 'recurrence-enabled' || target.name === 'recurrence_enabled') {
        const options = rootEl.querySelector('#recurrence-options');
        if (options) {
          if (target.checked) {
            options.classList.remove('recurrence-hidden');
            options.classList.add('recurrence-visible');
          } else {
            options.classList.remove('recurrence-visible');
            options.classList.add('recurrence-hidden');
          }
        }
      }
    });

    // Sync initial state immediately
    syncJobFormToggles(rootEl);
  }

  // Expose for use elsewhere
  window.initJobFormToggleUI = initJobFormToggleUI;
  window.syncJobFormToggles = syncJobFormToggles;

  // ==========================================================================
  // FRIENDLY DATE PICKER ENHANCEMENT
  // Wraps flatpickr to show user-friendly format (Dec 22, 2026) while
  // keeping ISO values for form submission. Supports flexible typed input.
  // ==========================================================================

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

    // Month name map
    const months = {
      jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5,
      jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11
    };

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
      if (months.hasOwnProperty(monthKey)) {
        month = months[monthKey];
        day = parseInt(m[2], 10);
        year = parseInt(m[3], 10);
        return new Date(year, month, day);
      }
    }

    // Try "Mon D, YYYY h:mm AM/PM" or similar with time
    m = str.match(/^([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})\s+(\d{1,2}):(\d{2})\s*(AM|PM)?$/i);
    if (m) {
      const monthKey = m[1].toLowerCase().slice(0, 3);
      if (months.hasOwnProperty(monthKey)) {
        month = months[monthKey];
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
   * Get flatpickr configuration enhanced for friendly display in #job-panel.
   * @param {HTMLElement} el - The input element
   * @param {Object} baseConfig - Original config passed to flatpickr
   * @returns {Object} - Enhanced config
   */
  function getPanelFlatpickrConfig(el, baseConfig) {
    const enableTime = baseConfig.enableTime === true;
    const inputName = el.name || '';

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

    return Object.assign({}, baseConfig, timeConfig, {
      altInput: true,
      altFormat: altFormat,
      allowInput: true,
      disableMobile: true,
      parseDate: customParseDate,
      onReady: function (selectedDates, dateStr, instance) {
        // Mark the original input so CSS can hide it
        if (instance.input) {
          instance.input.setAttribute('data-fp-original', 'true');
        }
        // Call original onReady if present
        if (baseConfig.onReady) {
          if (Array.isArray(baseConfig.onReady)) {
            baseConfig.onReady.forEach(fn => fn(selectedDates, dateStr, instance));
          } else {
            baseConfig.onReady(selectedDates, dateStr, instance);
          }
        }
      }
    });
  }

  /**
   * Wrap the global flatpickr function to enhance inputs inside #job-panel.
   * This must run before schedule_picker.js initializes flatpickr on date inputs.
   */
  function wrapFlatpickr() {
    if (window._panelFlatpickrWrapped) return;
    if (typeof window.flatpickr !== 'function') return;

    const originalFlatpickr = window.flatpickr;
    window._panelFlatpickrWrapped = true;

    window.flatpickr = function (selector, config) {
      config = config || {};

      // Handle string selector or element
      let elements;
      if (typeof selector === 'string') {
        elements = document.querySelectorAll(selector);
      } else if (selector instanceof Element) {
        elements = [selector];
      } else if (selector && selector.length !== undefined) {
        elements = selector;
      } else {
        elements = [selector];
      }

      // If single element and it's inside #job-panel, enhance config
      const results = [];
      for (const el of elements) {
        if (el && el.closest && el.closest('#job-panel')) {
          const enhancedConfig = getPanelFlatpickrConfig(el, config);
          results.push(originalFlatpickr(el, enhancedConfig));
        } else {
          results.push(originalFlatpickr(el, config));
        }
      }

      // Return single instance or array like original flatpickr
      return results.length === 1 ? results[0] : results;
    };

    // Copy static properties from original
    for (const key in originalFlatpickr) {
      if (originalFlatpickr.hasOwnProperty(key)) {
        window.flatpickr[key] = originalFlatpickr[key];
      }
    }
  }

  /**
   * Initialize flatpickr on date-only inputs in the panel that aren't
   * handled by schedule_picker.js (e.g., date_call_received, recurrence_until).
   */
  function initPanelDatePickers() {
    const panel = document.getElementById('job-panel');
    if (!panel) return;

    // Find date inputs that don't already have flatpickr and aren't start/end
    const dateInputs = panel.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
      // Skip if already has flatpickr
      if (input._flatpickr || input.classList.contains('flatpickr-input')) return;
      // Skip start_dt and end_dt (handled by schedule_picker.js)
      if (input.name === 'start_dt' || input.name === 'end_dt') return;

      // Store original value before converting
      const originalValue = input.value;

      // Change type to text so flatpickr can work with it
      input.type = 'text';

      // Initialize flatpickr with friendly format
      const fp = window.flatpickr(input, {
        dateFormat: 'Y-m-d',
        altInput: true,
        altFormat: 'M j, Y',
        allowInput: true,
        disableMobile: true,
        defaultDate: originalValue || null,
        parseDate: function (dateStr) {
          const parsed = parseFlexibleDate(dateStr);
          if (parsed && !isNaN(parsed.getTime())) {
            return parsed;
          }
          return undefined;
        },
        onReady: function (selectedDates, dateStr, instance) {
          if (instance.input) {
            instance.input.setAttribute('data-fp-original', 'true');
          }
        }
      });
    });
  }

  // Wrap flatpickr as early as possible
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wrapFlatpickr);
  } else {
    wrapFlatpickr();
  }

  // Initialize panel components after HTMX swaps
  document.body.addEventListener('htmx:afterSwap', function (event) {
    // Check if swap happened inside the panel
    const panel = document.getElementById('job-panel');
    if (panel && panel.contains(event.target)) {
      setTimeout(() => {
        initPanelDatePickers();
        // Initialize toggle UI (call reminder, recurrence)
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (panelBody) {
          initJobFormToggleUI(panelBody);
        }
      }, 100);
    }
  });

  document.body.addEventListener('htmx:load', function (event) {
    setTimeout(() => {
      initPanelDatePickers();
      // Initialize toggle UI (call reminder, recurrence)
      const panelBody = document.querySelector('#job-panel .panel-body');
      if (panelBody) {
        initJobFormToggleUI(panelBody);
      }
    }, 100);
  });

  // Vanilla JS fallback implementation
  function createVanillaPanel() {
    const panelEl = document.getElementById('job-panel');
    if (!panelEl) {
      console.error('Panel element not found');
      return null;
    }

    const st = load() || {};
    const panel = {
      isOpen: st.isOpen || false,
      title: st.title || 'Job',
      x: st.x || 80,
      y: st.y || 80,
      w: st.w || 520,
      h: st.h || null,
      docked: st.docked || false,
      dragging: false,
      sx: 0,
      sy: 0,
      isSwitchingJobs: false,  // Flag to prevent auto-close when switching between jobs
      currentJobId: null, // Track current job for workspace integration

      updateVisibility() {
        if (this.isOpen) {
          panelEl.classList.remove('hidden');
          panelEl.classList.add('block');
        } else {
          panelEl.classList.add('hidden');
          panelEl.classList.remove('block');
        }
      },

      updatePosition() {
        if (this.docked) {
          panelEl.style.top = '80px';
          panelEl.style.right = '16px';
          panelEl.style.left = 'auto';
          panelEl.style.transform = 'none';
        } else {
          panelEl.style.top = '0';
          panelEl.style.left = '0';
          panelEl.style.transform = `translate(${this.x}px, ${this.y}px)`;
        }
        this.constrainToViewport();
      },

      constrainToViewport() {
        const rect = panelEl.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;

        // If panel extends beyond bottom of viewport, constrain its height
        if (rect.bottom > viewportHeight) {
          const availableHeight = viewportHeight - rect.top - 20; // 20px margin
          if (availableHeight > 100) { // min-height
            panelEl.style.height = availableHeight + 'px';
            panelEl.style.maxHeight = availableHeight + 'px';
          } else {
            // Move panel up if there's not enough space
            const newY = Math.max(20, viewportHeight - parseInt(panelEl.style.height || 200) - 20);
            this.y = newY;
            panelEl.style.transform = `translate(${this.x}px, ${this.y}px)`;
          }
        }

        // Ensure panel doesn't exceed viewport width
        if (rect.right > viewportWidth) {
          const availableWidth = viewportWidth - rect.left - 20;
          if (availableWidth > 200) { // min-width
            panelEl.style.width = availableWidth + 'px';
          }
        }
      },

      open() {
        this.isOpen = true;
        this.updateVisibility();
        this.updateMinimizeButton();
        save(this);
      },

      close(skipUnsavedCheck) {
        // Check for unsaved changes before closing (unless explicitly skipped)
        if (!skipUnsavedCheck && this.hasUnsavedChanges()) {
          if (!confirm('You have unsaved changes. Are you sure you want to close without saving?')) {
            return; // User cancelled, don't close
          }
        }

        this.isOpen = false;
        this.updateVisibility();
        this.currentJobId = null; // Clear current job ID when closing
        this.updateMinimizeButton(); // Hide minimize button
        save(this);
      },

      setTitle(t) {
        this.title = t || 'Job';
        const titleEl = document.getElementById('job-panel-title');
        if (titleEl) titleEl.textContent = this.title;
        save(this);
      },

      setCurrentJobId(jobId) {
        this.currentJobId = normalizeJobId(jobId);
        this.updateMinimizeButton();
      },

      updateMinimizeButton() {
        const minimizeBtn = document.getElementById('panel-workspace-minimize-btn');
        if (!minimizeBtn) return;

        // Always show minimize button when panel is open
        if (this.isOpen) {
          minimizeBtn.style.display = 'inline-flex';
        } else {
          minimizeBtn.style.display = 'none';
        }
      },

      toggleDock() {
        this.docked = !this.docked;
        this.updatePosition();
        save(this);
      },

      setupDragging() {
        const header = panelEl.querySelector('.panel-header');
        if (!header) return;

        const onMouseDown = (e) => {
          if (this.docked) return;
          const p = e.touches?.[0] ?? e;
          this.dragging = true;
          this.sx = p.clientX - this.x;
          this.sy = p.clientY - this.y;

          document.addEventListener('mousemove', onMouseMove);
          document.addEventListener('mouseup', onMouseUp);
          document.addEventListener('touchmove', onMouseMove, { passive: false });
          document.addEventListener('touchend', onMouseUp);
        };

        const onMouseMove = (ev) => {
          if (!this.dragging) return;
          const p = ev.touches?.[0] ?? ev;
          const maxX = window.innerWidth - 200;
          const maxY = window.innerHeight - 48;
          this.x = clamp(p.clientX - this.sx, 8, maxX);
          this.y = clamp(p.clientY - this.sy, 8, maxY);
          this.updatePosition();
          ev.preventDefault();
        };

        const onMouseUp = () => {
          this.dragging = false;
          document.removeEventListener('mousemove', onMouseMove);
          document.removeEventListener('mouseup', onMouseUp);
          document.removeEventListener('touchmove', onMouseMove);
          document.removeEventListener('touchend', onMouseUp);
          save(this);
        };

        header.addEventListener('mousedown', onMouseDown);
        header.addEventListener('touchstart', onMouseDown, { passive: true });
      },

      hasUnsavedChanges() {
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) {
          console.log('hasUnsavedChanges: No panel body found');
          return false;
        }

        // Check for any form inputs that have been modified
        const inputs = panelBody.querySelectorAll('input, select, textarea');
        console.log('hasUnsavedChanges: Checking', inputs.length, 'inputs');

        for (const input of inputs) {
          // Skip hidden inputs and buttons
          if (input.type === 'hidden' || input.type === 'submit' || input.type === 'button') {
            continue;
          }

          // Skip inputs without a name attribute - they don't submit and are UI-only
          // (e.g., flatpickr alt display inputs, cloned header selects, etc.)
          if (!input.name) {
            continue;
          }

          // Check if the current value differs from the original value
          if (input.hasAttribute('data-original-value')) {
            const originalValue = input.getAttribute('data-original-value');
            const currentValue = input.value;
            if (originalValue !== currentValue) {
              console.log('hasUnsavedChanges: Found change in', input.name, 'original:', originalValue, 'current:', currentValue);
              return true;
            }
          } else if (input.value !== '') {
            // If no original value stored but input has a value, it might be a change
            // This is a fallback for inputs that weren't tracked from the start
            console.log('hasUnsavedChanges: Found untracked field with value:', input.name, 'value:', input.value);
            return true;
          }
        }

        console.log('hasUnsavedChanges: No changes detected');
        return false;
      },

      trackFormChanges() {
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) {
          console.log('trackFormChanges: No panel body found');
          return;
        }

        // Store original values for all form inputs
        const inputs = panelBody.querySelectorAll('input, select, textarea');
        console.log('trackFormChanges: Setting tracking on', inputs.length, 'inputs');
        inputs.forEach(input => {
          // Skip inputs without a name attribute - they don't submit and are UI-only
          if (!input.name) {
            return;
          }
          if (input.type !== 'hidden' && input.type !== 'submit' && input.type !== 'button') {
            input.setAttribute('data-original-value', input.value);
          }
        });
      },

      clearUnsavedChanges() {
        // Reset tracking by updating all original values to current values
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) return;

        const inputs = panelBody.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
          // Skip inputs without a name attribute - they don't submit and are UI-only
          if (!input.name) {
            return;
          }
          if (input.type !== 'hidden' && input.type !== 'submit' && input.type !== 'button') {
            input.setAttribute('data-original-value', input.value);
          }
        });
      },

      /**
       * Check which required fields are missing from the form.
       * Required fields: business_name, start_dt, end_dt, calendar
       * @param {HTMLFormElement} form - The form element
       * @returns {string[]} - Array of missing field names (empty if all present)
       */
      getRequiredMissing(form) {
        if (!form) return ['form'];
        const missing = [];

        // Business name - required and must not be whitespace-only
        const businessName = form.querySelector('input[name="business_name"]');
        if (!businessName || !businessName.value.trim()) {
          missing.push('business_name');
        }

        // Start date - required
        const startDt = form.querySelector('input[name="start_dt"]');
        if (!startDt || !startDt.value.trim()) {
          missing.push('start_dt');
        }

        // End date - required
        const endDt = form.querySelector('input[name="end_dt"]');
        if (!endDt || !endDt.value.trim()) {
          missing.push('end_dt');
        }

        // Calendar - required (select element)
        const calendar = form.querySelector('select[name="calendar"]');
        if (!calendar || !calendar.value) {
          missing.push('calendar');
        }

        return missing;
      },

      /**
       * Check if any required fields are missing.
       * @param {HTMLFormElement} form - The form element
       * @returns {boolean} - True if any required fields are missing
       */
      hasRequiredMissing(form) {
        return this.getRequiredMissing(form).length > 0;
      },

      /**
       * Minimize to workspace as draft/unsaved. Used by both minimize button and outside-click.
       * Reuses existing draft if present, otherwise creates one. Always closes the panel.
       * @param {Object} options
       * @param {string|null} options.jobId - Real job ID (if exists)
       * @param {Object} options.meta - Job metadata {customerName, trailerColor, calendarColor}
       * @param {string|null} options.currentHtml - Panel HTML content for restoration
       */
      minimizeAsDraft(options) {
        const { jobId, meta, currentHtml } = options;

        if (jobId && window.JobWorkspace) {
          // EXISTING JOB: minimize and mark as unsaved
          if (!window.JobWorkspace.hasJob(jobId)) {
            window.JobWorkspace.openJob(jobId, meta);
            this.setCurrentJobId(jobId);
          }

          // Mark as unsaved with current HTML BEFORE minimizing (so it's stored)
          if (window.JobWorkspace.markUnsaved) {
            window.JobWorkspace.markUnsaved(jobId, currentHtml);
          }

          // Minimize - this closes the panel
          window.JobWorkspace.minimizeJob(jobId);

        } else {
          // NEW JOB: reuse existing draft or create one
          let draftId = window.JobPanel.currentDraftId;

          if (draftId && window.JobWorkspace && window.JobWorkspace.hasJob(draftId)) {
            // Reuse existing draft - update meta and HTML
            if (window.JobWorkspace.updateJobMeta) {
              window.JobWorkspace.updateJobMeta(draftId, meta);
            }
            if (window.JobWorkspace.markUnsaved) {
              window.JobWorkspace.markUnsaved(draftId, currentHtml);
            }
          } else if (window.JobWorkspace && window.JobWorkspace.createDraft) {
            // Create new draft
            draftId = window.JobWorkspace.createDraft({
              customerName: meta.customerName || 'New Job',
              trailerColor: meta.trailerColor,
              calendarColor: meta.calendarColor,
              html: currentHtml
            });
            window.JobPanel.currentDraftId = draftId;
          } else {
            console.error('Cannot minimize: JobWorkspace not available');
            return;
          }

          // Minimize the draft - this closes the panel
          if (draftId && window.JobWorkspace) {
            window.JobWorkspace.minimizeJob(draftId);
          }
        }
      },

      /**
       * Save the form without causing page navigation.
       * Uses HTMX if the form has hx-post, otherwise uses fetch().
       * Handles draft promotion automatically on successful save.
       * @param {Object|Function} optionsOrCallback - Options object or callback function (for backwards compatibility)
       *   - mode: 'manual' | 'autosave' (default: 'autosave')
       *     - 'manual': Run HTML5 validation, block if invalid, show validation messages
       *     - 'autosave': Skip validation display, return unsuccessful if required fields missing
       * @param {Function} callback - Called with result object: { successful, jobId, responseHtml, status, reason }
       */
      saveForm(optionsOrCallback, callback) {
        // Handle backwards compatibility: saveForm(callback) vs saveForm(options, callback)
        let options = { mode: 'autosave' };
        if (typeof optionsOrCallback === 'function') {
          callback = optionsOrCallback;
        } else if (optionsOrCallback && typeof optionsOrCallback === 'object') {
          options = { ...options, ...optionsOrCallback };
        }
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) {
          console.warn('Panel body not found');
          if (callback) callback({ successful: false, jobId: null, responseHtml: null, status: null });
          return;
        }

        const form = panelBody.querySelector('form');
        if (!form) {
          console.warn('Form not found in panel');
          if (callback) callback({ successful: false, jobId: null, responseHtml: null, status: null });
          return;
        }

        const self = this;
        const mode = options.mode || 'autosave';

        // Check for missing required fields
        const missingFields = this.getRequiredMissing(form);
        const hasMissing = missingFields.length > 0;

        if (mode === 'manual') {
          // Manual save mode: run HTML5 validation and show messages
          if (hasMissing) {
            // Trigger HTML5 validation display
            if (!form.reportValidity()) {
              if (window.showToast) {
                window.showToast('Please fill in all required fields before saving.', 'warning');
              }
              if (callback) callback({ successful: false, jobId: null, responseHtml: null, status: null, reason: 'missing_required', missingFields });
              return;
            }
          }
        } else {
          // Autosave mode: don't show validation popups, just return unsuccessful
          if (hasMissing) {
            console.log('saveForm autosave skipped: missing required fields', missingFields);
            if (callback) callback({ successful: false, jobId: null, responseHtml: null, status: null, reason: 'missing_required', missingFields });
            return;
          }
        }

        /**
         * Handle draft promotion after successful save
         */
        const handleDraftPromotion = (jobId) => {
          if (jobId && window.JobPanel.currentDraftId && window.JobWorkspace && window.JobWorkspace.promoteDraft) {
            const draftId = window.JobPanel.currentDraftId;
            window.JobWorkspace.promoteDraft(draftId, jobId, {});
            window.JobPanel.currentDraftId = null;
            console.log('Promoted draft', draftId, 'to job', jobId);
          }
        };

        // Check if form has HTMX attributes (hx-post, hx-put, etc.)
        const hasHtmxPost = form.hasAttribute('hx-post') || form.hasAttribute('hx-put') ||
          form.hasAttribute('hx-patch') || form.hasAttribute('hx-delete');

        if (typeof htmx !== 'undefined' && hasHtmxPost) {
          // Use HTMX submission - it won't navigate because the form has hx-* attrs
          const afterRequestHandler = (event) => {
            const xhr = event.detail.xhr;
            const successful = event.detail.successful;
            const status = xhr ? xhr.status : null;
            const responseHtml = xhr ? xhr.responseText : null;
            let jobId = null;

            if (successful) {
              // Clear unsaved changes tracking
              self.clearUnsavedChanges();

              // Capture job ID from HX-Trigger header
              if (xhr) {
                const triggerHeader = xhr.getResponseHeader('HX-Trigger');
                if (triggerHeader) {
                  try {
                    const triggerData = JSON.parse(triggerHeader);
                    if (triggerData.jobSaved && triggerData.jobSaved.jobId) {
                      jobId = normalizeJobId(triggerData.jobSaved.jobId);
                      self.currentJobId = jobId;
                      console.log('Captured job ID from trigger:', jobId);
                    }
                  } catch (e) {
                    console.warn('Could not parse trigger data:', e);
                  }
                }
              }

              // Fallback: try to get from DOM
              if (!jobId) {
                const jobIdInput = form.querySelector('input[name="job_id"]');
                if (jobIdInput && jobIdInput.value) {
                  jobId = normalizeJobId(jobIdInput.value);
                  self.currentJobId = jobId;
                  console.log('Captured job ID from DOM fallback:', jobId);
                }
              }

              // Handle draft promotion
              handleDraftPromotion(jobId);

              // Migrate warning key from temp to job ID
              if (jobId && window.migrateWarningKeyToJobId) {
                window.migrateWarningKeyToJobId(form, jobId);
              }
            } else {
              console.error('Form submission failed with status:', status);
            }

            form.removeEventListener('htmx:afterRequest', afterRequestHandler);
            if (callback) callback({ successful, jobId, responseHtml, status });
          };

          form.addEventListener('htmx:afterRequest', afterRequestHandler);
          htmx.trigger(form, 'submit');

        } else {
          // Use fetch() to avoid navigation - never call form.submit()
          const formData = new FormData(form);
          const actionUrl = form.getAttribute('hx-post') || form.getAttribute('action') || window.location.href;
          const csrfToken = window.getCookie ? window.getCookie('csrftoken') :
            document.querySelector('meta[name="csrf-token"]')?.content ||
            form.querySelector('input[name="csrfmiddlewaretoken"]')?.value;

          fetch(actionUrl, {
            method: 'POST',
            body: formData,
            headers: {
              'X-CSRFToken': csrfToken || '',
              'X-Requested-With': 'XMLHttpRequest'
            }
          })
            .then(response => {
              return response.text().then(html => ({
                successful: response.ok,
                status: response.status,
                responseHtml: html,
                headers: response.headers
              }));
            })
            .then(result => {
              let jobId = null;

              if (result.successful) {
                self.clearUnsavedChanges();

                // Try to parse HX-Trigger from response headers
                const triggerHeader = result.headers.get('HX-Trigger');
                if (triggerHeader) {
                  try {
                    const triggerData = JSON.parse(triggerHeader);
                    if (triggerData.jobSaved && triggerData.jobSaved.jobId) {
                      jobId = normalizeJobId(triggerData.jobSaved.jobId);
                      self.currentJobId = jobId;
                      console.log('Captured job ID from fetch trigger:', jobId);
                    }
                  } catch (e) {
                    console.warn('Could not parse trigger data:', e);
                  }
                }

                // Fallback: try to extract job_id from response HTML
                if (!jobId && result.responseHtml) {
                  const match = result.responseHtml.match(/name="job_id"\s+value="(\d+)"/);
                  if (match) {
                    jobId = normalizeJobId(match[1]);
                    self.currentJobId = jobId;
                    console.log('Captured job ID from response HTML:', jobId);
                  }
                }

                // Handle draft promotion
                handleDraftPromotion(jobId);

                // Migrate warning key from temp to job ID
                if (jobId && window.migrateWarningKeyToJobId) {
                  window.migrateWarningKeyToJobId(form, jobId);
                }
              } else {
                console.error('Form submission failed with status:', result.status);
              }

              if (callback) callback({
                successful: result.successful,
                jobId,
                responseHtml: result.responseHtml,
                status: result.status
              });
            })
            .catch(error => {
              console.error('Fetch error:', error);
              if (callback) callback({ successful: false, jobId: null, responseHtml: null, status: null });
            });
        }
      },

      setupButtons() {
        // Close button - closes and removes job from workspace
        // If required fields are missing, just close without saving (discard incomplete job)
        // If required fields are present and there are changes, save first then close
        const closeBtn = panelEl.querySelector('.panel-header .btn-close');
        if (closeBtn) {
          closeBtn.addEventListener('click', () => {
            const self = this;
            const form = document.querySelector('#job-panel .panel-body form');
            const missingFields = this.getRequiredMissing(form);
            const hasMissingRequired = missingFields.length > 0;

            // If required fields are missing, just close without attempting save
            if (hasMissingRequired) {
              // Close the panel and remove from workspace
              if (self.currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob(self.currentJobId)) {
                window.JobWorkspace.closeJob(self.currentJobId);
              } else if (window.JobPanel.currentDraftId && window.JobWorkspace) {
                // Also clean up any draft
                window.JobWorkspace.closeJob(window.JobPanel.currentDraftId);
                window.JobPanel.currentDraftId = null;
              }
              self.close(true);
              return;
            }

            // Required fields present - If there are unsaved changes, save first
            if (this.hasUnsavedChanges()) {
              this.saveForm((result) => {
                // After saving (success or fail), close/remove from workspace
                if (self.currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob(self.currentJobId)) {
                  window.JobWorkspace.closeJob(self.currentJobId);
                } else {
                  self.close(true);
                }
              });
            } else {
              // No unsaved changes, just close
              if (this.currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob(this.currentJobId)) {
                window.JobWorkspace.closeJob(this.currentJobId);
              } else {
                this.close(true);
              }
            }
          });
        }

        // Workspace minimize button - HYBRID BEHAVIOR:
        // - If required fields missing: minimize as draft immediately (no DB save)
        // - If job has ID and required fields present: minimize immediately, save in background if dirty
        // - If new job and required fields present: save first to get ID, then minimize
        const workspaceMinimizeBtn = document.getElementById('panel-workspace-minimize-btn');
        if (workspaceMinimizeBtn && !workspaceMinimizeBtn.dataset.bound) {
          workspaceMinimizeBtn.dataset.bound = '1';  // Guard against double-binding
          workspaceMinimizeBtn.addEventListener('click', () => {
            const self = this;
            const form = document.querySelector('#job-panel .panel-body form');
            const panelBody = document.querySelector('#job-panel .panel-body');
            const jobIdInput = form?.querySelector('input[name="job_id"]');
            let jobId = this.currentJobId || (jobIdInput ? jobIdInput.value : null);
            const isDirty = this.hasUnsavedChanges();

            // Helper to get job metadata from form
            const getJobMeta = () => ({
              customerName: form?.querySelector('input[name="business_name"]')?.value ||
                form?.querySelector('input[name="contact_name"]')?.value ||
                'Unnamed Job',
              trailerColor: form?.querySelector('input[name="trailer_color"]')?.value || '',
              calendarColor: '#3B82F6'
            });

            // Capture current panel HTML for potential unsaved state restoration
            // Use serializeDraftHtml to preserve checkbox/select state
            const currentHtml = panelBody ? serializeDraftHtml(panelBody) : null;

            // Check for missing required fields FIRST
            const missingFields = this.getRequiredMissing(form);
            const hasMissingRequired = missingFields.length > 0;

            if (hasMissingRequired) {
              // MISSING REQUIRED FIELDS: Minimize as draft immediately, NO DB save attempt
              console.log('Minimize with missing required fields:', missingFields);

              // Use shared helper - reuses existing draft if present, always closes panel
              self.minimizeAsDraft({
                jobId: jobId,
                meta: getJobMeta(),
                currentHtml: currentHtml
              });

              return; // Exit early - no network save attempted
            }

            // REQUIRED FIELDS PRESENT: Proceed with normal save flow
            if (jobId && window.JobWorkspace) {
              // EXISTING JOB: Minimize immediately, save in background if dirty

              // Capture meta now (before panel closes) for use in save callback
              const currentMeta = getJobMeta();

              // Ensure job is in workspace
              if (!window.JobWorkspace.hasJob(jobId)) {
                window.JobWorkspace.openJob(jobId, currentMeta);
                self.setCurrentJobId(jobId);
              }

              // Minimize immediately (instant UI response)
              window.JobWorkspace.minimizeJob(jobId);

              // If dirty, save in background
              if (isDirty) {
                window.JobPanel.isSwitchingJobs = true;

                self.saveForm((result) => {
                  window.JobPanel.isSwitchingJobs = false;

                  if (result.successful) {
                    // Clear unsaved state on success
                    if (window.JobWorkspace.clearUnsaved) {
                      window.JobWorkspace.clearUnsaved(jobId);
                    }
                    // Update tab meta after successful save (e.g. if name changed)
                    if (window.JobWorkspace.updateJobMeta) {
                      window.JobWorkspace.updateJobMeta(jobId, currentMeta);
                    }
                  } else {
                    // Mark as unsaved on failure
                    if (window.JobWorkspace.markUnsaved) {
                      window.JobWorkspace.markUnsaved(jobId, result.responseHtml || currentHtml);
                    }
                    window.showToast('Failed to save changes. Reopen the job to fix.', 'warning');
                  }
                });
              }

            } else {
              // NEW JOB: Must save first to get an ID, then minimize

              // Show saving state on button
              const originalBtnContent = workspaceMinimizeBtn.innerHTML;
              workspaceMinimizeBtn.disabled = true;
              workspaceMinimizeBtn.innerHTML = '<span style="font-size: 10px;">Saving…</span>';

              window.JobPanel.isSwitchingJobs = true;

              self.saveForm((result) => {
                window.JobPanel.isSwitchingJobs = false;
                workspaceMinimizeBtn.disabled = false;
                workspaceMinimizeBtn.innerHTML = originalBtnContent;

                if (result.successful && result.jobId) {
                  // Success: add to workspace and minimize
                  const newJobId = result.jobId;
                  self.setCurrentJobId(newJobId);

                  if (!window.JobWorkspace.hasJob(newJobId)) {
                    window.JobWorkspace.openJob(newJobId, getJobMeta());
                  }
                  window.JobWorkspace.minimizeJob(newJobId);

                } else {
                  // Failed to save new job - create a draft entry
                  if (window.JobWorkspace.createDraft) {
                    const meta = getJobMeta();
                    const draftId = window.JobWorkspace.createDraft({
                      customerName: meta.customerName,
                      trailerColor: meta.trailerColor,
                      calendarColor: meta.calendarColor,
                      html: result.responseHtml || currentHtml
                    });
                    // Store draft ID so we can promote it later on successful save
                    window.JobPanel.currentDraftId = draftId;
                    window.showToast('Job not saved yet. Reopen to fix errors.', 'warning');
                  } else {
                    window.showToast('Failed to save new job.', 'error');
                  }
                }
              });
            }
          });
        }

        // Delete button is handled by the global API via setDeleteCallback

        // ESC key - same behavior as close button
        // If required fields are missing, just close without saving
        document.addEventListener('keydown', (e) => {
          const self = this;
          if (e.key === 'Escape' && this.isOpen) {
            const form = document.querySelector('#job-panel .panel-body form');
            const missingFields = this.getRequiredMissing(form);
            const hasMissingRequired = missingFields.length > 0;

            // If required fields are missing, just close without attempting save
            if (hasMissingRequired) {
              if (self.currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob(self.currentJobId)) {
                window.JobWorkspace.closeJob(self.currentJobId);
              } else if (window.JobPanel.currentDraftId && window.JobWorkspace) {
                window.JobWorkspace.closeJob(window.JobPanel.currentDraftId);
                window.JobPanel.currentDraftId = null;
              }
              self.close(true);
              return;
            }

            // Required fields present - If there are unsaved changes, save first
            if (this.hasUnsavedChanges()) {
              this.saveForm((result) => {
                // After saving (success or fail), close/remove from workspace
                if (self.currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob(self.currentJobId)) {
                  window.JobWorkspace.closeJob(self.currentJobId);
                } else {
                  self.close(true);
                }
              });
            } else {
              // No unsaved changes, just close
              if (this.currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob(this.currentJobId)) {
                window.JobWorkspace.closeJob(this.currentJobId);
              } else {
                this.close(true);
              }
            }
          }
        });

        // Enter key navigation within panel
        document.addEventListener('keydown', (e) => {
          // Only apply when panel is open
          if (!panelEl || !this.isOpen) return;

          // Check if the focused element is inside the panel
          if (!panelEl.contains(e.target)) return;

          if (e.key === 'Enter') {
            const target = e.target;

            // Allow normal Enter in textarea (for new lines) unless Shift is pressed
            if (target.tagName === 'TEXTAREA' && !e.shiftKey) {
              return;
            }

            // Prevent default Enter behavior
            e.preventDefault();

            // Get all focusable fields within the panel
            const fields = Array.from(panelEl.querySelectorAll('input, select, textarea, button'))
              .filter(el => {
                // Filter out hidden, disabled, or invisible elements
                return !el.disabled &&
                  el.offsetParent !== null &&
                  el.type !== 'hidden' &&
                  !el.hasAttribute('readonly');
              });

            const idx = fields.indexOf(target);

            if (idx > -1 && idx < fields.length - 1) {
              // Move to next field
              fields[idx + 1].focus();
            } else if (idx === fields.length - 1 && target.form) {
              // Last field → submit the form
              target.form.requestSubmit();
            }
          }
        });
      },

      setupOutsideClick() {
        // Guard against double-binding
        if (window._panelOutsideClickBound) return;
        window._panelOutsideClickBound = true;

        const self = this;

        // Use mousedown to detect clicks before they propagate
        document.addEventListener('mousedown', (e) => {
          // Only handle if panel is open
          if (!self.isOpen) return;

          // Get the panel element
          const panel = document.getElementById('job-panel');
          if (!panel) return;

          // Check if click is outside the panel
          if (!panel.contains(e.target)) {
            // Ignore clicks on workspace bar tabs (they have their own handling)
            const workspaceBar = document.getElementById('workspace-bar');
            if (workspaceBar && workspaceBar.contains(e.target)) {
              return;
            }

            // Ignore clicks on calendar events (they need to open in panel)
            if (e.target.closest('.fc-event') || e.target.closest('.fc-daygrid-event')) {
              return;
            }

            // Ignore clicks on today sidebar items (they open jobs)
            if (e.target.closest('.today-item')) {
              return;
            }

            // Ignore clicks on search results job rows (they open jobs)
            if (e.target.closest('.job-row')) {
              return;
            }

            // Ignore clicks on popovers (FullCalendar more events popover)
            if (e.target.closest('.fc-popover')) {
              return;
            }

            // Ignore clicks on flatpickr date picker popups (they render in document.body, not inside panel)
            if (e.target.closest('.flatpickr-calendar') || e.target.closest('.flatpickr-wrapper') || e.target.closest('.numInputWrapper')) {
              return;
            }

            // HYBRID BEHAVIOR for outside click - mirrors minimize button behavior
            const form = document.querySelector('#job-panel .panel-body form');
            const panelBody = document.querySelector('#job-panel .panel-body');
            const jobIdInput = form?.querySelector('input[name="job_id"]');
            let jobId = self.currentJobId || (jobIdInput ? jobIdInput.value : null);
            const isDirty = self.hasUnsavedChanges();

            // Helper to get job metadata from form
            const getJobMeta = () => ({
              customerName: form?.querySelector('input[name="business_name"]')?.value ||
                form?.querySelector('input[name="contact_name"]')?.value ||
                'Unnamed Job',
              trailerColor: form?.querySelector('input[name="trailer_color"]')?.value || '',
              calendarColor: '#3B82F6'
            });

            // Capture current panel HTML for potential unsaved state restoration
            // Use serializeDraftHtml to preserve checkbox/select state
            const currentHtml = panelBody ? serializeDraftHtml(panelBody) : null;

            // Check for missing required fields
            const missingFields = self.getRequiredMissing(form);
            const hasMissingRequired = missingFields.length > 0;

            if (hasMissingRequired) {
              // MISSING REQUIRED FIELDS: Minimize as draft immediately, NO DB save attempt
              console.log('Outside click with missing required fields:', missingFields);

              // Use shared helper - reuses existing draft if present, always closes panel
              self.minimizeAsDraft({
                jobId: jobId,
                meta: getJobMeta(),
                currentHtml: currentHtml
              });
              return;
            }

            // REQUIRED FIELDS PRESENT: Follow hybrid minimize behavior
            if (jobId && window.JobWorkspace) {
              // EXISTING JOB: Minimize immediately, save in background if dirty
              const currentMeta = getJobMeta();

              if (!window.JobWorkspace.hasJob(jobId)) {
                window.JobWorkspace.openJob(jobId, currentMeta);
              }

              // Minimize immediately
              window.JobWorkspace.minimizeJob(jobId);

              // If dirty, save in background
              if (isDirty) {
                window.JobPanel.isSwitchingJobs = true;
                self.saveForm((result) => {
                  window.JobPanel.isSwitchingJobs = false;
                  if (result.successful) {
                    if (window.JobWorkspace.clearUnsaved) {
                      window.JobWorkspace.clearUnsaved(jobId);
                    }
                    if (window.JobWorkspace.updateJobMeta) {
                      window.JobWorkspace.updateJobMeta(jobId, currentMeta);
                    }
                  } else {
                    if (window.JobWorkspace.markUnsaved) {
                      window.JobWorkspace.markUnsaved(jobId, result.responseHtml || currentHtml);
                    }
                  }
                });
              }

            } else {
              // NEW JOB: Must save first to get an ID, then minimize
              window.JobPanel.isSwitchingJobs = true;

              self.saveForm((result) => {
                window.JobPanel.isSwitchingJobs = false;

                if (result.successful && result.jobId) {
                  // Success: add to workspace and minimize
                  const newJobId = result.jobId;
                  self.setCurrentJobId(newJobId);
                  const meta = getJobMeta();

                  if (!window.JobWorkspace.hasJob(newJobId)) {
                    window.JobWorkspace.openJob(newJobId, meta);
                  }
                  window.JobWorkspace.minimizeJob(newJobId);

                } else {
                  // Failed to save new job - create/update draft and minimize
                  self.minimizeAsDraft({
                    jobId: null,
                    meta: getJobMeta(),
                    currentHtml: result.responseHtml || currentHtml
                  });
                }
              });
            }
          }
        });
      },

      init() {
        this.updatePosition();
        this.updateVisibility();
        this.setupDragging();
        this.setupButtons();
        this.setupOutsideClick();
      }
    };

    panel.init();
    return panel;
  }

  window.JobPanel = {
    open: () => {
      executeOperation(() => panelInstance.open());
    },
    close: (skipUnsavedCheck) => {
      executeOperation(() => panelInstance.close(skipUnsavedCheck));
    },
    setTitle: (t) => {
      executeOperation(() => panelInstance.setTitle(t));
    },
    setCurrentJobId: (jobId) => {
      executeOperation(() => panelInstance.setCurrentJobId(jobId));
    },
    updateMinimizeButton: () => {
      executeOperation(() => panelInstance.updateMinimizeButton());
    },
    setDeleteCallback: (callback) => {
      const deleteBtn = document.getElementById('panel-delete-btn');
      if (deleteBtn) {
        deleteBtn.style.display = callback ? 'inline-block' : 'none';
        deleteBtn.onclick = callback;
      }
    },
    hideDelete: () => {
      const deleteBtn = document.getElementById('panel-delete-btn');
      if (deleteBtn) deleteBtn.style.display = 'none';
    },
    load: (url) => {
      const target = document.querySelector('#job-panel .panel-body');
      if (!target) return;
      target.setAttribute('hx-get', url);
      target.setAttribute('hx-target', 'this');
      target.setAttribute('hx-swap', 'innerHTML');
      htmx.ajax('GET', url, {
        target: target,
        swap: 'innerHTML',
        'hx-on::after-settle': 'if(window.JobPanel && window.JobPanel.trackFormChanges) window.JobPanel.trackFormChanges(); if(window.JobPanel && window.JobPanel.updateMinimizeButton) window.JobPanel.updateMinimizeButton()'
      });
      executeOperation(() => panelInstance.open());
    },
    showContent: (html) => {
      const target = document.querySelector('#job-panel .panel-body');
      if (!target) return;

      // Sanitize the HTML to fix any invalid value attributes (e.g., from old cached drafts)
      const sanitizedHtml = sanitizeDraftHtml(html);
      target.innerHTML = sanitizedHtml;

      // Re-run HTMX processing so hx-* attributes work on restored content
      if (typeof htmx !== 'undefined') {
        htmx.process(target);
      }

      executeOperation(() => {
        panelInstance.open();
        panelInstance.trackFormChanges();
      });

      // Run targeted initializers instead of generic htmx:load dispatch
      // This avoids re-init storms and checkbox state fights
      setTimeout(() => {
        // Initialize toggle UI (call reminder, recurrence) - idempotent
        initJobFormToggleUI(target);

        // Initialize date pickers
        initPanelDatePickers();

        // Initialize phone masks if available
        if (window.PhoneMask && window.PhoneMask.init) {
          window.PhoneMask.init();
        }

        // Initialize schedule picker if available
        if (window.initSchedulePicker) {
          window.initSchedulePicker();
        }
      }, 50);
    },
    trackFormChanges: () => {
      executeOperation(() => panelInstance.trackFormChanges());
    },
    clearUnsavedChanges: () => {
      executeOperation(() => panelInstance.clearUnsavedChanges());
    },
    hasUnsavedChanges: () => {
      return panelInstance.hasUnsavedChanges();
    },
    saveForm: (callback) => {
      executeOperation(() => panelInstance.saveForm(callback));
    },
    get currentJobId() {
      return panelInstance.currentJobId;
    },
    set currentJobId(value) {
      panelInstance.currentJobId = value;
    },
    // Track draft ID for new unsaved jobs (used for draft promotion)
    currentDraftId: null
  };

  window.jobPanel = function jobPanel() {
    return {
      isOpen: false,
      title: 'Job',
      x: 80, y: 80, w: 520, h: null,
      docked: false,
      dragging: false, sx: 0, sy: 0,
      currentJobId: null, // Track current job for workspace integration
      get panelStyle() {
        if (this.docked) {
          return `top:80px; right:16px; left:auto; transform:none;`;
        }
        return `top:0; left:0; transform: translate(${this.x}px, ${this.y}px);`;
      },
      open() { this.isOpen = true; this.updateMinimizeButton(); save(this); },
      close(skipUnsavedCheck) {
        // Check for unsaved changes before closing (unless explicitly skipped)
        if (!skipUnsavedCheck && this.hasUnsavedChanges()) {
          if (!confirm('You have unsaved changes. Are you sure you want to close without saving?')) {
            return; // User cancelled, don't close
          }
        }

        this.isOpen = false;
        this.currentJobId = null; // Clear current job ID when closing
        this.updateMinimizeButton(); // Hide minimize button
        save(this);
      },
      setTitle(t) { this.title = t || 'Job'; save(this); },
      setCurrentJobId(jobId) {
        this.currentJobId = normalizeJobId(jobId);
        this.updateMinimizeButton();
      },
      updateMinimizeButton() {
        const minimizeBtn = document.getElementById('panel-workspace-minimize-btn');
        if (!minimizeBtn) return;

        // Always show minimize button when panel is open
        if (this.isOpen) {
          minimizeBtn.style.display = 'inline-flex';
        } else {
          minimizeBtn.style.display = 'none';
        }
      },
      toggleDock() { this.docked = !this.docked; save(this); },
      hasUnsavedChanges() {
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) return false;

        // Check for any form inputs that have been modified
        const inputs = panelBody.querySelectorAll('input, select, textarea');
        for (const input of inputs) {
          // Skip hidden inputs and buttons
          if (input.type === 'hidden' || input.type === 'submit' || input.type === 'button') {
            continue;
          }

          // Skip inputs without a name attribute - they don't submit and are UI-only
          // (e.g., flatpickr alt display inputs, cloned header selects, etc.)
          if (!input.name) {
            continue;
          }

          // Check if the current value differs from the original value
          if (input.hasAttribute('data-original-value')) {
            const originalValue = input.getAttribute('data-original-value');
            const currentValue = input.value;
            if (originalValue !== currentValue) {
              return true;
            }
          } else if (input.value !== '') {
            // If no original value stored but input has a value, it might be a change
            // This is a fallback for inputs that weren't tracked from the start
            return true;
          }
        }

        return false;
      },
      trackFormChanges() {
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) {
          console.log('trackFormChanges: No panel body found');
          return;
        }

        // Store original values for all form inputs
        const inputs = panelBody.querySelectorAll('input, select, textarea');
        console.log('trackFormChanges: Setting tracking on', inputs.length, 'inputs');
        inputs.forEach(input => {
          // Skip inputs without a name attribute - they don't submit and are UI-only
          if (!input.name) {
            return;
          }
          if (input.type !== 'hidden' && input.type !== 'submit' && input.type !== 'button') {
            input.setAttribute('data-original-value', input.value);
          }
        });
      },
      clearUnsavedChanges() {
        // Reset tracking by updating all original values to current values
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) return;

        const inputs = panelBody.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
          // Skip inputs without a name attribute - they don't submit and are UI-only
          if (!input.name) {
            return;
          }
          if (input.type !== 'hidden' && input.type !== 'submit' && input.type !== 'button') {
            input.setAttribute('data-original-value', input.value);
          }
        });
      },
      /**
       * Check which required fields are missing from the form (Alpine version).
       * Required fields: business_name, start_dt, end_dt, calendar
       * @param {HTMLFormElement} form - The form element
       * @returns {string[]} - Array of missing field names (empty if all present)
       */
      getRequiredMissing(form) {
        if (!form) return ['form'];
        const missing = [];

        // Business name - required and must not be whitespace-only
        const businessName = form.querySelector('input[name="business_name"]');
        if (!businessName || !businessName.value.trim()) {
          missing.push('business_name');
        }

        // Start date - required
        const startDt = form.querySelector('input[name="start_dt"]');
        if (!startDt || !startDt.value.trim()) {
          missing.push('start_dt');
        }

        // End date - required
        const endDt = form.querySelector('input[name="end_dt"]');
        if (!endDt || !endDt.value.trim()) {
          missing.push('end_dt');
        }

        // Calendar - required (select element)
        const calendar = form.querySelector('select[name="calendar"]');
        if (!calendar || !calendar.value) {
          missing.push('calendar');
        }

        return missing;
      },
      /**
       * Check if any required fields are missing (Alpine version).
       * @param {HTMLFormElement} form - The form element
       * @returns {boolean} - True if any required fields are missing
       */
      hasRequiredMissing(form) {
        return this.getRequiredMissing(form).length > 0;
      },
      /**
       * Save the form without causing page navigation (Alpine version).
       * Uses HTMX if the form has hx-post, otherwise uses fetch().
       * Handles draft promotion automatically on successful save.
       * @param {Object|Function} optionsOrCallback - Options object or callback function
       * @param {Function} callback - Called with result object: { successful, jobId, responseHtml, status, reason }
       */
      saveForm(optionsOrCallback, callback) {
        // Handle backwards compatibility: saveForm(callback) vs saveForm(options, callback)
        let options = { mode: 'autosave' };
        if (typeof optionsOrCallback === 'function') {
          callback = optionsOrCallback;
        } else if (optionsOrCallback && typeof optionsOrCallback === 'object') {
          options = { ...options, ...optionsOrCallback };
        }

        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) {
          console.warn('Panel body not found');
          if (callback) callback({ successful: false, jobId: null, responseHtml: null, status: null });
          return;
        }

        const form = panelBody.querySelector('form');
        if (!form) {
          console.warn('Form not found in panel');
          if (callback) callback({ successful: false, jobId: null, responseHtml: null, status: null });
          return;
        }

        const self = this;
        const mode = options.mode || 'autosave';

        // Check for missing required fields
        const missingFields = this.getRequiredMissing(form);
        const hasMissing = missingFields.length > 0;

        if (mode === 'manual') {
          // Manual save mode: run HTML5 validation and show messages
          if (hasMissing) {
            // Trigger HTML5 validation display
            if (!form.reportValidity()) {
              if (window.showToast) {
                window.showToast('Please fill in all required fields before saving.', 'warning');
              }
              if (callback) callback({ successful: false, jobId: null, responseHtml: null, status: null, reason: 'missing_required', missingFields });
              return;
            }
          }
        } else {
          // Autosave mode: don't show validation popups, just return unsuccessful
          if (hasMissing) {
            console.log('Alpine saveForm autosave skipped: missing required fields', missingFields);
            if (callback) callback({ successful: false, jobId: null, responseHtml: null, status: null, reason: 'missing_required', missingFields });
            return;
          }
        }

        /**
         * Handle draft promotion after successful save
         */
        const handleDraftPromotion = (jobId) => {
          if (jobId && window.JobPanel.currentDraftId && window.JobWorkspace && window.JobWorkspace.promoteDraft) {
            const draftId = window.JobPanel.currentDraftId;
            window.JobWorkspace.promoteDraft(draftId, jobId, {});
            window.JobPanel.currentDraftId = null;
            console.log('Alpine: Promoted draft', draftId, 'to job', jobId);
          }
        };

        // Check if form has HTMX attributes (hx-post, hx-put, etc.)
        const hasHtmxPost = form.hasAttribute('hx-post') || form.hasAttribute('hx-put') ||
          form.hasAttribute('hx-patch') || form.hasAttribute('hx-delete');

        if (typeof htmx !== 'undefined' && hasHtmxPost) {
          // Use HTMX submission - it won't navigate because the form has hx-* attrs
          const afterRequestHandler = (event) => {
            const xhr = event.detail.xhr;
            const successful = event.detail.successful;
            const status = xhr ? xhr.status : null;
            const responseHtml = xhr ? xhr.responseText : null;
            let jobId = null;

            if (successful) {
              // Clear unsaved changes tracking
              self.clearUnsavedChanges();

              // Capture job ID from HX-Trigger header
              if (xhr) {
                const triggerHeader = xhr.getResponseHeader('HX-Trigger');
                if (triggerHeader) {
                  try {
                    const triggerData = JSON.parse(triggerHeader);
                    if (triggerData.jobSaved && triggerData.jobSaved.jobId) {
                      jobId = normalizeJobId(triggerData.jobSaved.jobId);
                      self.currentJobId = jobId;
                      console.log('Captured job ID from trigger:', jobId);
                    }
                  } catch (e) {
                    console.warn('Could not parse trigger data:', e);
                  }
                }
              }

              // Fallback: try to get from DOM
              if (!jobId) {
                const jobIdInput = form.querySelector('input[name="job_id"]');
                if (jobIdInput && jobIdInput.value) {
                  jobId = normalizeJobId(jobIdInput.value);
                  self.currentJobId = jobId;
                  console.log('Captured job ID from DOM fallback:', jobId);
                }
              }

              // Handle draft promotion
              handleDraftPromotion(jobId);

              // Migrate warning key from temp to job ID
              if (jobId && window.migrateWarningKeyToJobId) {
                window.migrateWarningKeyToJobId(form, jobId);
              }
            } else {
              console.error('Form submission failed with status:', status);
            }

            form.removeEventListener('htmx:afterRequest', afterRequestHandler);
            if (callback) callback({ successful, jobId, responseHtml, status });
          };

          form.addEventListener('htmx:afterRequest', afterRequestHandler);
          htmx.trigger(form, 'submit');

        } else {
          // Use fetch() to avoid navigation - never call form.submit()
          const formData = new FormData(form);
          const actionUrl = form.getAttribute('hx-post') || form.getAttribute('action') || window.location.href;
          const csrfToken = window.getCookie ? window.getCookie('csrftoken') :
            document.querySelector('meta[name="csrf-token"]')?.content ||
            form.querySelector('input[name="csrfmiddlewaretoken"]')?.value;

          fetch(actionUrl, {
            method: 'POST',
            body: formData,
            headers: {
              'X-CSRFToken': csrfToken || '',
              'X-Requested-With': 'XMLHttpRequest'
            }
          })
            .then(response => {
              return response.text().then(html => ({
                successful: response.ok,
                status: response.status,
                responseHtml: html,
                headers: response.headers
              }));
            })
            .then(result => {
              let jobId = null;

              if (result.successful) {
                self.clearUnsavedChanges();

                // Try to parse HX-Trigger from response headers
                const triggerHeader = result.headers.get('HX-Trigger');
                if (triggerHeader) {
                  try {
                    const triggerData = JSON.parse(triggerHeader);
                    if (triggerData.jobSaved && triggerData.jobSaved.jobId) {
                      jobId = normalizeJobId(triggerData.jobSaved.jobId);
                      self.currentJobId = jobId;
                      console.log('Captured job ID from fetch trigger:', jobId);
                    }
                  } catch (e) {
                    console.warn('Could not parse trigger data:', e);
                  }
                }

                // Fallback: try to extract job_id from response HTML
                if (!jobId && result.responseHtml) {
                  const match = result.responseHtml.match(/name="job_id"\s+value="(\d+)"/);
                  if (match) {
                    jobId = normalizeJobId(match[1]);
                    self.currentJobId = jobId;
                    console.log('Captured job ID from response HTML:', jobId);
                  }
                }

                // Handle draft promotion
                handleDraftPromotion(jobId);

                // Migrate warning key from temp to job ID
                if (jobId && window.migrateWarningKeyToJobId) {
                  window.migrateWarningKeyToJobId(form, jobId);
                }
              } else {
                console.error('Form submission failed with status:', result.status);
              }

              if (callback) callback({
                successful: result.successful,
                jobId,
                responseHtml: result.responseHtml,
                status: result.status
              });
            })
            .catch(error => {
              console.error('Fetch error:', error);
              if (callback) callback({ successful: false, jobId: null, responseHtml: null, status: null });
            });
        }
      },
      startDrag(e) {
        if (this.docked) return;
        const p = e.touches?.[0] ?? e;
        this.dragging = true;
        this.sx = p.clientX - this.x;
        this.sy = p.clientY - this.y;
        window.addEventListener('mousemove', this._move);
        window.addEventListener('mouseup', this._stop);
        window.addEventListener('touchmove', this._move, { passive: false });
        window.addEventListener('touchend', this._stop);
      },
      _move: null,
      _stop: null,
      init() {
        const self = this;
        panelInstance = this; // Store reference for global API
        const st = load() || {};
        Object.assign(this, st);
        this._move = function (ev) {
          if (!self.dragging) return;
          const p = ev.touches?.[0] ?? ev;
          const maxX = window.innerWidth - 200; // keep header on-screen
          const maxY = window.innerHeight - 48;
          self.x = clamp(p.clientX - self.sx, 8, maxX);
          self.y = clamp(p.clientY - self.sy, 8, maxY);
          ev.preventDefault();
        };
        this._stop = function () {
          self.dragging = false;
          window.removeEventListener('mousemove', self._move);
          window.removeEventListener('mouseup', self._stop);
          window.removeEventListener('touchmove', self._move);
          window.removeEventListener('touchend', self._stop);
          save(self);
        };
        // Execute any queued operations now that panel is ready
        flushQueue();
      }
    };
  };

  // ==========================================================================
  // DATE VALIDATION GUARDRAILS
  // Values come from server (constants.py) via window.calendarConfig.guardrails
  // Fallbacks provided in case calendarConfig is not yet loaded
  // ==========================================================================
  function getGuardrails() {
    const serverGuardrails = window.calendarConfig?.guardrails || {};
    return {
      // UX warning thresholds (from server)
      MAX_DAYS_IN_FUTURE: serverGuardrails.warnDaysInFuture || 365,
      MAX_JOB_SPAN_DAYS: serverGuardrails.warnJobSpanDays || 60,
      // Hard validation limits (from server)
      MIN_VALID_YEAR: serverGuardrails.minValidYear || 2000,
      MAX_VALID_YEAR: serverGuardrails.maxValidYear || 2100,
    };
  }
  // Convenience alias for immediate use (re-evaluated each call for late-loading config)
  const DATE_GUARDRAILS = getGuardrails();

  /**
   * Get or create a stable key for tracking one-time warnings per job.
   * Returns "job:<id>" for existing jobs, or "temp:<random>" for new jobs.
   * The temp key is stored on form.dataset so retries reuse it.
   */
  function getJobWarningKey(form) {
    const jobIdInput = form.querySelector('input[name="job_id"]');
    if (jobIdInput && jobIdInput.value) {
      return `job:${jobIdInput.value}`;
    }
    // New job - use or create a temp key
    if (!form.dataset.tempWarningKey) {
      form.dataset.tempWarningKey = `temp:${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    }
    return form.dataset.tempWarningKey;
  }

  /**
   * Check if the initial save warning has already been shown for this job.
   */
  function hasShownInitialWarning(warningKey) {
    try {
      return localStorage.getItem(`gts-job-initial-save-attempted:${warningKey}`) === 'true';
    } catch (e) {
      // localStorage blocked - treat as already shown to avoid annoyance
      return true;
    }
  }

  /**
   * Mark that the initial save warning has been shown for this job.
   */
  function markInitialWarningShown(warningKey) {
    try {
      localStorage.setItem(`gts-job-initial-save-attempted:${warningKey}`, 'true');
    } catch (e) {
      // localStorage blocked - ignore
    }
  }

  /**
   * Migrate the one-time warning flag from a temp key to a job key.
   * Called after a new job is saved and gets its ID.
   */
  function migrateWarningKeyToJobId(form, jobId) {
    if (!form.dataset.tempWarningKey) return;
    const tempKey = form.dataset.tempWarningKey;
    const jobKey = `job:${jobId}`;
    try {
      const wasShown = localStorage.getItem(`gts-job-initial-save-attempted:${tempKey}`);
      if (wasShown === 'true') {
        localStorage.setItem(`gts-job-initial-save-attempted:${jobKey}`, 'true');
      }
      localStorage.removeItem(`gts-job-initial-save-attempted:${tempKey}`);
    } catch (e) {
      // localStorage blocked - ignore
    }
    // Update the form's key reference
    delete form.dataset.tempWarningKey;
  }

  // Expose migrateWarningKeyToJobId globally so saveForm can call it
  window.migrateWarningKeyToJobId = migrateWarningKeyToJobId;

  /**
   * Validate job date inputs before form submission
   * Returns true if validation passes (or user confirms), false to cancel submission
   * 
   * The warning dialog only appears on the FIRST save attempt per job (per-browser),
   * and only for start dates in the past or more than 3 years in the future.
   */
  function validateJobDates(form) {
    // Get fresh guardrails each call (in case config was loaded late)
    const guardrails = getGuardrails();

    const startInput = form.querySelector('input[name="start_dt"]');
    const endInput = form.querySelector('input[name="end_dt"]');

    if (!startInput || !endInput) return true; // No date inputs found, allow submission

    const startValue = startInput.value;
    const endValue = endInput.value;

    if (!startValue || !endValue) return true; // Empty dates handled by server validation

    // Parse dates using local time parser to avoid timezone issues
    // parseISOLocal handles both YYYY-MM-DD and YYYY-MM-DDTHH:MM formats
    let startDate = parseISOLocal(startValue);
    let endDate = parseISOLocal(endValue);

    // Check for invalid dates
    if (!startDate || !endDate || isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
      return true; // Let server handle invalid dates
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Check for absurd year values (these are hard errors, not warnings)
    const startYear = startDate.getFullYear();
    const endYear = endDate.getFullYear();

    if (startYear < guardrails.MIN_VALID_YEAR || startYear > guardrails.MAX_VALID_YEAR) {
      alert(`Invalid start year: ${startYear}. Please enter a year between ${guardrails.MIN_VALID_YEAR} and ${guardrails.MAX_VALID_YEAR}.`);
      startInput.focus();
      return false;
    }

    if (endYear < guardrails.MIN_VALID_YEAR || endYear > guardrails.MAX_VALID_YEAR) {
      alert(`Invalid end year: ${endYear}. Please enter a year between ${guardrails.MIN_VALID_YEAR} and ${guardrails.MAX_VALID_YEAR}.`);
      endInput.focus();
      return false;
    }

    // Get the warning key for this job
    const warningKey = getJobWarningKey(form);

    // If we've already shown the warning for this job, skip the check
    if (hasShownInitialWarning(warningKey)) {
      return true;
    }

    // Mark as shown BEFORE computing warnings (so it never shows again, even on cancel)
    markInitialWarningShown(warningKey);

    const warnings = [];

    // Calculate date thresholds
    const threeYearsFromToday = new Date(today);
    threeYearsFromToday.setFullYear(today.getFullYear() + 3);

    const daysUntilStart = Math.floor((startDate - today) / (1000 * 60 * 60 * 24));

    // Check for start date in the past
    if (startDate < today) {
      const daysInPast = Math.abs(daysUntilStart);
      warnings.push(`The start date is ${daysInPast} day${daysInPast !== 1 ? 's' : ''} in the past.`);
    }
    // Check for start date more than 3 years in the future
    else if (startDate > threeYearsFromToday) {
      warnings.push(`The start date is ${daysUntilStart} days in the future (more than 3 years).`);
    }

    // Check for very long job span
    const spanDays = Math.floor((endDate - startDate) / (1000 * 60 * 60 * 24));
    if (spanDays > guardrails.MAX_JOB_SPAN_DAYS) {
      warnings.push(`This job spans ${spanDays} days (more than ${guardrails.MAX_JOB_SPAN_DAYS} days).`);
    }

    // If there are warnings, ask for confirmation
    if (warnings.length > 0) {
      const message = warnings.join('\n') + '\n\nAre you sure you want to save this job?';
      if (!confirm(message)) {
        return false;
      }
    }

    return true;
  }

  // Hook into HTMX form submissions to validate dates
  document.addEventListener('htmx:beforeRequest', function (event) {
    const form = event.target.closest('form');
    if (!form) return;

    // Only validate job forms (check for job-related URL)
    const action = form.getAttribute('hx-post') || form.getAttribute('action') || '';
    if (!action.includes('job_create') && !action.includes('job') && !form.querySelector('input[name="start_dt"]')) {
      return;
    }

    // Validate dates
    if (!validateJobDates(form)) {
      event.preventDefault();
      event.stopPropagation();
    }
  });

  function save(vm) {
    const st = { x: vm.x, y: vm.y, w: vm.w, h: vm.h, docked: vm.docked, title: vm.title, isOpen: vm.isOpen };
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(st)); } catch (e) { }
  }
  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null'); } catch (e) { return null; }
  }

  // Initialize panel when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPanel);
  } else {
    // DOM already loaded
    initPanel();
  }

  function initPanel() {
    // Wait a bit for Alpine to potentially load
    setTimeout(() => {
      const hasAlpine = typeof Alpine !== 'undefined' && Alpine !== null && typeof Alpine.start === 'function';
      if (hasAlpine) {
        isAlpineMode = true;
        // Alpine will call init() on the component
        // Wait a bit more for Alpine to initialize the component
        setTimeout(() => {
          if (!panelInstance) {
            panelInstance = createVanillaPanel();
            if (panelInstance) {
              flushQueue();
            }
          }
        }, 500);
      } else {
        isAlpineMode = false;
        panelInstance = createVanillaPanel();
        if (panelInstance) {
          flushQueue();
        }
      }
    }, 100);
  }
})();
