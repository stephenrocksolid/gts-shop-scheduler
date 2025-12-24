/**
 * Calendar Toolbar Module
 * 
 * Handles toolbar UI elements including jump-to-date, calendar multi-select, and status dropdown.
 * Registers: styleCustomButtons, addJumpToDateControl, initializeJumpToDate,
 *            createCalendarMultiSelect, updateCalendarButtonText, initializeMovedCalendarDropdown,
 *            initializeMovedStatusDropdown, selectAllCalendars, adjustSundayColumnWidth
 */
(function() {
    'use strict';

    GTS.calendar.register('toolbar', function(proto) {
        /**
         * Adjust all day column widths to be equal
         */
        proto.adjustSundayColumnWidth = function() {
            // Find the table body
            var tableBody = document.querySelector('.fc-daygrid-body');
            if (!tableBody) return;

            // Find all rows in the table
            var rows = tableBody.querySelectorAll('tr');

            rows.forEach(function(row) {
                var cells = row.querySelectorAll('td');
                cells.forEach(function(cell) {
                    // All days equal width (100% / 7 days = 14.29%)
                    cell.style.width = '14.29%';
                    cell.style.minWidth = '14.29%';
                    cell.style.maxWidth = '14.29%';
                });
            });

            // Also target the day columns directly
            var dayColumns = document.querySelectorAll('.fc-daygrid-day');
            dayColumns.forEach(function(column) {
                // All days equal width (100% / 7 days = 14.29%)
                column.style.width = '14.29%';
                column.style.minWidth = '14.29%';
                column.style.maxWidth = '14.29%';
            });
        };

        /**
         * Style the custom buttons for better appearance
         */
        proto.styleCustomButtons = function() {
            var self = this;
            // Wait a bit for the DOM to be ready
            setTimeout(function() {
                // Adjust Sunday column width
                self.adjustSundayColumnWidth();

                // Hide the original calendar filter button since we moved it
                var calendarFilterBtn = document.querySelector('.fc-calendarFilterButton-button');
                if (calendarFilterBtn) {
                    calendarFilterBtn.style.display = 'none';
                }

                // Hide the original status filter button since we moved it
                var statusFilterBtn = document.querySelector('.fc-statusFilterButton-button');
                if (statusFilterBtn) {
                    statusFilterBtn.style.display = 'none';
                }

                // Add Jump to Date control
                self.addJumpToDateControl();
            }, 100);
        };

        /**
         * Add Jump to Date, Calendar, and Status controls to the calendar toolbar
         */
        proto.addJumpToDateControl = function() {
            var self = this;

            // Find the calendar toolbar
            var toolbar = document.querySelector('.fc-header-toolbar');
            if (!toolbar) return;

            // Create the controls container
            var controlsContainer = document.createElement('div');
            controlsContainer.className = 'fc-unified-controls';
            controlsContainer.style.cssText = 'display: flex; align-items: center; gap: 12px; margin-right: 16px;';

            // Create Jump to Date section
            var jumpToDateSection = document.createElement('div');
            jumpToDateSection.style.cssText = 'display: flex; align-items: center; gap: 8px;';

            // Create Jump to Date input
            var dateInput = document.createElement('input');
            dateInput.id = 'jump-to-date';
            dateInput.name = 'jump_to_date';
            dateInput.type = 'text';
            dateInput.placeholder = 'YYYY-MM-DD';
            dateInput.autocomplete = 'off';
            dateInput.style.cssText = 'height: 36px; width: 176px; border-radius: 6px; border: 1px solid #d1d5db; padding: 0 12px; font-size: 14px; color: #374151; background: #ffffff; transition: border-color 0.2s ease;';

            // Add hover and focus styles for date input
            dateInput.addEventListener('mouseenter', function() { dateInput.style.borderColor = '#9ca3af'; });
            dateInput.addEventListener('mouseleave', function() { if (document.activeElement !== dateInput) dateInput.style.borderColor = '#d1d5db'; });
            dateInput.addEventListener('focus', function() { dateInput.style.borderColor = '#3b82f6'; dateInput.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)'; });
            dateInput.addEventListener('blur', function() { dateInput.style.borderColor = '#d1d5db'; dateInput.style.boxShadow = 'none'; });

            // Create Today button
            var todayButton = document.createElement('button');
            todayButton.type = 'button';
            todayButton.title = 'Jump to Today';
            todayButton.style.cssText = 'height: 36px; width: 36px; padding: 0; border-radius: 6px; border: 1px solid #d1d5db; background: #ffffff; color: #374151; cursor: pointer; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center;';
            todayButton.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>';

            // Add hover styles for today button
            todayButton.addEventListener('mouseenter', function() { todayButton.style.borderColor = '#3b82f6'; todayButton.style.backgroundColor = '#eff6ff'; todayButton.style.color = '#3b82f6'; });
            todayButton.addEventListener('mouseleave', function() { todayButton.style.borderColor = '#d1d5db'; todayButton.style.backgroundColor = '#ffffff'; todayButton.style.color = '#374151'; });

            // Add click handler to jump to today
            todayButton.addEventListener('click', function() {
                var today = new Date();
                self.calendar.gotoDate(today);

                // Update the date input
                var pad = function(n) { return String(n).padStart(2, '0'); };
                var fmt = today.getFullYear() + '-' + pad(today.getMonth() + 1) + '-' + pad(today.getDate());
                dateInput.value = fmt;

                // Update URL param
                var sp = new URLSearchParams(window.location.search);
                sp.set('date', fmt);
                history.replaceState({}, '', location.pathname + '?' + sp.toString());
            });

            // Create Calendar dropdown section
            var calendarSection = document.createElement('div');
            calendarSection.style.cssText = 'display: flex; align-items: center; gap: 8px;';
            var calendarMultiSelect = this.createCalendarMultiSelect();

            // Create Status dropdown section
            var statusSection = document.createElement('div');
            statusSection.style.cssText = 'display: flex; align-items: center; gap: 8px;';

            // Create Status dropdown
            var statusDropdown = document.createElement('select');
            statusDropdown.id = 'status-filter-moved';
            statusDropdown.style.cssText = 'height: 36px; min-width: 120px; border-radius: 6px; border: 1px solid #d1d5db; padding: 0 12px; font-size: 14px; color: #374151; background: #ffffff; cursor: pointer; transition: border-color 0.2s ease;';
            statusDropdown.innerHTML = '<option value="">All Status</option><option value="uncompleted">Uncompleted</option><option value="completed">Completed</option>';

            // Add hover and focus styles for status dropdown
            statusDropdown.addEventListener('mouseenter', function() { statusDropdown.style.borderColor = '#9ca3af'; });
            statusDropdown.addEventListener('mouseleave', function() { if (document.activeElement !== statusDropdown) statusDropdown.style.borderColor = '#d1d5db'; });
            statusDropdown.addEventListener('focus', function() { statusDropdown.style.borderColor = '#3b82f6'; statusDropdown.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)'; });
            statusDropdown.addEventListener('blur', function() { statusDropdown.style.borderColor = '#d1d5db'; statusDropdown.style.boxShadow = 'none'; });

            // Assemble the sections
            jumpToDateSection.appendChild(dateInput);
            jumpToDateSection.appendChild(todayButton);
            calendarSection.appendChild(calendarMultiSelect);
            statusSection.appendChild(statusDropdown);

            controlsContainer.appendChild(jumpToDateSection);
            controlsContainer.appendChild(calendarSection);
            controlsContainer.appendChild(statusSection);
            toolbar.insertBefore(controlsContainer, toolbar.firstChild);

            // Initialize the jump to date functionality
            this.initializeJumpToDate(dateInput);

            // Update the calendar button text now that it's in the DOM
            this.updateCalendarButtonText();

            // Initialize the status dropdown functionality
            this.initializeMovedStatusDropdown(statusDropdown);
        };

        /**
         * Create calendar multi-select checkbox UI
         */
        proto.createCalendarMultiSelect = function() {
            var self = this;
            var container = document.createElement('div');
            container.style.cssText = 'position: relative; display: inline-block;';

            // Create button
            var button = document.createElement('button');
            button.id = 'calendar-multi-select-button';
            button.type = 'button';
            button.style.cssText = 'height: 36px; min-width: 140px; border-radius: 6px; border: 1px solid #d1d5db; padding: 0 32px 0 12px; font-size: 14px; color: #374151; background: #ffffff; cursor: pointer; transition: border-color 0.2s ease; text-align: left; position: relative; white-space: nowrap;';
            button.innerHTML = '<span id="calendar-button-text">All Calendars</span><svg style="position: absolute; right: 8px; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; pointer-events: none;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>';

            // Create popover
            var popover = document.createElement('div');
            popover.id = 'calendar-multi-select-popover';
            popover.style.cssText = 'position: absolute; top: calc(100% + 4px); left: 0; min-width: 220px; max-height: 400px; overflow-y: auto; background: white; border: 1px solid #d1d5db; border-radius: 8px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15); z-index: 1000; display: none; padding: 8px;';

            var calendars = (window.calendarConfig && window.calendarConfig.calendars) || [];

            // Build checkboxes
            var checkboxesHTML = '';

            // Add "All" checkbox
            var allChecked = this.selectedCalendars.size === calendars.length;
            checkboxesHTML += '<label style="display: flex; align-items: center; padding: 8px; cursor: pointer; border-radius: 4px; transition: background 0.15s;" onmouseover="this.style.background=\'#f3f4f6\'" onmouseout="this.style.background=\'transparent\'">' +
                '<input type="checkbox" data-calendar-id="all" ' + (allChecked ? 'checked' : '') + ' style="width: 16px; height: 16px; margin-right: 8px; cursor: pointer;">' +
                '<span style="font-weight: 600; color: #111827;">All Calendars</span></label>' +
                '<div style="border-top: 1px solid #e5e7eb; margin: 4px 0;"></div>';

            // Add individual calendar checkboxes
            calendars.forEach(function(cal) {
                var isChecked = self.selectedCalendars.has(cal.id);
                var isDefault = self.defaultCalendar === cal.id;
                var backgroundColor = isDefault ? '#e0f2fe' : 'transparent';

                checkboxesHTML += '<div class="calendar-item" data-calendar-id="' + cal.id + '" style="display: flex; align-items: center; padding: 8px; border-radius: 4px; transition: background 0.15s; background: ' + backgroundColor + ';">' +
                    '<input type="checkbox" data-calendar-id="' + cal.id + '" ' + (isChecked ? 'checked' : '') + ' style="width: 16px; height: 16px; margin-right: 8px; cursor: pointer; accent-color: ' + cal.color + ';">' +
                    '<div class="calendar-name-area" data-calendar-id="' + cal.id + '" style="display: flex; align-items: center; flex: 1; cursor: pointer;">' +
                    '<span style="display: inline-block; width: 12px; height: 12px; border-radius: 3px; background: ' + cal.color + '; margin-right: 8px;"></span>' +
                    '<span style="color: #374151; flex: 1;">' + cal.name + '</span></div></div>';
            });

            popover.innerHTML = checkboxesHTML;

            // Set initial indeterminate state for "All" checkbox if partially selected
            var selectedCount = this.selectedCalendars.size;
            var totalCount = calendars.length;
            if (selectedCount > 0 && selectedCount < totalCount) {
                var allCheckbox = popover.querySelector('input[data-calendar-id="all"]');
                if (allCheckbox) allCheckbox.indeterminate = true;
            }

            // Prevent scroll events from propagating to calendar
            popover.addEventListener('wheel', function(e) { e.stopPropagation(); }, { passive: false });

            // Toggle popover on button click
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                var isVisible = popover.style.display === 'block';
                popover.style.display = isVisible ? 'none' : 'block';
            });

            // Close popover when clicking outside
            document.addEventListener('click', function(e) {
                if (!container.contains(e.target)) popover.style.display = 'none';
            });

            // Handle calendar name clicks (set as default)
            popover.addEventListener('click', function(e) {
                var nameArea = e.target.closest('.calendar-name-area');
                if (nameArea) {
                    e.stopPropagation();
                    var calendarId = parseInt(nameArea.dataset.calendarId);

                    // Set as default calendar
                    self.defaultCalendar = calendarId;

                    // Auto-check the checkbox if not already checked
                    if (!self.selectedCalendars.has(calendarId)) {
                        self.selectedCalendars.add(calendarId);
                        var checkbox = popover.querySelector('input[type="checkbox"][data-calendar-id="' + calendarId + '"]');
                        if (checkbox) checkbox.checked = true;

                        // Update "All" checkbox
                        var allCheckbox = popover.querySelector('input[data-calendar-id="all"]');
                        var sc = self.selectedCalendars.size;
                        var tc = calendars.length;
                        allCheckbox.checked = sc === tc;
                        allCheckbox.indeterminate = sc > 0 && sc < tc;

                        // Save selected calendars
                        try { localStorage.setItem('gts-selected-calendars', JSON.stringify(Array.from(self.selectedCalendars))); }
                        catch (err) { console.warn('Error saving calendar selection:', err); }
                    }

                    // Update visual highlighting
                    popover.querySelectorAll('.calendar-item').forEach(function(item) {
                        var itemId = parseInt(item.dataset.calendarId);
                        item.style.background = itemId === calendarId ? '#e0f2fe' : 'transparent';
                    });

                    // Save default calendar
                    try { localStorage.setItem('gts-default-calendar', calendarId.toString()); }
                    catch (err) { console.warn('Error saving default calendar:', err); }

                    self.updateCalendarButtonText();
                    self.debouncedRefetch();
                }
            });

            // Handle checkbox changes
            popover.addEventListener('change', function(e) {
                if (e.target.type === 'checkbox') {
                    var calendarId = e.target.dataset.calendarId;

                    if (calendarId === 'all') {
                        var allCheckbox = e.target;
                        var checkboxes = popover.querySelectorAll('input[type="checkbox"][data-calendar-id]:not([data-calendar-id="all"])');
                        allCheckbox.indeterminate = false;

                        if (allCheckbox.checked) {
                            self.selectedCalendars = new Set(calendars.map(function(c) { return c.id; }));
                            checkboxes.forEach(function(cb) { cb.checked = true; });
                        } else {
                            self.selectedCalendars.clear();
                            checkboxes.forEach(function(cb) { cb.checked = false; });
                        }
                    } else {
                        var id = parseInt(calendarId);
                        if (e.target.checked) {
                            self.selectedCalendars.add(id);
                        } else {
                            self.selectedCalendars.delete(id);
                        }

                        var allCb = popover.querySelector('input[data-calendar-id="all"]');
                        var sc = self.selectedCalendars.size;
                        var tc = calendars.length;
                        allCb.checked = sc === tc;
                        allCb.indeterminate = sc > 0 && sc < tc;
                    }

                    self.updateCalendarButtonText();

                    try { localStorage.setItem('gts-selected-calendars', JSON.stringify(Array.from(self.selectedCalendars))); }
                    catch (err) { console.warn('Error saving calendar selection:', err); }

                    self.debouncedRefetch();
                }
            });

            container.appendChild(button);
            container.appendChild(popover);

            return container;
        };

        /**
         * Update calendar button text based on selection
         */
        proto.updateCalendarButtonText = function() {
            var buttonText = document.getElementById('calendar-button-text');
            if (!buttonText) return;

            var calendars = (window.calendarConfig && window.calendarConfig.calendars) || [];
            var selectedCount = this.selectedCalendars.size;

            if (selectedCount === 0) {
                buttonText.textContent = 'No Calendars';
            } else if (selectedCount === calendars.length) {
                buttonText.textContent = 'All Calendars';
            } else if (selectedCount === 1) {
                var selectedId = Array.from(this.selectedCalendars)[0];
                var calendar = calendars.find(function(c) { return c.id === selectedId; });
                buttonText.textContent = calendar ? calendar.name : 'Calendars (1)';
            } else {
                buttonText.textContent = 'Calendars (' + selectedCount + ')';
            }
        };

        /**
         * Initialize Jump to Date functionality
         */
        proto.initializeJumpToDate = function(input) {
            var self = this;

            // Helper: format Date -> YYYY-MM-DD (local)
            var fmt = function(d) {
                if (window.GtsDateInputs && window.GtsDateInputs.formatISODate) {
                    return window.GtsDateInputs.formatISODate(d);
                }
                var pad = function(n) { return String(n).padStart(2, '0'); };
                return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
            };

            // Helper: parse ISO date safely (local timezone)
            var parseISO = function(str) {
                if (window.GtsDateInputs && window.GtsDateInputs.parseISOLocal) {
                    return window.GtsDateInputs.parseISOLocal(str);
                }
                if (!str) return null;
                var m = str.match(/^(\d{4})-(\d{2})-(\d{2})$/);
                if (m) return new Date(parseInt(m[1]), parseInt(m[2]) - 1, parseInt(m[3]));
                return new Date(str);
            };

            // Pick initial date from URL (?date=YYYY-MM-DD) or today
            var params = new URLSearchParams(window.location.search);
            var urlDate = params.get('date');
            var initialDate = urlDate ? parseISO(urlDate) : new Date();
            var safeInitialDate = (initialDate && !isNaN(initialDate.getTime())) ? initialDate : new Date();

            input.value = fmt(safeInitialDate);

            if (urlDate && safeInitialDate) {
                try { this.calendar.gotoDate(safeInitialDate); }
                catch (e) { console.warn('Failed to navigate to URL date:', e); }
            }

            var fpInstance = null;

            if (window.GtsDateInputs && window.GtsDateInputs.initFriendlyDateInput) {
                fpInstance = window.GtsDateInputs.initFriendlyDateInput(input, {
                    enableTime: false,
                    defaultDate: safeInitialDate,
                    onChange: function(selectedDates) {
                        var d = selectedDates && selectedDates[0];
                        if (!d) return;
                        self.calendar.gotoDate(d);
                        var sp = new URLSearchParams(window.location.search);
                        sp.set('date', fmt(d));
                        history.replaceState({}, '', location.pathname + '?' + sp.toString());
                    }
                });
            } else if (window.flatpickr) {
                fpInstance = flatpickr(input, {
                    dateFormat: 'Y-m-d',
                    allowInput: true,
                    defaultDate: input.value,
                    onChange: function(selectedDates) {
                        var d = selectedDates && selectedDates[0];
                        if (!d) return;
                        self.calendar.gotoDate(d);
                        var sp = new URLSearchParams(window.location.search);
                        sp.set('date', fmt(d));
                        history.replaceState({}, '', location.pathname + '?' + sp.toString());
                    }
                });
            } else {
                input.type = 'date';
                input.addEventListener('change', function(e) {
                    var val = e.target.value;
                    if (!val) return;
                    var d = parseISO(val);
                    if (d && !isNaN(d.getTime())) {
                        self.calendar.gotoDate(d);
                        var sp = new URLSearchParams(window.location.search);
                        sp.set('date', val);
                        history.replaceState({}, '', location.pathname + '?' + sp.toString());
                    }
                });
            }

            // Keep picker synced when navigating via calendar arrows
            this.calendar.on('datesSet', function(info) {
                var center = info.view.currentStart;
                if (fpInstance && fpInstance.setDate) {
                    fpInstance.setDate(center, false);
                } else {
                    input.value = fmt(center);
                }
            });
        };

        /**
         * Initialize the moved calendar dropdown functionality
         */
        proto.initializeMovedCalendarDropdown = function(dropdown) {
            this.calendarFilter = dropdown;
            dropdown.addEventListener('change', this.handleFilterChange.bind(this));
            if (this.currentFilters.calendar) {
                dropdown.value = this.currentFilters.calendar;
            }
        };

        /**
         * Initialize the moved status dropdown functionality
         */
        proto.initializeMovedStatusDropdown = function(dropdown) {
            this.statusFilter = dropdown;
            dropdown.addEventListener('change', this.handleFilterChange.bind(this));
            if (this.currentFilters.status) {
                dropdown.value = this.currentFilters.status;
            }
        };

        /**
         * Select all calendars and refresh the calendar
         * Called from the no-calendars overlay "Select all" button
         */
        proto.selectAllCalendars = function() {
            var self = this;
            var calendars = (window.calendarConfig && window.calendarConfig.calendars) || [];
            this.selectedCalendars = new Set(calendars.map(function(c) { return c.id; }));

            // Update the checkbox UI in the popover
            var popover = document.getElementById('calendar-multi-select-popover');
            if (popover) {
                var allCheckbox = popover.querySelector('input[data-calendar-id="all"]');
                if (allCheckbox) {
                    allCheckbox.checked = true;
                    allCheckbox.indeterminate = false;
                }
                var checkboxes = popover.querySelectorAll('input[type="checkbox"][data-calendar-id]:not([data-calendar-id="all"])');
                checkboxes.forEach(function(cb) { cb.checked = true; });
            }

            // Save to localStorage
            try { localStorage.setItem('gts-selected-calendars', JSON.stringify(Array.from(this.selectedCalendars))); }
            catch (error) { console.warn('Error saving calendar selection:', error); }

            // Update button text
            this.updateCalendarButtonText();

            // Hide the overlay and refresh calendar
            this.updateNoCalendarsOverlay(false);
            this.debouncedRefetch();
        };
    });

})();
