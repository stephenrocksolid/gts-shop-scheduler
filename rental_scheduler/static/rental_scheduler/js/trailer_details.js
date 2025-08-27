/**
 * TrailerDetails - Manages trailer selection, scheduling, and rental calculations
 * Handles form interactions, API calls, and real-time calculations
 */

// Wrap in IIFE to avoid global conflicts
(function () {
    'use strict';

    // Defensive loading - only declare TrailerDetails if it doesn't already exist
    if (typeof window.TrailerDetails === 'undefined') {
        window.TrailerDetails = class TrailerDetails {
            constructor(config) {
                // Check for required dependencies
                if (!window.RentalConfig) {
                    window.Logger?.error('TrailerDetails: RentalConfig is required but not available');
                    return;
                }

                this.fieldIds = config.fieldIds || window.RentalConfig.fieldIds;
                this.currentContractId = config.currentContractId;
                this.taxRate = config.taxRate || this.getTaxRateFromElement() || 0;

                this.inFullCalculation = false;
                this.trailerRates = {};

                this.debounceTimers = {
                    calculation: null,
                    trailerUpdate: null
                };
                this.debounceDelay = 100;

                // Initialize DOM elements
                this.initializeElements();

                // Validate required elements
                if (!this.validateElements()) {
                    return;
                }

                // Get add-on prices
                this.furnitureBlanketPrice = this.getFurnitureBlanketPrice();
                this.strapChainPrice = this.getStrapChainPrice();

                // Initialize component
                this.initializeComponent();

                window.Logger?.debug('TrailerDetails initialized successfully', {
                    currentContractId: this.currentContractId,
                    taxRate: this.taxRate,
                    hasFieldIds: !!this.fieldIds
                });
            }

            /**
             * Initialize all DOM element references
             */
            initializeElements() {
                this.categorySelect = document.getElementById(this.fieldIds.category);
                this.trailerSelect = document.getElementById(this.fieldIds.trailer);
                this.startDateTimeInput = document.getElementById(this.fieldIds.startDateTime);
                this.endDateTimeInput = document.getElementById(this.fieldIds.endDateTime);
                this.durationDisplay = window.RentalConfig?.getDisplay('durationDisplay') ||
                    document.getElementById('duration_display');
                this.rateDisplay = window.RentalConfig?.getDisplay('rateDisplay') ||
                    document.getElementById('rate_display');
                this.subtotalDisplay = window.RentalConfig?.getDisplay('subtotalDisplay') ||
                    document.getElementById('subtotal_display');
                this.taxDisplay = window.RentalConfig?.getDisplay('taxDisplay') ||
                    document.getElementById('tax_display');
                this.customRateInput = document.getElementById(this.fieldIds.customRate);
                this.extraMileageInput = document.getElementById(this.fieldIds.extraMileage);
                this.includesWinchCheckbox = document.getElementById(this.fieldIds.includesWinch);
                this.includesHitchBarCheckbox = document.getElementById(this.fieldIds.includesHitchBar);
                this.hasEveningPickupCheckbox = document.getElementById(this.fieldIds.hasEveningPickup);
                this.furnitureBlanketCountInput = document.getElementById(this.fieldIds.furnitureBlanketCount);
                this.strapChainCountInput = document.getElementById(this.fieldIds.strapChainCount);
                this.downPaymentInput = document.getElementById(this.fieldIds.downPayment);
                this.balanceDueDisplay = window.RentalConfig?.getDisplay('balanceDueDisplay') ||
                    document.getElementById('balance_due_display');
                this.trailerTooltip = document.getElementById('trailer-tooltip');
            }

            /**
             * Validate that all required elements are present
             * @returns {boolean} True if all elements found
             */
            validateElements() {
                const requiredElements = [
                    'categorySelect', 'trailerSelect', 'startDateTimeInput', 'endDateTimeInput',
                    'durationDisplay', 'rateDisplay', 'subtotalDisplay', 'taxDisplay',
                    'customRateInput', 'extraMileageInput', 'includesWinchCheckbox',
                    'includesHitchBarCheckbox', 'hasEveningPickupCheckbox',
                    'furnitureBlanketCountInput', 'strapChainCountInput',
                    'downPaymentInput', 'balanceDueDisplay'
                ];

                const missingElements = requiredElements.filter(elementName => !this[elementName]);

                if (missingElements.length > 0) {
                    window.Logger?.error('TrailerDetails: Missing required elements:', missingElements);
                    return false;
                }

                return true;
            }

            /**
             * Get tax rate from hidden input element
             */
            getTaxRateFromElement() {
                const taxRateElement = document.getElementById('tax_rate');
                return taxRateElement?.dataset.taxRate ? parseFloat(taxRateElement.dataset.taxRate) : 0;
            }

            /**
             * Get furniture blanket price from help text
             */
            getFurnitureBlanketPrice() {
                if (!this.furnitureBlanketCountInput) return 0;

                const helpTextElement = this.furnitureBlanketCountInput
                    .closest('div').parentElement.querySelector('p.text-gray-500');

                if (!helpTextElement) return 0;

                const priceMatch = helpTextElement.textContent.match(/\$(\d+\.?\d*)/);
                return priceMatch ? parseFloat(priceMatch[1]) : 0;
            }

            /**
             * Get strap/chain price from help text
             */
            getStrapChainPrice() {
                if (!this.strapChainCountInput) return 0;

                const helpTextElement = this.strapChainCountInput
                    .closest('div').parentElement.querySelector('p.text-gray-500');

                if (!helpTextElement) return 0;

                const priceMatch = helpTextElement.textContent.match(/\$(\d+\.?\d*)/);
                return priceMatch ? parseFloat(priceMatch[1]) : 0;
            }

            /**
             * Initialize the component after elements are validated
             */
            initializeComponent() {
                this.initializeTrailerSelect();
                this.bindEventListeners();
                this.initializeTooltip();

                // Handle initial values (edit mode)
                if (this.hasInitialValues()) {
                    this.handleInitialValues();
                }
            }

            /**
             * Check if form has initial values (edit mode)
             */
            hasInitialValues() {
                return this.categorySelect.value &&
                    this.startDateTimeInput.value &&
                    this.endDateTimeInput.value;
            }

            /**
             * Handle initial form values in edit mode
             */
            async handleInitialValues() {
                this.updateDuration();
                await this.updateAvailableTrailers();

                if (this.trailerSelect.value) {
                    await this.calculateRate();
                }
            }

            /**
             * Initialize trailer select dropdown state
             */
            initializeTrailerSelect() {
                const hasSelectedTrailer = this.trailerSelect.value !== '';
                const hasRequiredFields = this.categorySelect.value !== '' &&
                    this.startDateTimeInput.value !== '' &&
                    this.endDateTimeInput.value !== '';

                if (hasSelectedTrailer && hasRequiredFields) {
                    this.trailerSelect.disabled = false;
                    this.hideTooltip();
                } else {
                    this.trailerSelect.disabled = true;
                    this.trailerSelect.innerHTML = '<option value="">Select dates and category first</option>';
                    // Update tooltip text based on what's missing
                    this.updateTooltipText();
                }
            }

            /**
             * Initialize trailer tooltip functionality
             */
            initializeTooltip() {
                if (!this.trailerTooltip) {
                    return;
                }

                // Show tooltip when hovering over disabled trailer select
                this.trailerSelect.addEventListener('mouseenter', () => {
                    if (this.trailerSelect.disabled) {
                        this.showTooltip();
                    }
                });

                // Hide tooltip when leaving trailer select
                this.trailerSelect.addEventListener('mouseleave', () => {
                    this.hideTooltip();
                });

                // Also show tooltip when trying to click on disabled select
                this.trailerSelect.addEventListener('click', (e) => {
                    if (this.trailerSelect.disabled) {
                        e.preventDefault();
                        this.showTooltip();
                        // Hide after 2 seconds
                        setTimeout(() => {
                            this.hideTooltip();
                        }, 2000);
                    }
                });
            }

            /**
             * Show the trailer tooltip
             */
            showTooltip() {
                if (this.trailerTooltip) {
                    this.trailerTooltip.classList.remove('opacity-0', 'invisible');
                    this.trailerTooltip.classList.add('opacity-100', 'visible');
                }
            }

            /**
             * Hide the trailer tooltip
             */
            hideTooltip() {
                if (this.trailerTooltip) {
                    this.trailerTooltip.classList.remove('opacity-100', 'visible');
                    this.trailerTooltip.classList.add('opacity-0', 'invisible');
                }
            }

            /**
             * Update tooltip text based on current form state
             */
            updateTooltipText() {
                if (!this.trailerTooltip) return;

                const hasCategory = this.categorySelect.value !== '';
                const hasStartDate = this.startDateTimeInput.value !== '';
                const hasEndDate = this.endDateTimeInput.value !== '';

                let message = 'Select ';
                const missing = [];

                if (!hasStartDate || !hasEndDate) {
                    missing.push('dates');
                }
                if (!hasCategory) {
                    missing.push('category');
                }

                if (missing.length === 0) {
                    message = 'Loading available trailers...';
                } else if (missing.length === 1) {
                    message += missing[0] + ' first';
                } else {
                    message += missing.join(' and ') + ' first';
                }

                this.trailerTooltip.textContent = message;
            }

            /**
             * Bind all event listeners
             */
            bindEventListeners() {

                this.categorySelect.addEventListener('change', () => {
                    this.debouncedTrailerUpdate();
                });

                this.startDateTimeInput.addEventListener('change', () => {
                    this.handleStartDateChange();
                    this.debouncedTrailerUpdate();
                });

                this.endDateTimeInput.addEventListener('change', () => {
                    this.debouncedTrailerUpdate();
                });

                this.trailerSelect.addEventListener('change', () => {
                    this.debouncedCalculateRate();
                });

                this.customRateInput.addEventListener('input', () => {
                    this.debouncedCalculateRate();
                });


                [
                    this.extraMileageInput,
                    this.includesWinchCheckbox,
                    this.includesHitchBarCheckbox,
                    this.hasEveningPickupCheckbox,
                    this.furnitureBlanketCountInput,
                    this.strapChainCountInput,
                    this.downPaymentInput
                ].forEach(element => {
                    if (element) {
                        const eventType = element.type === 'checkbox' ? 'change' : 'input';
                        element.addEventListener(eventType, () => {
                            this.debouncedCalculateSubtotalAndTax();
                        });
                    }
                });
            }

            debouncedTrailerUpdate() {
                if (this.debounceTimers.trailerUpdate) {
                    clearTimeout(this.debounceTimers.trailerUpdate);
                }

                this.debounceTimers.trailerUpdate = setTimeout(async () => {
                    await this.updateAvailableTrailers();
                    await this.updateDuration();
                    await this.calculateRate();
                }, this.debounceDelay);
            }

            debouncedCalculateRate() {
                if (this.debounceTimers.calculation) {
                    clearTimeout(this.debounceTimers.calculation);
                }

                this.debounceTimers.calculation = setTimeout(async () => {
                    await this.calculateRate();
                }, this.debounceDelay);
            }

            debouncedCalculateSubtotalAndTax() {
                if (this.debounceTimers.calculation) {
                    clearTimeout(this.debounceTimers.calculation);
                }

                this.debounceTimers.calculation = setTimeout(async () => {
                    await this.calculateSubtotalAndTax();
                }, this.debounceDelay);
            }

            /**
             * Handle start date change validation
             */
            handleStartDateChange() {
                const startDate = new Date(this.startDateTimeInput.value);
                const endDate = new Date(this.endDateTimeInput.value);

                if (this.endDateTimeInput.value && startDate > endDate) {
                    this.endDateTimeInput.value = '';
                }
            }

            /**
             * Gather form data for API calls
             */
            gatherFormData() {
                return {
                    trailer_id: this.trailerSelect.value || null,
                    start_datetime: this.startDateTimeInput.value || null,
                    end_datetime: this.endDateTimeInput.value || null,
                    custom_rate: this.customRateInput?.value || null,
                    extra_mileage: this.extraMileageInput?.value || 0,
                    includes_winch: this.includesWinchCheckbox?.checked || false,
                    includes_hitch_bar: this.includesHitchBarCheckbox?.checked || false,
                    furniture_blanket_count: parseInt(this.furnitureBlanketCountInput?.value) || 0,
                    strap_chain_count: parseInt(this.strapChainCountInput?.value) || 0,
                    has_evening_pickup: this.hasEveningPickupCheckbox?.checked || false,
                    down_payment: this.downPaymentInput?.value || 0,
                    current_contract_id: this.currentContractId || null
                };
            }

            /**
             * Format date for server communication
             */
            formatDateForServer(dateString) {
                if (!dateString) return '';

                const date = new Date(dateString);
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                const seconds = String(date.getSeconds()).padStart(2, '0');

                return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
            }

            /**
             * Check if required fields are filled for trailer loading
             */
            checkRequiredFields() {
                const hasCategory = this.categorySelect.value !== '';
                const hasStartDate = this.startDateTimeInput.value !== '';
                const hasEndDate = this.endDateTimeInput.value !== '';
                const isValidDateRange = hasStartDate && hasEndDate &&
                    new Date(this.startDateTimeInput.value) < new Date(this.endDateTimeInput.value);

                return hasCategory && isValidDateRange;
            }

            /**
             * Update available trailers based on category and dates
             */
            async updateAvailableTrailers() {
                if (!this.checkRequiredFields()) {
                    this.trailerSelect.disabled = true;
                    this.trailerSelect.innerHTML = '<option value="">Select dates and category first</option>';
                    this.rateDisplay.value = 'Select trailer and dates to see rate';
                    this.updateTooltipText();
                    return;
                }

                const categoryId = this.categorySelect.value;
                const startDate = this.formatDateForServer(this.startDateTimeInput.value);
                const endDate = this.formatDateForServer(this.endDateTimeInput.value);
                const selectedTrailerId = this.trailerSelect.value;

                let url = `${window.RentalConfig.getApiUrl('getAvailableTrailers')}?category=${categoryId}`;

                if (startDate && endDate) {
                    url += `&start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`;
                }
                if (this.currentContractId) {
                    url += `&current_contract_id=${this.currentContractId}`;
                }

                // Show loading state immediately
                this.trailerSelect.disabled = true;
                this.trailerSelect.innerHTML = '<option value="">Loading trailers...</option>';

                if (this.trailerTooltip) {
                    this.trailerTooltip.textContent = 'Loading available trailers...';
                }

                try {
                    const response = await fetch(url);
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }

                    const data = await response.json();

                    this.populateTrailerOptions(data, selectedTrailerId);

                } catch (error) {
                    window.Logger?.error('Error loading trailers:', error);
                    this.trailerSelect.innerHTML = '<option value="">Unable to load trailers</option>';
                    this.trailerSelect.disabled = true;
                    if (this.trailerTooltip) {
                        this.trailerTooltip.textContent = 'Failed to load trailers. Please try again.';
                    }
                    window.Logger?.showUserError(this.rateDisplay, 'Unable to load rates');
                } finally {
                    // Auto-hide tooltip after 2 seconds if trailers loaded successfully
                    if (!this.trailerSelect.disabled) {
                        setTimeout(() => {
                            this.hideTooltip();
                        }, 2000);
                    }
                }
            }

            /**
             * Populate trailer dropdown options
             */
            populateTrailerOptions(data, selectedTrailerId) {
                this.trailerSelect.innerHTML = '<option value="">---------</option>';

                // Clear trailer rates object to avoid stale data
                this.trailerRates = {};

                let selectedTrailerAvailable = false;

                if (data?.trailers && Array.isArray(data.trailers)) {
                    data.trailers.forEach(trailer => {
                        const option = document.createElement('option');
                        option.value = trailer.id;

                        // Build display text: Number - Model - Hauling capacity (if exists and > 0)
                        let displayText = `${trailer.number} - ${trailer.model}`;
                        if (trailer.hauling_capacity && trailer.hauling_capacity > 0) {
                            displayText += ` - ${trailer.hauling_capacity.toLocaleString()} lbs`;
                        }

                        option.textContent = displayText;

                        // Check if this is the selected trailer
                        if (selectedTrailerId && selectedTrailerId == trailer.id) {
                            option.selected = true;
                            selectedTrailerAvailable = true;
                        }

                        this.trailerSelect.appendChild(option);

                        // Store trailer rates
                        this.trailerRates[trailer.id] = {
                            halfDayRate: trailer.half_day_rate,
                            dailyRate: trailer.daily_rate,
                            weeklyRate: trailer.weekly_rate
                        };
                    });

                    // If the previously selected trailer is no longer available, clear the selection
                    if (selectedTrailerId && !selectedTrailerAvailable) {
                        this.trailerSelect.value = '';
                        this.rateDisplay.value = 'Selected trailer not available for these dates';
                    }

                    // Enable/disable based on availability
                    this.trailerSelect.disabled = data.trailers.length === 0;

                    if (data.trailers.length === 0) {
                        this.trailerSelect.innerHTML = '<option value="">No available trailers for selected dates</option>';
                        this.rateDisplay.value = 'No available trailers';
                        if (this.trailerTooltip) {
                            this.trailerTooltip.textContent = 'No trailers available for these dates';
                        }
                    } else {
                        // Success - re-enable dropdown and hide tooltip after a short delay
                        this.trailerSelect.disabled = false;
                        setTimeout(() => {
                            this.hideTooltip();
                        }, 500);
                    }
                } else {
                    throw new Error('Invalid response format');
                }
            }

            /**
             * Update duration display
             */
            async updateDuration() {
                const startDate = this.startDateTimeInput.value;
                const endDate = this.endDateTimeInput.value;

                if (!startDate || !endDate) {
                    this.durationDisplay.value = 'Select start and end dates to see duration';
                    return;
                }

                try {
                    const response = await window.RentalCalculator.calculateDurationInfo(startDate, endDate);
                    const durationInfo = response?.duration_info ? response.duration_info : response;
                    this.durationDisplay.value = window.RentalCalculator.formatDuration(durationInfo);
                } catch (error) {
                    window.Logger?.error('Error calculating duration:', error);
                    this.handleDurationError(startDate, endDate);
                }
            }

            /**
             * Handle duration calculation error with fallback
             */
            handleDurationError(startDate, endDate) {
                const start = new Date(startDate);
                const end = new Date(endDate);

                if (end < start) {
                    this.durationDisplay.value = 'End date must be after start date';
                } else {
                    this.durationDisplay.value = 'Error calculating duration';
                }
            }

            /**
     * Calculate rental rate
     */
            async calculateRate() {
                // Check for custom rate first
                if (this.customRateInput?.value) {
                    const customRate = parseFloat(this.customRateInput.value);
                    if (!isNaN(customRate)) {
                        this.rateDisplay.value = window.RentalCalculator.formatCurrency(customRate);
                        this.calculateSubtotalAndTax();
                        return;
                    }
                }

                const trailerId = this.trailerSelect.value;
                if (!trailerId || !this.trailerRates[trailerId]) {
                    this.rateDisplay.value = 'Select trailer and dates to see rate';
                    return;
                }

                const startDate = this.startDateTimeInput.value;
                const endDate = this.endDateTimeInput.value;

                if (!startDate || !endDate) {
                    this.rateDisplay.value = 'Select dates to see rate';
                    return;
                }

                window.RentalCalculator.showLoading(this.rateDisplay, 'Calculating...');
                this.inFullCalculation = true;

                try {
                    const quoteData = this.gatherFormData();
                    const result = await window.RentalCalculator.calculateQuote(quoteData);
                    const quote = result?.quote ? result.quote : result;

                    this.updateAllCalculatedFields(quote);

                } catch (error) {
                    window.Logger?.error('Error calculating rate:', error);
                    this.handleCalculationError();
                } finally {
                    window.RentalCalculator.hideLoading(this.rateDisplay, this.rateDisplay.value);
                    this.inFullCalculation = false;
                }
            }

            /**
             * Update all calculated display fields
             */
            updateAllCalculatedFields(quote) {
                const category = quote.duration_info?.rate_category;
                const trailerId = this.trailerSelect.value;
                let unitRate = quote.base_rate;
                if (this.customRateInput?.value) {
                    const val = parseFloat(this.customRateInput.value);
                    if (!isNaN(val)) unitRate = val;
                } else if (this.trailerRates[trailerId]) {
                    const rates = this.trailerRates[trailerId];
                    if (category === 'half_day') {
                        unitRate = rates.halfDayRate;
                    } else if (category === 'daily') {
                        unitRate = rates.dailyRate;
                    } else if (category === 'weekly') {
                        unitRate = rates.weeklyRate;
                    } else if (category === 'extended') {
                        unitRate = parseFloat(rates.weeklyRate) / 6;
                    }
                }
                this.rateDisplay.value = window.RentalCalculator.formatCurrency(unitRate);

                if (quote.duration_info) {
                    this.durationDisplay.value = window.RentalCalculator.formatDuration(quote.duration_info);
                }

                this.subtotalDisplay.value = window.RentalCalculator.formatCurrency(quote.subtotal);
                this.taxDisplay.value = window.RentalCalculator.formatCurrency(quote.tax_amount);
                this.balanceDueDisplay.value = window.RentalCalculator.formatCurrency(quote.balance_due);
            }

            /**
             * Handle calculation error
             */
            handleCalculationError() {
                window.RentalCalculator.showError(this.rateDisplay, 'Error calculating rate');
                this.subtotalDisplay.value = 'Error';
                this.taxDisplay.value = 'Error';
                this.balanceDueDisplay.value = 'Error';
            }

            /**
             * Calculate subtotal and tax only
             */
            async calculateSubtotalAndTax() {
                if (this.inFullCalculation) {
                    return;
                }

                const trailerId = this.trailerSelect.value;
                const startDate = this.startDateTimeInput.value;
                const endDate = this.endDateTimeInput.value;

                if (!trailerId || !startDate || !endDate) {
                    this.clearCalculatedFields();
                    return;
                }

                try {
                    const quoteData = this.gatherFormData();
                    const result = await window.RentalCalculator.calculateQuote(quoteData);
                    const quote = result && result.quote ? result.quote : result;

                    this.subtotalDisplay.value = window.RentalCalculator.formatCurrency(quote.subtotal);
                    this.taxDisplay.value = window.RentalCalculator.formatCurrency(quote.tax_amount);
                    this.balanceDueDisplay.value = window.RentalCalculator.formatCurrency(quote.balance_due);

                } catch (error) {
                    window.Logger?.error('Error calculating subtotal and tax:', error);
                    this.showCalculationError();
                }
            }

            /**
             * Clear calculated fields when data is incomplete
             */
            clearCalculatedFields() {
                this.subtotalDisplay.value = 'Select trailer and dates';
                this.taxDisplay.value = 'Select trailer and dates';
                this.balanceDueDisplay.value = 'Select trailer and dates';
            }

            /**
             * Show error in calculation fields
             */
            showCalculationError() {
                this.subtotalDisplay.value = 'Error calculating';
                this.taxDisplay.value = 'Error calculating';
                this.balanceDueDisplay.value = 'Error calculating';
            }
        }

        /**
         * QuickSchedule - Handles quick schedule button functionality
         */
        class QuickSchedule {
            constructor(fieldIds) {
                this.fieldIds = fieldIds;
                this.fullDayDays = 1;
                this.pendingQuickSchedule = null;

                this.initializeButtons();
            }

            /**
             * Initialize quick schedule buttons
             */
            initializeButtons() {
                this.setupMorningHalfDay();
                this.setupAfternoonHalfDay();
                this.setupFullDay();
                this.setupWeekly();
            }

            /**
             * Setup morning half day button
             */
            setupMorningHalfDay() {
                const button = window.RentalConfig?.getQuickScheduleButton('morningHalfDay') ||
                    document.getElementById('qs_morning_half_day');
                if (!button) return;

                button.addEventListener('click', () => {
                    this.handleQuickSchedule('morningHalfDay', () => this.applyMorningHalfDay());
                });
            }

            /**
             * Setup afternoon half day button
             */
            setupAfternoonHalfDay() {
                const button = window.RentalConfig?.getQuickScheduleButton('afternoonHalfDay') ||
                    document.getElementById('qs_afternoon_half_day');
                if (!button) return;

                button.addEventListener('click', () => {
                    this.handleQuickSchedule('afternoonHalfDay', () => this.applyAfternoonHalfDay());
                });
            }

            /**
         * Setup full day button with cycling functionality
         */
            setupFullDay() {
                const button = window.RentalConfig?.getQuickScheduleButton('fullDay') ||
                    document.getElementById('qs_full_day');
                if (!button) return;

                // Set initial button label (shows what first click will do)
                this.updateFullDayButtonLabel();

                button.addEventListener('click', () => {
                    // Apply current day value
                    const currentDays = this.fullDayDays;

                    // Update label to show what we're about to apply
                    this.updateFullDayButtonLabelForDays(currentDays);

                    this.handleQuickSchedule('fullDay', () => this.applyFullDay(currentDays));

                    // After a short delay, increment for next click
                    const quickScheduleDelay = window.RentalConfig?.timing?.quickScheduleDelay || 100;
                    setTimeout(() => {
                        this.fullDayDays = (this.fullDayDays % 4) + 1;
                    }, quickScheduleDelay);
                });
            }

            /**
             * Setup weekly button
             */
            setupWeekly() {
                const button = window.RentalConfig?.getQuickScheduleButton('weekly') ||
                    document.getElementById('qs_weekly');
                if (!button) return;

                button.addEventListener('click', () => {
                    this.handleQuickSchedule('weekly', () => this.applyFullDay(7));
                });
            }

            /**
             * Handle quick schedule button click
             */
            handleQuickSchedule(scheduleType, applyFunction) {
                const startDateInput = document.getElementById(this.fieldIds.startDateTime);

                if (!startDateInput.value) {
                    this.pendingQuickSchedule = scheduleType;
                    this.showFieldValidationError(
                        this.fieldIds.startDateTime,
                        'Please select a start date first. The schedule will be applied automatically.'
                    );

                    const applyScheduleOnDateSelect = () => {
                        if (startDateInput.value && this.pendingQuickSchedule === scheduleType) {
                            this.pendingQuickSchedule = null;
                            const quickScheduleDelay = window.RentalConfig?.timing?.quickScheduleDelay || 100;
                            setTimeout(applyFunction, quickScheduleDelay);
                            startDateInput.removeEventListener('change', applyScheduleOnDateSelect);
                        }
                    };

                    startDateInput.addEventListener('change', applyScheduleOnDateSelect);
                    return;
                }

                applyFunction();
            }

            /**
             * Apply morning half day schedule
             */
            applyMorningHalfDay() {
                const schedule = this.getDateSchedule('7:00 AM', '12:00 PM');
                this.applySchedule(schedule);
            }

            /**
             * Apply afternoon half day schedule
             */
            applyAfternoonHalfDay() {
                const schedule = this.getDateSchedule('1:00 PM', '6:00 PM');
                this.applySchedule(schedule);
            }

            /**
             * Apply full day schedule for specified number of days
             */
            applyFullDay(days) {
                const startDateInput = document.getElementById(this.fieldIds.startDateTime);
                if (!startDateInput.value) return;

                let startDateObj = this.parseDate(startDateInput.value);
                if (!startDateObj) return;

                startDateObj.setHours(7, 0, 0, 0);
                const endDateObj = new Date(startDateObj);
                endDateObj.setDate(endDateObj.getDate() + (days - 1));
                endDateObj.setHours(17, 0, 0, 0);

                const schedule = {
                    start: this.formatDateString(startDateObj, '7:00 AM'),
                    end: this.formatDateString(endDateObj, '5:00 PM')
                };

                this.applySchedule(schedule);
            }

            /**
             * Get schedule for same day with different times
             */
            getDateSchedule(startTime, endTime) {
                const startDateInput = document.getElementById(this.fieldIds.startDateTime);
                if (!startDateInput.value) return null;

                const datePart = startDateInput.value.split(' ')[0];

                return {
                    start: `${datePart} ${startTime}`,
                    end: `${datePart} ${endTime}`
                };
            }

            /**
             * Parse date from input value
             */
            parseDate(value) {
                if (!value) return null;

                let startDateObj;
                const startDateInput = document.getElementById(this.fieldIds.startDateTime);

                if (startDateInput._flatpickr?.selectedDates.length) {
                    startDateObj = new Date(startDateInput._flatpickr.selectedDates[0]);
                } else {
                    startDateObj = new Date(value);
                    if (isNaN(startDateObj)) {
                        const datePart = value.split(' ')[0];
                        const parts = datePart.split('/');
                        if (parts.length === 3) {
                            startDateObj = new Date(`${parts[2]}-${parts[0].padStart(2, '0')}-${parts[1].padStart(2, '0')}`);
                        }
                    }
                }

                return isNaN(startDateObj) ? null : startDateObj;
            }

            /**
             * Format date object to date string
             */
            formatDateString(dateObj, time) {
                const pad = n => String(n).padStart(2, '0');
                const dateStr = `${pad(dateObj.getMonth() + 1)}/${pad(dateObj.getDate())}/${dateObj.getFullYear()}`;
                return `${dateStr} ${time}`;
            }

            /**
             * Apply schedule to form inputs
             */
            applySchedule(schedule) {
                if (!schedule) return;

                const startDateInput = document.getElementById(this.fieldIds.startDateTime);
                const endDateInput = document.getElementById(this.fieldIds.endDateTime);
                const categorySelect = document.getElementById(this.fieldIds.category);

                // Set dates using flatpickr if available, otherwise direct value
                if (startDateInput._flatpickr) {
                    startDateInput._flatpickr.setDate(schedule.start);
                    startDateInput._flatpickr.close();
                } else {
                    startDateInput.value = schedule.start;
                }

                if (endDateInput._flatpickr) {
                    endDateInput._flatpickr.setDate(schedule.end);
                    endDateInput._flatpickr.close();
                } else {
                    endDateInput.value = schedule.end;
                }

                // Trigger change events
                startDateInput.dispatchEvent(new Event('change', { bubbles: true }));
                endDateInput.dispatchEvent(new Event('change', { bubbles: true }));

                // Focus category field after short delay
                const focusDelay = window.RentalConfig?.timing?.focusDelay || 200;
                setTimeout(() => {
                    if (categorySelect) {
                        categorySelect.focus();
                        categorySelect.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }, focusDelay);
            }

            /**
         * Update full day button label
         */
            updateFullDayButtonLabel() {
                this.updateFullDayButtonLabelForDays(this.fullDayDays);
            }

            /**
             * Update full day button label for specific number of days
             * @param {number} days - Number of days to show in label
             */
            updateFullDayButtonLabelForDays(days) {
                const button = window.RentalConfig?.getQuickScheduleButton('fullDay') ||
                    document.getElementById('qs_full_day');
                if (!button) return;

                const svgHTML = button.querySelector('svg').outerHTML;
                const label = days > 1 ? ` Full Day (${days} days)` : ' Full Day';
                button.innerHTML = svgHTML + label;
            }

            /**
             * Show field validation error
             */
            showFieldValidationError(fieldId, message) {
                const field = document.getElementById(fieldId);
                if (!field) return;

                // Remove existing error
                const existingError = field.parentElement.parentElement.querySelector('.validation-error-message');
                if (existingError) {
                    existingError.remove();
                }

                // Style field with error
                field.classList.remove('border-gray-300', 'focus:border-indigo-500');
                field.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');

                // Create error message
                const errorElement = document.createElement('p');
                errorElement.className = 'validation-error-message mt-2 text-sm text-red-600';
                errorElement.textContent = message;

                // Insert error message
                const fieldContainer = field.parentElement.parentElement;
                fieldContainer.appendChild(errorElement);

                // Focus and scroll to field
                field.focus();
                field.scrollIntoView({ behavior: 'smooth', block: 'center' });

                // Setup error clearing
                const clearError = () => {
                    field.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
                    field.classList.add('border-gray-300', 'focus:border-indigo-500');
                    if (errorElement.parentElement) {
                        errorElement.remove();
                    }
                    field.removeEventListener('input', clearError);
                    field.removeEventListener('change', clearError);
                };

                field.addEventListener('input', clearError);
                field.addEventListener('change', clearError);
            }
        }

        /**
 * Utility function to format rate labels consistently
 * This mirrors the Django template tag logic for consistency
 */
        function formatRateLabel(rateCategory, hasHalfDay = false, halfDayRate = null) {
            if (!rateCategory) {
                return 'Rate';
            }

            // Handle daily with half-day component
            if (rateCategory.toLowerCase() === 'daily' && hasHalfDay) {
                let label = 'Rate (Daily + half day';
                if (halfDayRate !== null) {
                    label += `: $${halfDayRate.toFixed(2)}`;
                }
                label += ')';
                return label;
            }

            // Handle all other categories
            const displayCategory = rateCategory.charAt(0).toUpperCase() + rateCategory.slice(1).replace('_', ' ');
            return `Rate (${displayCategory})`;
        }

        /**
         * RateTypeManager - Handles rate type label updates
         */
        class RateTypeManager {
            constructor(fieldIds) {
                this.fieldIds = fieldIds;
                this.rateTypeLabel = window.RentalConfig?.getDisplay('rateTypeLabel') ||
                    document.getElementById('rate_type_label');
            }

            /**
             * Update rate type label based on current form state
             */
            async updateRateTypeLabel() {
                if (!this.rateTypeLabel) return;

                const customRateInput = document.getElementById(this.fieldIds.customRate);

                // Check for custom rate
                if (customRateInput?.value) {
                    const customRate = parseFloat(customRateInput.value);
                    if (!isNaN(customRate)) {
                        this.rateTypeLabel.textContent = 'Rate (Custom)';
                        return;
                    }
                }

                // Get rate type from API
                const startDate = document.getElementById(this.fieldIds.startDateTime).value;
                const endDate = document.getElementById(this.fieldIds.endDateTime).value;
                const trailerId = document.getElementById(this.fieldIds.trailer).value;

                if (!trailerId || !startDate || !endDate) {
                    this.rateTypeLabel.textContent = 'Rate';
                    return;
                }

                try {
                    const response = await window.RentalCalculator.calculateDurationInfo(startDate, endDate);
                    const { rate_category, has_half_day } = response.duration_info || {};

                    // Get half-day rate if available
                    let halfDayRate = null;
                    if (rate_category === 'daily' && has_half_day) {
                        const trailerRates = window.ActiveTrailerDetails?.trailerRates;
                        if (trailerRates && trailerRates[trailerId] && trailerRates[trailerId].halfDayRate !== undefined) {
                            halfDayRate = trailerRates[trailerId].halfDayRate;
                        }
                    }

                    // Use the centralized rate label formatting function
                    const label = formatRateLabel(rate_category, has_half_day, halfDayRate);

                    this.rateTypeLabel.textContent = label;
                } catch (error) {
                    window.Logger?.error('Error getting rate type:', error);
                    this.rateTypeLabel.textContent = formatRateLabel();
                }
            }
        }

        /**
         * TrailerDetailsApp - Main application controller
         */
        class TrailerDetailsApp {
            constructor(config) {
                this.config = config;
                this.initializeApp();
            }

            /**
             * Initialize the complete application
             */
            initializeApp() {
                // Disable autocomplete on date inputs
                this.disableAutocomplete();

                // Initialize main components
                this.trailerDetails = new TrailerDetails(this.config);
                window.ActiveTrailerDetails = this.trailerDetails;
                this.quickSchedule = new QuickSchedule(this.config.fieldIds);
                this.rateTypeManager = new RateTypeManager(this.config.fieldIds);

                // Override calculateRate to include rate type updates
                if (this.trailerDetails && this.rateTypeManager) {
                    this.enhanceCalculateRate();
                }
            }

            /**
             * Disable autocomplete on date/time inputs
             */
            disableAutocomplete() {
                const startDateInput = document.getElementById(this.config.fieldIds.startDateTime);
                const endDateInput = document.getElementById(this.config.fieldIds.endDateTime);

                if (startDateInput) {
                    startDateInput.setAttribute('autocomplete', 'off');
                }
                if (endDateInput) {
                    endDateInput.setAttribute('autocomplete', 'off');
                }
            }

            /**
             * Enhance calculateRate method to include rate type updates
             */
            enhanceCalculateRate() {
                const originalCalculateRate = this.trailerDetails.calculateRate.bind(this.trailerDetails);

                this.trailerDetails.calculateRate = async () => {
                    await originalCalculateRate();
                    await this.rateTypeManager.updateRateTypeLabel();
                };
            }
        };

        // Export classes for global access
        window.QuickSchedule = QuickSchedule;
        window.RateTypeManager = RateTypeManager;
        window.TrailerDetailsApp = TrailerDetailsApp;

        /**
         * Auto-initialization for trailer details forms
         * Looks for forms with trailer details and initializes automatically
         */
        function autoInitializeTrailerDetails() {
            // Look for trailer details form container
            const trailerDetailsContainer = document.querySelector('[data-trailer-details]');
            if (!trailerDetailsContainer) {
                window.Logger?.debug('TrailerDetails: No trailer details container found, skipping auto-initialization');
                return;
            }

            // Extract configuration from data attributes
            const config = {
                fieldIds: window.RentalConfig?.fieldIds || {},
                currentContractId: trailerDetailsContainer.dataset.contractId || '',
                taxRate: parseFloat(trailerDetailsContainer.dataset.taxRate || '0'),
                formContext: {
                    instanceId: trailerDetailsContainer.dataset.contractId || '',
                    taxRate: parseFloat(trailerDetailsContainer.dataset.taxRate || '0'),
                    furnitureBlanketPrice: parseFloat(trailerDetailsContainer.dataset.furnitureBlanketPrice || '0'),
                    strapChainPrice: parseFloat(trailerDetailsContainer.dataset.strapChainPrice || '0')
                }
            };

            window.Logger?.debug('TrailerDetails: Auto-initializing with config', config);

            // Initialize the app
            new TrailerDetailsApp(config);
        }

        // Auto-initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', autoInitializeTrailerDetails);
        } else {
            // DOM is already loaded
            autoInitializeTrailerDetails();
        }

    } else {
        window.Logger?.debug('TrailerDetails already exists, skipping initialization');
    }

})(); // End of IIFE