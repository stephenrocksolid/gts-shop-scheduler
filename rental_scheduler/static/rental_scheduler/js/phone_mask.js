/**
 * Phone mask utility - formats phone numbers as xxx-xxx-xxxx or 1-xxx-xxx-xxxx
 * with proper caret position preservation for natural editing.
 */
(function() {
  'use strict';

  /**
   * Format a string of digits into phone format.
   * @param {string} digits - Only digit characters
   * @returns {string} Formatted phone number
   */
  function formatPhone(digits) {
    if (!digits) return '';
    
    // Handle 11+ digits starting with 1 (country code) - truncate to 11
    if (digits.length >= 11 && digits[0] === '1') {
      digits = digits.substring(0, 11);
      return '1-' + digits.substring(1, 4) + '-' + digits.substring(4, 7) + '-' + digits.substring(7, 11);
    }
    
    // Standard 10-digit format or partial
    if (digits.length <= 3) {
      return digits;
    } else if (digits.length <= 6) {
      return digits.substring(0, 3) + '-' + digits.substring(3);
    } else if (digits.length <= 10) {
      return digits.substring(0, 3) + '-' + digits.substring(3, 6) + '-' + digits.substring(6);
    } else {
      // More than 10 digits but doesn't start with 1 - truncate to 10
      digits = digits.substring(0, 10);
      return digits.substring(0, 3) + '-' + digits.substring(3, 6) + '-' + digits.substring(6);
    }
  }

  /**
   * Count digits in a string up to a given position.
   * @param {string} str - The string to scan
   * @param {number} pos - Position to count up to
   * @returns {number} Number of digits before pos
   */
  function countDigitsBefore(str, pos) {
    let count = 0;
    for (let i = 0; i < pos && i < str.length; i++) {
      if (/\d/.test(str[i])) count++;
    }
    return count;
  }

  /**
   * Find the position in formatted string that corresponds to N digits.
   * @param {string} formatted - The formatted string
   * @param {number} digitCount - Number of digits to find position for
   * @returns {number} Character position
   */
  function positionAfterNDigits(formatted, digitCount) {
    let count = 0;
    for (let i = 0; i < formatted.length; i++) {
      if (/\d/.test(formatted[i])) {
        count++;
        if (count === digitCount) {
          return i + 1;
        }
      }
    }
    return formatted.length;
  }

  /**
   * Apply phone mask to an input element.
   * @param {HTMLInputElement} input - The input element to mask
   */
  function applyPhoneMask(input) {
    if (!input || input._phoneMaskApplied) return;
    input._phoneMaskApplied = true;

    input.addEventListener('input', function(e) {
      const oldValue = this.value;
      const oldPos = this.selectionStart;
      
      // Count digits before cursor in the old value
      const digitsBefore = countDigitsBefore(oldValue, oldPos);
      
      // Extract all digits
      let digits = oldValue.replace(/\D/g, '');
      
      // Limit to 11 digits (for 1-xxx-xxx-xxxx) or 10 otherwise
      if (digits.length > 11) {
        digits = digits.substring(0, 11);
      } else if (digits.length > 10 && digits[0] !== '1') {
        digits = digits.substring(0, 10);
      }
      
      // Format
      const formatted = formatPhone(digits);
      
      // Only update if different (avoids infinite loops)
      if (formatted !== oldValue) {
        this.value = formatted;
        
        // Restore cursor position based on digit count
        const newPos = positionAfterNDigits(formatted, digitsBefore);
        this.setSelectionRange(newPos, newPos);
      }
    });

    // Handle keydown for backspace/delete near dashes
    input.addEventListener('keydown', function(e) {
      const pos = this.selectionStart;
      const val = this.value;
      
      // If selection exists, let default behavior handle it
      if (this.selectionStart !== this.selectionEnd) return;
      
      if (e.key === 'Backspace') {
        // If cursor is right after a dash, skip over it
        if (pos > 0 && val[pos - 1] === '-') {
          e.preventDefault();
          // Move cursor back past the dash, then delete the digit before it
          if (pos > 1) {
            const before = val.substring(0, pos - 2);
            const after = val.substring(pos);
            this.value = before + after;
            // Trigger input event to reformat
            this.dispatchEvent(new Event('input', { bubbles: true }));
            // Position cursor
            const newPos = pos - 2;
            this.setSelectionRange(newPos, newPos);
          }
        }
      } else if (e.key === 'Delete') {
        // If cursor is right before a dash, skip over it
        if (pos < val.length && val[pos] === '-') {
          e.preventDefault();
          // Delete the digit after the dash
          if (pos + 1 < val.length) {
            const before = val.substring(0, pos);
            const after = val.substring(pos + 2);
            this.value = before + after;
            // Trigger input event to reformat
            this.dispatchEvent(new Event('input', { bubbles: true }));
            this.setSelectionRange(pos, pos);
          }
        }
      }
    });

    // Format on blur (in case of paste without triggering input)
    input.addEventListener('blur', function() {
      const digits = this.value.replace(/\D/g, '');
      this.value = formatPhone(digits);
    });

    // Format initial value if present
    if (input.value) {
      const digits = input.value.replace(/\D/g, '');
      input.value = formatPhone(digits);
    }
  }

  /**
   * Initialize phone masks on all matching inputs.
   */
  function initPhoneMasks() {
    const phoneInputs = document.querySelectorAll('input[name="phone"]');
    phoneInputs.forEach(applyPhoneMask);
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPhoneMasks);
  } else {
    initPhoneMasks();
  }

  // Re-initialize after HTMX swaps
  document.body.addEventListener('htmx:afterSwap', function() {
    setTimeout(initPhoneMasks, 50);
  });
  
  document.body.addEventListener('htmx:load', function() {
    setTimeout(initPhoneMasks, 50);
  });

  // Expose for manual use if needed
  window.PhoneMask = {
    apply: applyPhoneMask,
    format: formatPhone,
    init: initPhoneMasks
  };
})();

