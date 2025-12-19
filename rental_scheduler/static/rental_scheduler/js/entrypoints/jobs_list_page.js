/**
 * Jobs List Page Entrypoint
 * 
 * Extracted from job_list.html inline script.
 * Handles:
 * - Calendar dropdown open/close + selection label
 * - Date filter radios + show/hide custom date range
 * - Persist filters to localStorage (job-list-filters)
 * - Search input Enter behavior (submit once, then cycle highlights)
 * - Per-row click/hover handlers via event delegation
 * 
 * Requires: GTS.initOnce, window.JobPanel
 */
(function() {
    'use strict';

    /**
     * Initialize the jobs list page behaviors.
     */
    function initJobsListPage() {
        GTS.onDomReady(function() {
            GTS.initOnce('jobs_list_page', function() {
                initCalendarDropdown();
                initDateFilterRadios();
                initLocalStoragePersistence();
                initSearchNavigation();
                initRowClickHandlers();
            });
        });
    }

    // ========================================================================
    // CALENDAR DROPDOWN
    // ========================================================================

    function initCalendarDropdown() {
        const calendarDropdownBtn = document.getElementById('calendar-dropdown-btn');
        const calendarDropdown = document.getElementById('calendar-dropdown');
        const calendarCheckboxes = document.querySelectorAll('.calendar-checkbox');
        const calendarSelectedText = document.getElementById('calendar-selected-text');

        if (!calendarDropdownBtn || !calendarDropdown) return;

        // Toggle calendar dropdown
        calendarDropdownBtn.addEventListener('click', function(e) {
            e.preventDefault();
            calendarDropdown.classList.toggle('hidden');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!calendarDropdownBtn.contains(e.target) && !calendarDropdown.contains(e.target)) {
                calendarDropdown.classList.add('hidden');
            }
        });

        // Update selected text when checkboxes change
        calendarCheckboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                updateCalendarSelectedText();
                saveFiltersToLocalStorage();
            });
        });

        function updateCalendarSelectedText() {
            if (!calendarSelectedText) return;
            
            const checkedCount = document.querySelectorAll('.calendar-checkbox:checked').length;
            const totalCount = calendarCheckboxes.length;

            if (checkedCount === 0 || checkedCount === totalCount) {
                calendarSelectedText.textContent = 'All Calendars';
            } else {
                calendarSelectedText.textContent = checkedCount + ' calendar(s) selected';
            }
        }
    }

    // ========================================================================
    // DATE FILTER RADIOS
    // ========================================================================

    function initDateFilterRadios() {
        const dateFilterRadios = document.querySelectorAll('.date-filter-radio');
        const customDateRange = document.getElementById('custom-date-range');

        if (!customDateRange) return;

        // Toggle custom date range visibility
        dateFilterRadios.forEach(function(radio) {
            radio.addEventListener('change', function() {
                if (this.value === 'custom') {
                    customDateRange.classList.remove('hidden');
                } else {
                    customDateRange.classList.add('hidden');
                }

                saveFiltersToLocalStorage();
            });
        });
    }

    // ========================================================================
    // LOCAL STORAGE PERSISTENCE
    // ========================================================================

    function saveFiltersToLocalStorage() {
        const filters = {
            calendars: Array.from(document.querySelectorAll('.calendar-checkbox:checked')).map(function(cb) {
                return cb.value;
            }),
            dateFilter: (document.querySelector('.date-filter-radio:checked') || {}).value || 'all'
        };
        localStorage.setItem('job-list-filters', JSON.stringify(filters));
    }

    function initLocalStoragePersistence() {
        const saved = localStorage.getItem('job-list-filters');
        if (!saved) return;

        try {
            const filters = JSON.parse(saved);

            // Only apply saved filters if no filters are currently set via URL
            const urlParams = new URLSearchParams(window.location.search);
            const hasUrlFilters = urlParams.has('calendars') || 
                                  (urlParams.has('date_filter') && urlParams.get('date_filter') !== 'all') ||
                                  urlParams.has('search');

            if (hasUrlFilters) {
                // URL has filters, don't override with localStorage
                return;
            }

            // Apply saved calendar filters
            if (filters.calendars && filters.calendars.length > 0) {
                const calendarCheckboxes = document.querySelectorAll('.calendar-checkbox');
                const calendarSelectedText = document.getElementById('calendar-selected-text');
                
                calendarCheckboxes.forEach(function(cb) {
                    cb.checked = filters.calendars.includes(cb.value);
                });

                // Update selected text
                if (calendarSelectedText) {
                    const checkedCount = filters.calendars.length;
                    const totalCount = calendarCheckboxes.length;
                    if (checkedCount === totalCount) {
                        calendarSelectedText.textContent = 'All Calendars';
                    } else {
                        calendarSelectedText.textContent = checkedCount + ' calendar(s) selected';
                    }
                }
            }
        } catch (e) {
            console.warn('Error loading filters from localStorage:', e);
        }
    }

    // ========================================================================
    // SEARCH NAVIGATION
    // ========================================================================

    function initSearchNavigation() {
        const searchInput = document.getElementById('search-input');
        const searchForm = document.getElementById('search-form');
        
        if (!searchInput || !searchForm) return;

        let currentHighlightIndex = -1;
        let hasSubmitted = false;

        // Get all job rows
        function getJobRows() {
            return Array.from(document.querySelectorAll('.job-row'));
        }

        // Highlight a specific row
        function highlightRow(index) {
            const jobRows = getJobRows();
            
            // Remove previous highlights
            jobRows.forEach(function(row) {
                row.classList.remove('bg-blue-100', 'ring-2', 'ring-blue-500');
                row.style.backgroundColor = '';
            });

            if (index >= 0 && index < jobRows.length) {
                const row = jobRows[index];
                row.classList.add('bg-blue-100', 'ring-2', 'ring-blue-500');

                // Scroll the row into view smoothly
                row.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
        }

        // Handle Enter key navigation
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();

                // If search hasn't been submitted yet or input has changed
                if (!hasSubmitted || this.value !== this.getAttribute('data-last-search')) {
                    // Submit the form
                    this.setAttribute('data-last-search', this.value);
                    hasSubmitted = true;
                    currentHighlightIndex = -1;
                    searchForm.submit();
                    return;
                }

                // Otherwise, navigate through results
                const jobRows = getJobRows();
                if (jobRows.length > 0) {
                    currentHighlightIndex = (currentHighlightIndex + 1) % jobRows.length;
                    highlightRow(currentHighlightIndex);
                }
            }
        });

        // Track if search value changes
        searchInput.addEventListener('input', function() {
            hasSubmitted = false;
        });

        // Focus search input on page load if there's a search query
        if (searchInput.value) {
            searchInput.focus();
            searchInput.setAttribute('data-last-search', searchInput.value);
            hasSubmitted = true;
        }
    }

    // ========================================================================
    // ROW CLICK HANDLERS (Event Delegation)
    // ========================================================================

    function initRowClickHandlers() {
        const jobTableContainer = document.getElementById('job-table-container');
        if (!jobTableContainer) return;

        // Use event delegation for clicks
        jobTableContainer.addEventListener('click', function(e) {
            const row = e.target.closest('.job-row');
            if (!row) return;

            // Don't navigate if user clicked on an action link or button
            if (e.target.tagName === 'A' || e.target.closest('a') ||
                e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                return;
            }

            // Get job ID from the row
            const jobId = row.getAttribute('data-job-id');
            if (jobId && window.JobPanel) {
                // Get the job create URL from the config or data attribute
                let jobCreateUrl = '';
                if (window.jobListConfig && window.jobListConfig.jobCreateUrl) {
                    jobCreateUrl = window.jobListConfig.jobCreateUrl;
                } else if (jobTableContainer.getAttribute('data-job-create-url')) {
                    jobCreateUrl = jobTableContainer.getAttribute('data-job-create-url');
                } else if (window.calendarConfig && window.calendarConfig.jobCreateUrl) {
                    jobCreateUrl = window.calendarConfig.jobCreateUrl;
                } else {
                    // Fallback URL
                    jobCreateUrl = '/jobs/new/partial/';
                }
                
                window.JobPanel.setTitle('Edit Job');
                window.JobPanel.load(jobCreateUrl + '?edit=' + jobId);
            }
        });

        // Use event delegation for hover (using mouseover/mouseout since mouseenter doesn't bubble)
        jobTableContainer.addEventListener('mouseover', function(e) {
            const row = e.target.closest('.job-row');
            if (row && !row.classList.contains('bg-blue-100')) {
                row.style.backgroundColor = '#f9fafb';
            }
        });

        jobTableContainer.addEventListener('mouseout', function(e) {
            const row = e.target.closest('.job-row');
            if (row && !row.classList.contains('bg-blue-100')) {
                row.style.backgroundColor = '';
            }
        });
    }

    // ========================================================================
    // ENTRY POINT
    // ========================================================================

    initJobsListPage();

})();
