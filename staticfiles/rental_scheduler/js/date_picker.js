document.addEventListener('DOMContentLoaded', function () {
    // Prevent multiple initializations
    if (window.datePickerInitialized) {
        window.Logger?.debug('DatePicker: Already initialized, skipping');
        return;
    }
    window.datePickerInitialized = true;

    // Use RentalConfig for field IDs if available, otherwise fallback to hardcoded values
    const startDateTimeId = window.RentalConfig?.fieldIds?.startDateTime || 'id_start_datetime';
    const endDateTimeId = window.RentalConfig?.fieldIds?.endDateTime || 'id_end_datetime';
    const returnDateTimeId = window.RentalConfig?.fieldIds?.returnDateTime || 'id_return_datetime';
    const isReturnedId = window.RentalConfig?.fieldIds?.isReturned || 'id_is_returned';

    const startElement = document.getElementById(startDateTimeId);
    const endElement = document.getElementById(endDateTimeId);

    if (!startElement || !endElement) {
        window.Logger?.error('DatePicker: Could not find required datetime input fields', {
            startDateTimeId,
            endDateTimeId,
            startElementFound: !!startElement,
            endElementFound: !!endElement
        });
        return;
    }

    window.Logger?.debug('DatePicker: Initializing date picker for contract form');

    const commonConfig = {
        enableTime: true,
        dateFormat: "m/d/Y h:i K",
        time_24hr: false,
        minuteIncrement: 15,
        minDate: "today",
        allowInput: true,
        placeholder: "MM/DD/YYYY HH:MM AM/PM",
        theme: "light",
        position: "auto",
        onChange: function (selectedDates, dateStr, instance) {
            instance.input.value = dateStr;
        }
    };

    const startPicker = flatpickr(`#${startDateTimeId}`, {
        ...commonConfig,
        defaultHour: 7,
        defaultMinute: 0,
        onChange: function (selectedDates, dateStr, instance) {
            instance.input.value = dateStr;
            window.Logger?.debug('DatePicker: Start date changed', { dateStr, selectedDate: selectedDates[0] });

            const endDate = endPicker.selectedDates[0];
            if (endDate && selectedDates[0]) {
                const minEndTime = new Date(selectedDates[0].getTime() + 60000);
                if (endDate < minEndTime) {
                    window.Logger?.debug('DatePicker: Start date changed, end date must be at least 1 minute after, clearing end date');
                    endPicker.clear();
                }
            }
            if (selectedDates.length > 0) {
                const minEndTime = new Date(selectedDates[0].getTime() + 60000);
                endPicker.set('minDate', minEndTime);

                if (!endDate || !endPicker.input.value) {
                    const endDateTime = new Date(selectedDates[0]);
                    endDateTime.setHours(17, 0, 0, 0);
                    isEndDateAutoSet = true;
                    endPicker.setDate(endDateTime, true);
                }
            }
            instance.input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });

    // Flag to track if end date is being set automatically
    let isEndDateAutoSet = false;

    const endPicker = flatpickr(`#${endDateTimeId}`, {
        ...commonConfig,
        defaultHour: 17,
        defaultMinute: 0,
        onChange: function (selectedDates, dateStr, instance) {
            if (selectedDates.length > 0 && isEndDateAutoSet) {
                const selectedDate = new Date(selectedDates[0]);
                selectedDate.setHours(17, 0, 0, 0);
                const formattedDate = instance.formatDate(selectedDate, "m/d/Y h:i K");
                instance.input.value = formattedDate;
                instance.selectedDates[0] = selectedDate;
                isEndDateAutoSet = false;
            }

            window.Logger?.debug('DatePicker: End date changed', { dateStr, selectedDate: selectedDates[0] });

            const startDate = startPicker.selectedDates[0];
            if (startDate && selectedDates[0]) {
                const minEndTime = new Date(startDate.getTime() + 60000);
                if (selectedDates[0] <= minEndTime) {
                    window.Logger?.debug('DatePicker: End date must be at least 1 minute after start date, clearing end date');
                    instance.clear();
                    return;
                }
            }
            instance.input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.altKey && e.key === 's') {
            e.preventDefault();
            startPicker.open();
        }
        if (e.altKey && e.key === 'e') {
            e.preventDefault();
            endPicker.open();
        }
    });

    // Handle return datetime checkbox and field visibility
    const isReturnedCheckbox = document.getElementById(isReturnedId);
    const returnDateTimeContainer = document.getElementById('return_datetime_container');
    const returnDateTimeInput = document.getElementById(returnDateTimeId);

    if (isReturnedCheckbox && returnDateTimeContainer && returnDateTimeInput) {
        // Initialize return picker with 5 PM default
        let returnPicker = null;

        function initializeReturnPicker() {
            if (!returnPicker) {
                returnPicker = flatpickr(`#${returnDateTimeId}`, {
                    ...commonConfig,
                    defaultHour: 17,
                    defaultMinute: 0,
                    minDate: null, // Allow past dates for return datetime
                    onChange: function (selectedDates, dateStr, instance) {
                        instance.input.value = dateStr;
                        window.Logger?.debug('DatePicker: Return date changed', { dateStr, selectedDate: selectedDates[0] });
                        instance.input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });
                window.Logger?.debug('DatePicker: Return datetime picker initialized');
            }
            return returnPicker;
        }

        function handleReturnDateTimeVisibility() {
            if (isReturnedCheckbox.checked) {
                returnDateTimeContainer.classList.remove('hidden');
                returnDateTimeInput.required = true;

                // Initialize picker if not already done
                const picker = initializeReturnPicker();

                // Set default time to 5 PM today if no value exists
                if (!returnDateTimeInput.value) {
                    const now = new Date();
                    const defaultReturnTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 17, 0);
                    picker.setDate(defaultReturnTime, true);
                    window.Logger?.debug('DatePicker: Set default return time to 5 PM');
                }
            } else {
                returnDateTimeContainer.classList.add('hidden');
                returnDateTimeInput.required = false;
                // Clear the field when unchecked
                if (returnPicker && typeof returnPicker.clear === 'function') {
                    try {
                        returnPicker.clear();
                    } catch (error) {
                        window.Logger?.warn('DatePicker: Error clearing return picker', error);
                        // Fallback to manual clear
                        returnDateTimeInput.value = '';
                    }
                }
            }
        }

        // Set initial state
        handleReturnDateTimeVisibility();

        // Listen for checkbox changes
        isReturnedCheckbox.addEventListener('change', handleReturnDateTimeVisibility);

        // Add keyboard shortcut for return date picker
        document.addEventListener('keydown', function (e) {
            if (e.altKey && e.key === 'r' && returnPicker) {
                e.preventDefault();
                returnPicker.open();
            }
        });

        window.Logger?.debug('DatePicker: Return datetime checkbox handler initialized');
    }

    window.Logger?.info('DatePicker: All date pickers initialized successfully');
}); 