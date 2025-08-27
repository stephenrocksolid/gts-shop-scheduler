/**
 * ContractForm - Manages contract form interactions, submission, and PDF generation
 * Handles form validation, print functionality, and coordinates with other modules
 */

// Prevent redeclaration errors during browser cache transitions
if (typeof ContractForm === 'undefined') {
    window.ContractForm = class ContractForm {
        constructor(config = {}) {
            // Configuration and dependencies
            this.config = config;
            this.form = null;
            this.categorySelect = null;
            this.trailerSelect = null;
            this.savePrintButton = null;
            this.printButton = null;
            this.additionalDetailsToggle = null;
            this.additionalDetailsSection = null;

            // State management
            this.isSubmitting = false;
            this.retryCount = 0;
            this.maxRetries = 3;

            // Initialize if dependencies are available
            this.initialize();
        }

        /**
         * Initialize the contract form module
         */
        initialize() {
            // Check for required dependencies
            if (!window.RentalConfig) {
                window.Logger?.error('ContractForm: RentalConfig is required but not available');
                return;
            }

            if (!window.Logger) {
                console.warn('ContractForm: Logger not available, falling back to console logging');
            }

            // Initialize DOM elements
            this.initializeElements();

            if (!this.validateElements()) {
                window.Logger?.error('ContractForm: Required form elements not found');
                return;
            }

            // Setup event listeners
            this.setupEventListeners();

            window.Logger?.debug('ContractForm initialized successfully');
        }

        /**
         * Initialize DOM element references using RentalConfig
         */
        initializeElements() {
            this.form = document.getElementById('contract-form');
            this.categorySelect = window.RentalConfig.getField('category');
            this.trailerSelect = window.RentalConfig.getField('trailer');
            this.savePrintButton = document.getElementById('save-print-contract-btn');
            this.printButton = document.getElementById('print-contract-btn');
            this.additionalDetailsToggle = document.getElementById('additional-details-toggle');
            this.additionalDetailsSection = document.getElementById('additional-details');
        }

        /**
         * Validate that required elements exist
         * @returns {boolean} True if all required elements are present
         */
        validateElements() {
            const required = {
                form: this.form,
                categorySelect: this.categorySelect,
                trailerSelect: this.trailerSelect
            };

            const missing = Object.entries(required)
                .filter(([name, element]) => !element)
                .map(([name]) => name);

            if (missing.length > 0) {
                window.Logger?.error('ContractForm: Missing required elements', { missing });
                return false;
            }

            return true;
        }

        /**
         * Setup all event listeners
         */
        setupEventListeners() {
            // Category change handler
            if (this.categorySelect) {
                this.categorySelect.addEventListener('change', () => {
                    this.handleCategoryChange();
                });
            }

            // Save & Print button handler
            if (this.savePrintButton) {
                this.savePrintButton.addEventListener('click', (e) => {
                    this.handleSavePrintClick(e);
                });
            }

            // Update & Print button handler (for existing contracts)
            if (this.printButton) {
                this.printButton.addEventListener('click', (e) => {
                    this.handlePrintClick(e);
                });
            }

            // Initialize additional details section state
            this.initializeAdditionalDetailsState();

            if (this.additionalDetailsToggle && this.additionalDetailsSection) {
                this.additionalDetailsToggle.addEventListener('click', () => {
                    this.toggleAdditionalDetails();
                });
            }

            window.Logger?.debug('ContractForm: Event listeners setup complete');
        }

        /**
         * Initialize the additional details section state based on existing values
         */
        initializeAdditionalDetailsState() {
            if (!this.additionalDetailsToggle || !this.additionalDetailsSection) {
                return;
            }

            // Check if any additional details fields have values
            const hasAdditionalDetails = this.checkForAdditionalDetailsValues();

            if (hasAdditionalDetails) {
                // Show the additional details section
                this.additionalDetailsSection.classList.add('open');
                this.updateToggleButton(true);
                window.Logger?.debug('ContractForm: Additional details section auto-expanded due to existing values');
            }
        }

        /**
         * Check if any additional details fields have values
         * @returns {boolean} True if any additional detail field has a value
         */
        checkForAdditionalDetailsValues() {
            // Try to get values from the customer info context
            try {
                const contextElement = document.getElementById('customer-info-context');
                if (contextElement) {
                    const context = JSON.parse(contextElement.textContent);
                    if (context.additionalDetailsValues) {
                        const values = context.additionalDetailsValues;
                        return Object.values(values).some(value => value && value.trim() !== '');
                    }
                }
            } catch (error) {
                window.Logger?.debug('ContractForm: Could not parse customer info context', error);
            }

            // Fallback: check field values directly
            const additionalFields = [
                'customer_street_address',
                'customer_city',
                'customer_state',
                'customer_zip_code',
                'customer_po_number'
            ];

            return additionalFields.some(fieldName => {
                const field = this.form?.querySelector(`[name="${fieldName}"]`);
                return field && field.value && field.value.trim() !== '';
            });
        }

        /**
         * Toggle the additional details section
         */
        toggleAdditionalDetails() {
            if (!this.additionalDetailsToggle || !this.additionalDetailsSection) {
                return;
            }

            const isOpen = this.additionalDetailsSection.classList.toggle('open');
            this.updateToggleButton(isOpen);
        }

        /**
         * Update the toggle button appearance based on state
         * @param {boolean} isOpen - Whether the section is open
         */
        updateToggleButton(isOpen) {
            if (!this.additionalDetailsToggle) return;

            if (isOpen) {
                this.additionalDetailsToggle.innerHTML = `
                    <svg class="w-4 h-4 transform rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                    Hide Additional Details
                `;
            } else {
                this.additionalDetailsToggle.innerHTML = `
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                    Show Additional Details
                `;
            }
        }

        /**
         * Handle category selection change
         */
        async handleCategoryChange() {
            const categoryId = this.categorySelect?.value;

            if (!categoryId) {
                this.clearTrailerOptions();
                return;
            }

            const startInput = document.getElementById('id_start_datetime');
            const endInput = document.getElementById('id_end_datetime');
            if (!startInput?.value || !endInput?.value) {
                this.clearTrailerOptions();
                if (this.trailerSelect) {
                    this.trailerSelect.disabled = true;
                    this.trailerSelect.innerHTML = '<option value="">Select dates first</option>';
                }
                return;
            }

            window.Logger?.debug('ContractForm: Category changed', { categoryId });

            try {
                // Show loading state
                window.Logger?.showLoading(this.trailerSelect, 'Loading trailers...');

                const response = await fetch(
                    `${window.RentalConfig.getApiUrl('getAvailableTrailers')}?category=${categoryId}`,
                    {
                        headers: window.RentalConfig.getApiHeaders()
                    }
                );

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                this.updateTrailerOptions(data.trailers);

                window.Logger?.debug('ContractForm: Trailers loaded successfully', {
                    count: data.trailers.length
                });

            } catch (error) {
                window.Logger?.error('ContractForm: Failed to load trailers', error);
                window.Logger?.showUserError(
                    this.trailerSelect,
                    window.RentalConfig.ui?.messages?.errorLoadingTrailers || 'Unable to load trailers'
                );
            } finally {
                window.Logger?.hideLoading(this.trailerSelect);
            }
        }

        /**
         * Clear trailer dropdown options
         */
        clearTrailerOptions() {
            if (this.trailerSelect) {
                this.trailerSelect.innerHTML = '<option value="">---------</option>';
            }
        }

        /**
         * Update trailer dropdown with new options
         * @param {Array} trailers - Array of trailer objects
         */
        updateTrailerOptions(trailers) {
            if (!this.trailerSelect) return;

            // Clear existing options
            this.clearTrailerOptions();

            // Add new options
            trailers.forEach(trailer => {
                const option = document.createElement('option');
                option.value = trailer.id;

                // Build display text: Number - Model - Hauling capacity (if exists and > 0)
                let displayText = `${trailer.number} - ${trailer.model}`;
                if (trailer.hauling_capacity && trailer.hauling_capacity > 0) {
                    displayText += ` - ${trailer.hauling_capacity.toLocaleString()} lbs`;
                }

                option.textContent = displayText;
                this.trailerSelect.appendChild(option);
            });

            window.Logger?.debug('ContractForm: Trailer options updated', { count: trailers.length });
        }

        /**
         * Handle save and print button click
         * @param {Event} e - Click event
         */
        handleSavePrintClick(e) {
            e.preventDefault();
            if (!this.form || !this.savePrintButton) return;

            window.Logger?.debug('ContractForm: Save & Print initiated');
            this.handlePrintSubmission(this.form, this.savePrintButton);
        }

        /**
         * Handle print button click (for existing contracts)
         * @param {Event} e - Click event
         */
        handlePrintClick(e) {
            e.preventDefault();
            if (!this.form || !this.printButton) return;

            window.Logger?.debug('ContractForm: Update & Print initiated');
            this.handlePrintSubmission(this.form, this.printButton);
        }

        /**
         * Handle form submission with print functionality
         * @param {HTMLFormElement} form - The form element
         * @param {HTMLButtonElement} button - The submit button
         */
        async handlePrintSubmission(form, button) {
            // Prevent multiple submissions
            if (this.isSubmitting || button.disabled) {
                window.Logger?.warn('ContractForm: Submission already in progress');
                return;
            }

            window.Logger?.debug('ContractForm: Starting print submission process');

            // Clear any existing error messages
            this.clearErrorMessages();

            // Validate form before submission
            if (!this.validateForm()) {
                return;
            }

            // Set submitting state AFTER successful validation
            this.isSubmitting = true;
            this.setButtonLoadingState(button, true);

            try {
                // Prepare form data
                const formData = new FormData(form);
                formData.append('print_contract', 'true');

                window.Logger?.debug('ContractForm: Submitting form', {
                    action: form.action,
                    hasFormData: formData.has('print_contract')
                });

                // Submit form
                const response = await this.submitFormWithRetry(form.action, formData);

                if (response.status === 'success' && response.contract_id) {
                    await this.handleSuccessfulSubmission(response.contract_id);
                } else {
                    throw new Error('Invalid response from server');
                }

            } catch (error) {
                this.handleSubmissionError(error);
            } finally {
                // Reset state
                this.isSubmitting = false;
                this.setButtonLoadingState(button, false);
                this.retryCount = 0;
            }
        }

        /**
         * Submit form with retry logic
         * @param {string} url - Submit URL
         * @param {FormData} formData - Form data
         * @returns {Promise<Object>} Response data
         */
        async submitFormWithRetry(url, formData) {
            const maxRetries = window.RentalConfig.timing?.maxRetries || this.maxRetries;

            for (let attempt = 1; attempt <= maxRetries; attempt++) {
                try {
                    window.Logger?.debug(`ContractForm: Submission attempt ${attempt}/${maxRetries}`);

                    const response = await fetch(url, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });

                    if (!response.ok) {
                        const errorData = await response.json().catch(() => ({}));
                        throw new Error(JSON.stringify(errorData.errors || errorData));
                    }

                    const data = await response.json();
                    window.Logger?.debug('ContractForm: Submission successful', data);
                    return data;

                } catch (error) {
                    window.Logger?.warn(`ContractForm: Submission attempt ${attempt} failed`, error);

                    if (attempt === maxRetries) {
                        throw error;
                    }

                    // Wait before retry with exponential backoff
                    const delay = Math.pow(2, attempt - 1) * 1000;
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }

        /**
 * Handle successful form submission
 * @param {number} contractId - The created/updated contract ID
 */
        async handleSuccessfulSubmission(contractId) {
            window.Logger?.info('ContractForm: Form submitted successfully', { contractId });

            try {
                // Generate PDF URL using the proper endpoint
                const pdfUrl = window.RentalConfig.getApiUrl('contractPdf', { id: contractId });

                window.Logger?.debug('ContractForm: Opening PDF', { pdfUrl });

                // Open PDF in new tab
                window.open(pdfUrl, '_blank');

                // Get the 'next' parameter from the form to determine where to redirect
                const nextInput = this.form?.querySelector('input[name="next"]');
                const nextUrl = nextInput?.value;

                // Determine redirect URL - use 'next' parameter if available, otherwise default to contract list
                const redirectUrl = nextUrl || '/contracts/';

                window.Logger?.debug('ContractForm: Redirecting after success', {
                    nextUrl,
                    redirectUrl
                });

                window.location.href = redirectUrl;

            } catch (error) {
                window.Logger?.error('ContractForm: Failed to open PDF', error);
                // Still show success message even if PDF fails
                this.showSuccessMessage('Contract saved successfully, but PDF generation failed');
            }
        }

        /**
         * Handle submission errors
         * @param {Error} error - The error that occurred
         */
        handleSubmissionError(error) {
            window.Logger?.error('ContractForm: Form submission failed', error);

            let errorMessage = window.RentalConfig.ui?.messages?.errorCalculating ||
                'Failed to generate PDF. Please try again or contact support if the issue persists.';

            try {
                // Try to parse validation errors
                const errorData = JSON.parse(error.message);
                if (errorData && typeof errorData === 'object') {
                    errorMessage = this.formatValidationErrors(errorData);
                }
            } catch (parseError) {
                // Use generic message if parsing fails
                window.Logger?.debug('ContractForm: Could not parse error details', parseError);
            }

            this.showErrorMessage(errorMessage);
        }

        /**
         * Format validation errors for display
         * @param {Object} errors - Validation error object
         * @returns {string} Formatted error message HTML
         */
        formatValidationErrors(errors) {
            let message = 'Validation errors:<br>';

            for (const field in errors) {
                if (Array.isArray(errors[field])) {
                    errors[field].forEach(msg => {
                        message += `• ${field}: ${msg}<br>`;
                    });
                } else {
                    message += `• ${field}: ${errors[field]}<br>`;
                }
            }

            return message;
        }

        /**
         * Validate form before submission
         * @returns {boolean} True if form is valid
         */
        validateForm() {
            // Use native browser validation first
            if (!this.form.checkValidity()) {
                this.form.reportValidity();
                return false;
            }

            // Basic validation - can be expanded
            if (!this.form) return false;

            const requiredFields = ['customer_name', 'start_datetime', 'end_datetime', 'category', 'trailer'];
            const missingFields = [];
            let firstMissingField = null;

            requiredFields.forEach(fieldName => {
                const field = this.form.querySelector(`[name="${fieldName}"]`);
                if (!field || !field.value.trim()) {
                    missingFields.push(fieldName);
                    if (!firstMissingField) firstMissingField = field;
                    window.Logger?.debug(`ContractForm: Missing field ${fieldName}`, {
                        fieldExists: !!field,
                        fieldValue: field ? field.value : 'N/A'
                    });
                }
            });

            if (missingFields.length > 0) {
                window.Logger?.warn('ContractForm: Required fields missing', { missingFields });
                this.showErrorMessage(`Please fill in required fields: ${missingFields.join(', ')}`);
                if (firstMissingField && typeof firstMissingField.scrollIntoView === 'function') {
                    firstMissingField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    if (typeof firstMissingField.focus === 'function') firstMissingField.focus();
                }
                return false;
            }

            return true;
        }

        /**
         * Set button loading state
         * @param {HTMLButtonElement} button - Button element
         * @param {boolean} isLoading - Whether button should show loading state
         */
        setButtonLoadingState(button, isLoading) {
            if (!button) return;

            if (isLoading) {
                button.disabled = true;
                button.classList.add('opacity-50', 'cursor-not-allowed');
                window.Logger?.showLoading(button, 'Processing...');
            } else {
                button.disabled = false;
                button.classList.remove('opacity-50', 'cursor-not-allowed');
                window.Logger?.hideLoading(button);
            }
        }

        /**
         * Clear existing error messages
         */
        clearErrorMessages() {
            const existingErrors = document.querySelectorAll('.rounded-md.bg-red-50.p-4.mb-6');
            existingErrors.forEach(error => error.remove());
        }

        /**
         * Show error message to user
         * @param {string} message - Error message to display
         */
        showErrorMessage(message) {
            this.clearErrorMessages();

            const errorDiv = document.createElement('div');
            errorDiv.className = 'rounded-md bg-red-50 p-4 mb-6';
            errorDiv.innerHTML = `
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <h3 class="text-sm font-medium text-red-800">Form submission failed</h3>
                        <div class="mt-2 text-sm text-red-700">${message}</div>
                    </div>
                </div>
            `;

            // Insert at the top of the form container
            if (this.form && this.form.parentNode) {
                this.form.parentNode.insertBefore(errorDiv, this.form);
                errorDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }

        /**
         * Show success message to user
         * @param {string} message - Success message to display
         */
        showSuccessMessage(message) {
            const successDiv = document.createElement('div');
            successDiv.className = 'rounded-md bg-green-50 p-4 mb-6';
            successDiv.innerHTML = `
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <div class="text-sm text-green-700">${message}</div>
                    </div>
                </div>
            `;

            if (this.form && this.form.parentNode) {
                this.form.parentNode.insertBefore(successDiv, this.form);
            }
        }

        /**
         * Cleanup method for removing event listeners and resetting state
         */
        destroy() {
            // Remove event listeners if needed
            this.isSubmitting = false;
            this.retryCount = 0;
            window.Logger?.debug('ContractForm: Destroyed');
        }
    }

    // Auto-initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function () {
        // Wait for dependencies to be available
        if (window.RentalConfig) {
            window.contractForm = new ContractForm();
        } else {
            // Wait a bit for dependencies to load
            setTimeout(() => {
                if (window.RentalConfig) {
                    window.contractForm = new ContractForm();
                } else {
                    console.error('ContractForm: RentalConfig dependency not available');
                }
            }, 100);
        }
    });

} else {
    window.Logger?.debug('ContractForm already exists, skipping initialization');
} 