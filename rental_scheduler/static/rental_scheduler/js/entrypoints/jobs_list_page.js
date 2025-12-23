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
        GTS.storage.setJson('job-list-filters', filters);
    }

    function initLocalStoragePersistence() {
        const filters = GTS.storage.getJson('job-list-filters', null);
        if (!filters) return;

        try {

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
    // ROW CLICK HANDLERS (Event Delegation on document.body for HTMX resilience)
    // ========================================================================

    function initRowClickHandlers() {
        // Use document.body for delegation - survives any HTMX swap of #job-table-container
        // Filter inside handler to only process events within #job-table-container
        
        document.body.addEventListener('click', function(e) {
            // Only handle clicks inside #job-table-container
            var container = e.target.closest('#job-table-container');
            if (!container) return;
            
            // Handle series header row click (grouped search mode)
            var seriesRow = e.target.closest('.series-header-row');
            if (seriesRow) {
                e.preventDefault();
                e.stopPropagation();
                handleSeriesHeaderClick(seriesRow);
                return;
            }

            // Handle "Show more" button for series occurrences
            var showMoreSeriesBtn = e.target.closest('.show-more-series-btn');
            if (showMoreSeriesBtn) {
                e.stopPropagation();
                handleShowMoreSeriesOccurrences(showMoreSeriesBtn);
                return;
            }

            // Note: .expand-occurrences-btn is no longer used - series headers handle expansion now

            var row = e.target.closest('.job-row');
            if (!row) return;

            // Don't navigate if user clicked on an action link or button
            if (e.target.tagName === 'A' || e.target.closest('a') ||
                e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                return;
            }

            // Check if this is a virtual occurrence row
            if (row.getAttribute('data-virtual') === '1') {
                handleVirtualRowClick(row);
                return;
            }

            // Get job ID from the row
            var jobId = row.getAttribute('data-job-id');
            if (jobId && window.JobPanel) {
                // Use config-driven URL from GTS.urls (global, always available)
                window.JobPanel.setTitle('Edit Job');
                window.JobPanel.load(GTS.urls.jobCreatePartial({ edit: jobId }));
            }
        });

        // Keyboard accessibility for series header rows (Enter/Space to expand)
        document.body.addEventListener('keydown', function(e) {
            if (e.key !== 'Enter' && e.key !== ' ') return;
            
            var seriesRow = e.target.closest('.series-header-row');
            if (seriesRow && seriesRow.closest('#job-table-container')) {
                e.preventDefault();
                handleSeriesHeaderClick(seriesRow);
            }
        });

        // Use event delegation for hover on document.body (filter to container)
        document.body.addEventListener('mouseover', function(e) {
            var container = e.target.closest('#job-table-container');
            if (!container) return;
            
            var row = e.target.closest('.job-row');
            if (row && !row.classList.contains('bg-blue-100')) {
                row.style.backgroundColor = '#f9fafb';
            }
        });

        document.body.addEventListener('mouseout', function(e) {
            var container = e.target.closest('#job-table-container');
            if (!container) return;
            
            var row = e.target.closest('.job-row');
            if (row && !row.classList.contains('bg-blue-100')) {
                row.style.backgroundColor = '';
            }
        });
    }

    // ========================================================================
    // HTMX DEDUPE FOR SERIES HEADERS
    // ========================================================================

    /**
     * After HTMX appends new rows (load-more), dedupe series header rows.
     * If a series header already exists in the DOM for the same (parent_id, scope),
     * remove the duplicate that was just appended.
     */
    function initHtmxSeriesHeaderDedupe() {
        document.body.addEventListener('htmx:afterSwap', function(e) {
            // Only care about swaps into #job-table-body or #job-table-container
            var target = e.detail.target;
            if (!target) return;
            if (!target.id || (target.id !== 'job-table-body' && target.id !== 'job-table-container')) {
                // Check if target is inside our container
                if (!target.closest('#job-table-container')) return;
            }

            // Find all series header rows and dedupe
            var allHeaders = document.querySelectorAll('#job-table-container .series-header-row');
            var seen = {};

            allHeaders.forEach(function(header) {
                var seriesId = header.getAttribute('data-series-id');
                var scope = header.getAttribute('data-scope');
                var key = seriesId + '-' + scope;

                if (seen[key]) {
                    // Duplicate - remove the later one (the one just appended)
                    header.remove();
                } else {
                    seen[key] = header;
                }
            });
        });
    }

    // Initialize dedupe listener
    initHtmxSeriesHeaderDedupe();

    // ========================================================================
    // VIRTUAL ROW CLICK HANDLER
    // ========================================================================

    /**
     * Handle click on a virtual occurrence row (materialize + open)
     */
    function handleVirtualRowClick(row) {
        const parentId = row.getAttribute('data-recurrence-parent-id');
        const originalStart = row.getAttribute('data-recurrence-original-start');

        if (!parentId || !originalStart) {
            console.error('Missing parent_id or original_start for virtual row');
            return;
        }

        // Show loading indicator on the row
        row.style.opacity = '0.6';
        row.style.pointerEvents = 'none';

        // Get CSRF token
        var csrfToken = '';
        var csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfEl) {
            csrfToken = csrfEl.value;
        } else {
            // Try cookie
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.startsWith('csrftoken=')) {
                    csrfToken = cookie.substring(10);
                    break;
                }
            }
        }

        fetch(GTS.urls.materializeOccurrence, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                parent_id: parseInt(parentId, 10),
                original_start: originalStart
            })
        })
            .then(function(response) {
                if (!response.ok) {
                    return response.json().then(function(data) {
                        throw new Error(data.error || 'Failed to materialize occurrence');
                    });
                }
                return response.json();
            })
            .then(function(data) {
                var jobId = data.job_id;
                console.log('Materialized occurrence, job ID:', jobId, 'created:', data.created);

                // Open the real job
                if (window.JobWorkspace) {
                    window.JobWorkspace.openJob(jobId, {
                        customerName: 'Job',
                        trailerColor: '',
                        calendarColor: '#3B82F6'
                    });
                } else if (window.JobPanel) {
                    window.JobPanel.setTitle('Edit Job');
                    window.JobPanel.load(GTS.urls.jobCreatePartial({ edit: jobId }));
                }

                // If materialization created a new row, optionally refresh the parent's expanded view
                if (data.created) {
                    // Remove the virtual row since it's now real
                    row.remove();
                }
            })
            .catch(function(error) {
                console.error('Error materializing virtual occurrence:', error);
                if (window.showToast) {
                    window.showToast('Failed to open occurrence: ' + error.message, 'error');
                }
                row.style.opacity = '1';
                row.style.pointerEvents = '';
            });
    }

    // ========================================================================
    // SERIES HEADER EXPAND/COLLAPSE (Grouped Search Mode)
    // Uses shared GTS.seriesOccurrencesUI module
    // ========================================================================

    /**
     * Get current search query from the page (URL or input)
     */
    function getSeriesSearchQuery() {
        var urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('search') || '';
    }

    /**
     * Handle click on a series header row to expand/collapse occurrences
     */
    function handleSeriesHeaderClick(headerRow) {
        GTS.seriesOccurrencesUI.toggle(headerRow, {
            count: 5,
            getSearchQuery: getSeriesSearchQuery,
            rootEl: document
        });
    }

    /**
     * Handle "Show more" button click for series occurrences
     */
    function handleShowMoreSeriesOccurrences(btn) {
        GTS.seriesOccurrencesUI.showMore(btn, {
            count: 5,
            rootEl: document
        });
    }

    // ========================================================================
    // ENTRY POINT
    // ========================================================================

    initJobsListPage();

})();
